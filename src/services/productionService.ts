/**
 * BistroConta Multi-Level Recipe & Batch Production Service
 *
 * Supports nested elaborations / sub-elaborations (escandallos multinivel),
 * anti-loop circular reference protection, cascading cost calculation,
 * unified recipe + inventory + branch_inventory synchronization,
 * and online/offline batch production transformation.
 */

import { supabase } from '../lib/supabase';
import { offlineSync, getLocalInventory, saveLocalInventory } from './offlineSync';

export interface BatchProductionParams {
  branchId: string;
  productId: string;
  productName?: string;
  quantityProduced: number;
  userId?: string;
  userName?: string;
  companyId?: string;
}

export interface BatchProductionResult {
  success: boolean;
  produced?: number;
  error?: string;
  offline?: boolean;
}

export interface RecipeIngredientRequirement {
  ingredientId: string;
  ingredientName: string;
  isSubElaboration: boolean;
  neededQuantity: number;
  availableStock: number;
}

export function cleanEntityId(rawId?: string): string {
  return String(rawId || '').replace(/^(inv_|ing_)/, '').trim();
}

/**
 * Anti-loop validator: checks if adding `candidateId` as an ingredient of `currentRecipeId`
 * would introduce a direct or indirect circular dependency.
 */
export function wouldCreateRecipeCycle(
  candidateId: string,
  currentRecipeId: string | null | undefined,
  allRecipes: any[],
  visited: Set<string> = new Set()
): boolean {
  if (!currentRecipeId || !candidateId) return false;
  const cleanCandidate = cleanEntityId(candidateId);
  const cleanCurrent = cleanEntityId(currentRecipeId);
  if (cleanCandidate === cleanCurrent) return true;
  if (visited.has(cleanCandidate)) return false;
  visited.add(cleanCandidate);

  const subRecipe = (allRecipes || []).find((r) => cleanEntityId(r.id) === cleanCandidate);
  if (!subRecipe || !Array.isArray(subRecipe.ingredients)) return false;

  for (const ing of subRecipe.ingredients) {
    const ingId = cleanEntityId(ing.id || ing.ingredientId || ing.inventoryId);
    if (ingId === cleanCurrent) return true;
    if (wouldCreateRecipeCycle(ingId, cleanCurrent, allRecipes, visited)) return true;
  }
  return false;
}

/**
 * Calculates exact cascading cost per portion for a recipe, resolving sub-elaboration
 * costs recursively with cycle protection.
 */
export function calculateCascadingRecipeCost(
  recipe: any,
  allRecipes: any[],
  allInventory: any[],
  visited: Set<string> = new Set()
): { totalCost: number; costPerPortion: number } {
  if (!recipe) return { totalCost: 0, costPerPortion: 0 };
  const recId = cleanEntityId(recipe.id);
  if (recId && visited.has(recId)) {
    const fallback = Number(recipe.cost_per_portion ?? recipe.costPerPortion ?? recipe.total_cost ?? 0);
    return { totalCost: fallback, costPerPortion: fallback };
  }
  if (recId) visited.add(recId);

  const yieldPortions = Math.max(0.0001, Number(recipe.portionYield ?? recipe.portions ?? 1) || 1);
  let rawAndSubCost = 0;

  if (Array.isArray(recipe.ingredients)) {
    for (const ing of recipe.ingredients) {
      const ingId = cleanEntityId(ing.id || ing.ingredientId || ing.inventoryId);
      const qty = Math.abs(Number(ing.quantity ?? 0));
      const subRecipe = (allRecipes || []).find((r) => cleanEntityId(r.id) === ingId);
      let unitCost = Number(ing.unit_cost ?? ing.costPerUnit ?? ing.cost_cup ?? ing.cost ?? 0);

      if (subRecipe) {
        const subCalc = calculateCascadingRecipeCost(subRecipe, allRecipes, allInventory, new Set(visited));
        if (subCalc.costPerPortion > 0) unitCost = subCalc.costPerPortion;
      } else {
        const invItem = (allInventory || []).find((it) => cleanEntityId(it.id) === ingId);
        if (invItem) {
          const invCost = Number(invItem.cost_per_portion ?? invItem.cost_cup ?? invItem.costCUP ?? invItem.costPerUnit ?? 0);
          if (invCost > 0) unitCost = invCost;
        }
      }
      rawAndSubCost += qty * unitCost;
    }
  }

  const extraPackaging = Number(recipe.packagingCost ?? 0);
  const totalCost = +(rawAndSubCost + extraPackaging).toFixed(4);
  const costPerPortion = +(totalCost / yieldPortions).toFixed(4);
  return { totalCost, costPerPortion };
}

