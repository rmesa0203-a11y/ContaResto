-- ==============================================================================
-- BistroConta: Procedimiento Almacenado de Registro de Lotes de Producción
-- Soporta Escandallos Multinivel (Materias Primas + Sub-elaboraciones anidadas)
-- Compatible con esquema real JSONB de public.recipes.ingredients
-- ==============================================================================

CREATE OR REPLACE FUNCTION public.register_batch_production(
  p_branch_id TEXT,
  p_product_id TEXT,
  p_quantity_produced NUMERIC,
  p_user_id UUID DEFAULT '00000000-0000-0000-0000-000000000000',
  p_company_id TEXT DEFAULT 'biz-main'
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_recipe_row RECORD;
  v_ing JSONB;
  v_raw_ing_id TEXT;
  v_clean_ing_id TEXT;
  v_ing_name TEXT;
  v_ing_type TEXT;
  v_unit_qty NUMERIC;
  v_portion_yield NUMERIC := 1;
  v_needed_stock NUMERIC;
  v_current_stock NUMERIC;
  v_inv_record RECORD;
BEGIN
  -- Obtener la receta principal
  SELECT * INTO v_recipe_row
  FROM public.recipes
  WHERE id = p_product_id
  LIMIT 1;

  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'success', false,
      'error', 'No se encontró el escandallo / receta con ID: ' || p_product_id
    );
  END IF;

  -- Extraer rendimiento base si existe en raw_data
  IF v_recipe_row.raw_data IS NOT NULL AND (v_recipe_row.raw_data->>'portionYield') IS NOT NULL THEN
    v_portion_yield := GREATEST(COALESCE((v_recipe_row.raw_data->>'portionYield')::NUMERIC, 1), 0.0001);
  END IF;

  -- 1. Validar existencias de todos los insumos y sub-elaboraciones según el escandallo JSONB
  IF v_recipe_row.ingredients IS NOT NULL AND jsonb_typeof(v_recipe_row.ingredients) = 'array' THEN
    FOR v_ing IN SELECT * FROM jsonb_array_elements(v_recipe_row.ingredients)
    LOOP
      v_raw_ing_id := COALESCE(v_ing->>'id', v_ing->>'ingredientId', v_ing->>'inventoryId', '');
      v_clean_ing_id := regexp_replace(v_raw_ing_id, '^(inv_|ing_)', '');
      v_ing_name := COALESCE(v_ing->>'name', v_ing->>'ingredientName', 'Insumo');
      v_ing_type := COALESCE(v_ing->>'type', 'raw_material');
      v_unit_qty := ABS(COALESCE((v_ing->>'quantity')::NUMERIC, 0));
      v_needed_stock := ROUND((v_unit_qty * (p_quantity_produced / v_portion_yield))::NUMERIC, 4);

      IF v_needed_stock > 0 AND v_clean_ing_id <> '' THEN
        -- Resolver contra inventory por ID limpio o por nombre
        SELECT id, name, category INTO v_inv_record
        FROM public.inventory
        WHERE id = v_clean_ing_id OR id = v_raw_ing_id OR lower(trim(name)) = lower(trim(v_ing_name))
        LIMIT 1;

        IF FOUND THEN
          v_clean_ing_id := v_inv_record.id;
          v_ing_name := v_inv_record.name;
        END IF;

        SELECT COALESCE(current_stock, 0) INTO v_current_stock
        FROM public.branch_inventory
        WHERE branch_id = p_branch_id AND item_id = v_clean_ing_id
        LIMIT 1;

        v_current_stock := COALESCE(v_current_stock, 0);

        IF v_current_stock < v_needed_stock THEN
          RETURN jsonb_build_object(
            'success', false,
            'error', CASE WHEN v_ing_type = 'elaboration' OR v_inv_record.category = 'Elaboraciones'
                     THEN 'Stock insuficiente de sub-elaboración: '
                     ELSE 'Stock insuficiente de materia prima: ' END ||
                     v_ing_name || ' (Requerido: ' || v_needed_stock || ', Disponible: ' || v_current_stock || ')'
          );
        END IF;
      END IF;
    END LOOP;

    -- 2. Descontar materias primas y sub-elaboraciones en branch_inventory e inventory
    FOR v_ing IN SELECT * FROM jsonb_array_elements(v_recipe_row.ingredients)
    LOOP
      v_raw_ing_id := COALESCE(v_ing->>'id', v_ing->>'ingredientId', v_ing->>'inventoryId', '');
      v_clean_ing_id := regexp_replace(v_raw_ing_id, '^(inv_|ing_)', '');
      v_ing_name := COALESCE(v_ing->>'name', v_ing->>'ingredientName', 'Insumo');
      v_unit_qty := ABS(COALESCE((v_ing->>'quantity')::NUMERIC, 0));
      v_needed_stock := ROUND((v_unit_qty * (p_quantity_produced / v_portion_yield))::NUMERIC, 4);

      IF v_needed_stock > 0 AND v_clean_ing_id <> '' THEN
        SELECT id, name INTO v_inv_record
        FROM public.inventory
        WHERE id = v_clean_ing_id OR id = v_raw_ing_id OR lower(trim(name)) = lower(trim(v_ing_name))
        LIMIT 1;

        IF FOUND THEN
          v_clean_ing_id := v_inv_record.id;
        END IF;

        UPDATE public.branch_inventory
        SET
          current_stock = GREATEST(0, current_stock - v_needed_stock),
          updated_at = timezone('utc'::text, now())
        WHERE branch_id = p_branch_id AND item_id = v_clean_ing_id;

        UPDATE public.inventory
        SET
          current_stock = GREATEST(0, COALESCE(current_stock, 0) - v_needed_stock),
          updated_at = timezone('utc'::text, now())
        WHERE id = v_clean_ing_id;
      END IF;
    END LOOP;
  END IF;

  -- 3. Asegurar que exista el producto elaborado en public.inventory con categoría 'Elaboraciones'
  INSERT INTO public.inventory (
    id, tenant_id, company_id, name, category, product_type, unit,
    cost_cup, selling_price_cup, current_stock, is_produced_internally, recipe_id, active, updated_at
  ) VALUES (
    p_product_id,
    p_company_id,
    p_company_id,
    v_recipe_row.name,
    'Elaboraciones',
    'elaborated',
    'porciones',
    COALESCE(v_recipe_row.cost_per_portion, v_recipe_row.total_cost, 0),
    COALESCE(v_recipe_row.selling_price_cup, v_recipe_row.selling_price, COALESCE(v_recipe_row.cost_per_portion, 0) * 1.5),
    p_quantity_produced,
    true,
    p_product_id,
    true,
    timezone('utc'::text, now())
  )
  ON CONFLICT (id)
  DO UPDATE SET
    category = 'Elaboraciones',
    is_produced_internally = true,
    recipe_id = p_product_id,
    current_stock = COALESCE(public.inventory.current_stock, 0) + EXCLUDED.current_stock,
    updated_at = timezone('utc'::text, now());

  -- 4. Incrementar o insertar el stock del producto elaborado en branch_inventory (sin company_id)
  IF EXISTS (
    SELECT 1 FROM public.branch_inventory WHERE branch_id = p_branch_id AND item_id = p_product_id
  ) THEN
    UPDATE public.branch_inventory
    SET
      current_stock = COALESCE(current_stock, 0) + p_quantity_produced,
      updated_at = timezone('utc'::text, now())
    WHERE branch_id = p_branch_id AND item_id = p_product_id;
  ELSE
    INSERT INTO public.branch_inventory (
      id, branch_id, item_id, tenant_id, current_stock, min_stock, updated_at
    ) VALUES (
      gen_random_uuid(), p_branch_id, p_product_id, p_company_id, p_quantity_produced, 0, timezone('utc'::text, now())
    );
  END IF;

  RETURN jsonb_build_object('success', true, 'produced', p_quantity_produced);
END;
$$;