export class ProductionService {
  /**
   * Synchronizes a saved recipe with `inventory` (category: 'Elaboraciones')
   * and ensures its row exists in `branch_inventory` (without company_id).
   */
  public static async syncRecipeElaborationToInventory(params: {
    recipeId: string;
    recipeName: string;
    recipeUnit?: string;
    costPerPortion: number;
    sellingPrice?: number;
    activeBranchId: string;
    existingStock?: number;
  }): Promise<void> {
    const {
      recipeId,
      recipeName,
      recipeUnit = 'porciones',
      costPerPortion,
      sellingPrice,
      activeBranchId,
      existingStock = 0
    } = params;

    const nowIso = new Date().toISOString();
    const finalPrice = Number(sellingPrice && sellingPrice > 0 ? sellingPrice : +(costPerPortion * 1.5).toFixed(2));

    if (typeof navigator !== 'undefined' && navigator.onLine) {
      await supabase.from('inventory').upsert({
        id: recipeId,
        name: recipeName,
        category: 'Elaboraciones',
        product_type: 'elaborated',
        unit: recipeUnit || 'porciones',
        cost_cup: Number(costPerPortion),
        selling_price_cup: finalPrice,
        current_stock: Number(existingStock),
        is_produced_internally: true,
        recipe_id: recipeId,
        active: true,
        tenant_id: 'biz-main',
        company_id: 'biz-main',
        updated_at: nowIso
      });

      const { data: existingBr } = await supabase
        .from('branch_inventory')
        .select('id')
        .eq('branch_id', activeBranchId)
        .eq('item_id', recipeId)
        .maybeSingle();

      if (!existingBr?.id) {
        await supabase.from('branch_inventory').insert({
          tenant_id: 'biz-main',
          branch_id: activeBranchId,
          item_id: recipeId,
          current_stock: Number(existingStock),
          min_stock: 0,
          updated_at: nowIso
        });
      }
    }
  }

  /**
   * Validates if a branch has sufficient raw ingredients AND sub-elaborations to produce the given quantity.
   */
  public static checkRecipeAvailability(
    branchId: string,
    productId: string,
    quantityProduced: number,
    recipes: any[],
    inventory: any[]
  ): { canProduce: boolean; missingIngredients: RecipeIngredientRequirement[] } {
    const recipe = recipes.find(
      (r) => r.productId === productId || r.id === productId || r.name === productId
    );

    if (!recipe || !Array.isArray(recipe.ingredients) || recipe.ingredients.length === 0) {
      return { canProduce: true, missingIngredients: [] };
    }

    const localCatalog = getLocalInventory(branchId);
    const missing: RecipeIngredientRequirement[] = [];

    for (const item of recipe.ingredients) {
      const ingId = cleanEntityId(item.ingredientId || item.inventoryId || item.id);
      const needed = Math.abs(Number(item.quantity || 0)) * quantityProduced;

      const catItem = localCatalog.find((it) => cleanEntityId(it.id) === ingId || cleanEntityId(it.item_id) === ingId);
      const invItem = inventory.find((it) => cleanEntityId(it.id) === ingId || it.recipe_id === ingId);
      const isSubElab = Boolean(
        item.type === 'elaboration' ||
          item.isElaboration ||
          invItem?.category === 'Elaboraciones' ||
          recipes.some((r) => cleanEntityId(r.id) === ingId)
      );

      const available = Number(catItem?.current_stock ?? catItem?.stock ?? invItem?.branchStock?.[branchId] ?? invItem?.current_stock ?? 0);
      const name = catItem?.name || invItem?.name || item.name || `Insumo ${ingId}`;

      if (available < needed) {
        missing.push({
          ingredientId: ingId,
          ingredientName: name,
          isSubElaboration: isSubElab,
          neededQuantity: needed,
          availableStock: available
        });
      }
    }

    return {
      canProduce: missing.length === 0,
      missingIngredients: missing
    };
  }

  /**
   * Registers a batch production with online Supabase RPC and offline-first fallback.
   */
  public static async registerBatchProduction(
    params: BatchProductionParams,
    recipes: any[] = [],
    inventory: any[] = []
  ): Promise<BatchProductionResult> {
    const {
      branchId,
      productId,
      quantityProduced,
      userId = '00000000-0000-0000-0000-000000000000',
      companyId = 'biz-main'
    } = params;

    const validUserId =
      userId && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(userId)
        ? userId
        : null;

    if (typeof navigator !== 'undefined' && navigator.onLine) {
      try {
        const { data, error } = await supabase.rpc('register_batch_production', {
          p_branch_id: branchId,
          p_recipe_id: productId,
          p_product_id: productId,
          p_quantity_produced: Number(quantityProduced),
          p_user_id: validUserId,
          p_company_id: companyId
        });

        if (error) {
          console.error('Error RPC Supabase:', error);
          return { success: false, error: `Error al registrar lote: ${error.message}` };
        }

        if (data && data.success === false) {
          return { success: false, error: data.error || 'Error en la producción' };
        }

        if (data && data.success) {
          await offlineSync.reconcileDelta(branchId);
          return { success: true, produced: Number(quantityProduced), offline: false };
        }
      } catch (rpcErr: any) {
        console.error('[ProductionService] Supabase RPC notice:', rpcErr);
        return { success: false, error: rpcErr?.message || 'Error al conectar con la base de datos' };
      }
    }

    return this.executeLocalBatchProduction(params, recipes, inventory);
  }

  /**
   * Executes batch production locally: validates raw materials & sub-elaborations,
   * updates local inventory, and queues for background sync.
   */
  public static executeLocalBatchProduction(
    params: BatchProductionParams,
    recipes: any[],
    inventory: any[]
  ): BatchProductionResult {
    const { branchId, productId, quantityProduced, userId, companyId = 'biz-main' } = params;

    const recipe = recipes.find(
      (r) => r.productId === productId || r.id === productId || r.name === productId
    );

    const catalog = getLocalInventory(branchId);
    const deductions: Array<{ id: string; quantity: number }> = [];

    if (recipe && Array.isArray(recipe.ingredients) && recipe.ingredients.length > 0) {
      for (const ing of recipe.ingredients) {
        const ingId = cleanEntityId(ing.ingredientId || ing.inventoryId || ing.id);
        const needed = Math.abs(Number(ing.quantity || 0)) * quantityProduced;
        const target = catalog.find((it) => cleanEntityId(it.id) === ingId || cleanEntityId(it.item_id) === ingId);
        const currentStock = Number(target?.current_stock ?? target?.stock ?? 0);
        const name = target?.name || ing.name || `Insumo ${ingId}`;

        if (currentStock < needed) {
          return {
            success: false,
            error: `Stock insuficiente de insumo/sub-elaboración: ${name} (Requerido: ${needed}, Disponible: ${currentStock})`
          };
        }
      }

      for (const ing of recipe.ingredients) {
        const ingId = cleanEntityId(ing.ingredientId || ing.inventoryId || ing.id);
        const needed = Math.abs(Number(ing.quantity || 0)) * quantityProduced;
        const target = catalog.find((it) => cleanEntityId(it.id) === ingId || cleanEntityId(it.item_id) === ingId);
        if (target) {
          const newStock = Math.max(0, Number(target.current_stock ?? target.stock ?? 0) - needed);
          target.current_stock = newStock;
          target.stock = newStock;
          deductions.push({ id: target.id || ingId, quantity: needed });
        }
      }
    }

    let finishedItem = catalog.find((it) => cleanEntityId(it.id) === productId || cleanEntityId(it.item_id) === productId);
    if (finishedItem) {
      const updatedStock = Number(finishedItem.current_stock ?? finishedItem.stock ?? 0) + quantityProduced;
      finishedItem.current_stock = updatedStock;
      finishedItem.stock = updatedStock;
      finishedItem.category = 'Elaboraciones';
    } else {
      catalog.push({
        id: productId,
        item_id: productId,
        name: params.productName || recipe?.name || `Producto Elaborado ${productId}`,
        category: 'Elaboraciones',
        current_stock: quantityProduced,
        stock: quantityProduced,
        price: Number(recipe?.sellingPriceCUP ?? recipe?.selling_price ?? 0),
        branch_id: branchId
      });
    }

    saveLocalInventory(branchId, catalog);

    offlineSync.enqueueOperation({
      action: 'PRODUCTION_BATCH',
      table: 'branch_inventory',
      payload: {
        branchId,
        productId,
        quantityProduced,
        deductions,
        userId,
        companyId,
        createdAt: new Date().toISOString()
      }
    });

    return {
      success: true,
      produced: quantityProduced,
      offline: true
    };
  }
}
