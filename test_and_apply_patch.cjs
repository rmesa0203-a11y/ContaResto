const fs = require('fs');
const esbuild = require('esbuild');

// Clean helper block for POS checkout stock deduction
const block = `
;us = (he || t || []).map(it => {
  const rawId = String(it.id || "");
  const cid = rawId.replace(/^(inv_|ing_|rec_)+/, "");
  const bStock = Number(
    branchStockMap[\`\${te}_\${rawId}\`] ??
    branchStockMap[\`\${te}_\${cid}\`] ??
    branchStockMap[rawId] ??
    branchStockMap[cid] ??
    it.branchStock?.[te] ??
    it.current_stock ??
    it.stock ??
    0
  );
  return {
    ...it,
    current_stock: bStock,
    currentStock: bStock,
    stock: bStock,
    branchStock: { ...(it.branchStock || {}), [te]: bStock }
  };
});
let ws = 0;
const zn = [];
const cleanId = x => String(x || "").replace(/^(inv_|ing_|rec_)+/, "").trim();
const Xn = x => String(x || "").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").trim();

const Wr = (k, C) => {
  if (k < 0 || k >= us.length || C <= 0) return;
  const T = us[k];
  const rawId = String(T.id || "");
  const cid = cleanId(rawId);
  const Be = Number(
    branchStockMap[\`\${te}_\${rawId}\`] ??
    branchStockMap[\`\${te}_\${cid}\`] ??
    branchStockMap[rawId] ??
    branchStockMap[cid] ??
    T.branchStock?.[te] ??
    T.current_stock ??
    T.stock ??
    0
  );
  const Ke = Math.max(0, +(Be - C).toFixed(4));
  const lt = { ...(T.branchStock || {}), [te]: Ke };
  const ie = n9e(T.fifoBatches || [], C, te, T.costPerUnit || 0);
  const ke = ie.totalFifoCostCUP || 0;
  ws += ke;
  const Rt = {
    ...T,
    branchStock: lt,
    currentStock: Ke,
    stock: Ke,
    current_stock: Ke,
    fifoBatches: ie.updatedBatches,
    totalValue: +(Ke * (T.costPerUnit || 0)).toFixed(2),
    status: Ke <= (T.minStock || 0) * 0.5 ? "critical" : Ke <= (T.minStock || 0) ? "low" : "optimal"
  };
  us[k] = Rt;
  zn.push({ id: T.id, newStock: Ke, newBranchStock: Ke, qtyDeducted: C, branchId: te, item: Rt });
  branchStockMap[\`\${te}_\${rawId}\`] = Ke;
  branchStockMap[\`\${te}_\${cid}\`] = Ke;
  branchStockMap[rawId] = Ke;
  branchStockMap[cid] = Ke;
  dN({
    id: \`kardex-pos-\${Date.now()}-\${Math.random().toString(36).slice(2, 6)}\`,
    timestamp: Date.now(),
    date: new Date().toISOString().split("T")[0],
    branchId: te,
    originType: "venta_pos",
    referenceDocumentId: va,
    referenceDocumentNumber: Wt?.tabNumber || va,
    productId: T.id,
    productName: T.name,
    movementType: "salida",
    quantity: C,
    unit: T.unit,
    unitCostFifo: C > 0 ? +(ke / C).toFixed(4) : T.costPerUnit,
    totalValue: +ke.toFixed(2),
    stockBefore: Be,
    stockAfter: Ke,
    operatorName: P.name,
    details: \`Venta POS: \${ie.consumedBatches?.length || 0} lote(s) consumido(s) FIFO\`
  });
};

const deductIngredientsFromList = (ingredients, multiplier) => {
  if (!Array.isArray(ingredients) || ingredients.length === 0 || multiplier <= 0) return;
  ingredients.forEach(Ke => {
    const rawIngId = String(Ke.ingredientId || Ke.inventoryId || Ke.id || "");
    const cid = cleanId(rawIngId);
    const ingName = Xn(Ke.ingredientName || Ke.name || "");
    const Rt = us.findIndex(it => {
      const rawItemId = String(it.id || "");
      const itemCid = cleanId(rawItemId);
      if (rawIngId && (rawItemId === rawIngId || itemCid === cid || it.recipe_id === rawIngId || cleanId(it.recipe_id) === cid)) return true;
      const itemName = Xn(it.name);
      return itemName === ingName || (ingName.length >= 3 && (itemName.includes(ingName) || ingName.includes(itemName)));
    });
    if (Rt >= 0) {
      const matchedItem = us[Rt];
      let unitFactor = 1;
      const ingUnit = (Ke.unit || "").toLowerCase();
      const itemUnit = (matchedItem.unit || "").toLowerCase();
      if ((ingUnit === "g" || ingUnit === "ml") && (itemUnit === "kg" || itemUnit === "l" || itemUnit === "litro" || itemUnit === "litros")) {
        unitFactor = 1 / 1000;
      } else if ((ingUnit === "kg" || ingUnit === "l" || ingUnit === "litro" || ingUnit === "litros") && (itemUnit === "g" || itemUnit === "ml")) {
        unitFactor = 1000;
      }
      const deductAmt = +(Number(Ke.quantity || 1) * multiplier * unitFactor).toFixed(4);
      Wr(Rt, deductAmt);
    }
  });
};

Da.forEach(k => {
  const C = Xn(k.name);
  if (k.isPresentation && k.presentationComponents && k.presentationComponents.length > 0) {
    k.presentationComponents.forEach(ke => {
      const Be = ke.quantity * k.quantity;
      const Ke = Xn(ke.itemName);
      if (ke.itemType === "inventory") {
        const lt = us.findIndex(Et => (ke.itemId && Et.id === ke.itemId) || Xn(Et.name) === Ke || (Ke.length >= 3 && (Xn(Et.name).includes(Ke) || Ke.includes(Xn(Et.name)))));
        if (lt >= 0) Wr(lt, Be);
      } else if (ke.itemType === "recipe") {
        const lt = (e || []).find(Et => (ke.itemId && Et.id === ke.itemId) || Xn(Et.name) === Ke);
        if (lt) {
          const Et = us.findIndex($t => ($t.id === lt.id || cleanId($t.id) === cleanId(lt.id) || Xn($t.name) === Xn(lt.name)) && $t.productType === "elaborated");
          let Rt = Be;
          if (Et >= 0) {
            const $t = Number(branchStockMap[\`\${te}_\${us[Et].id}\`] ?? branchStockMap[\`\${te}_\${cleanId(us[Et].id)}\`] ?? us[Et].branchStock?.[te] ?? 0);
            if ($t > 0) {
              const Yt = Math.min(Be, $t);
              Wr(Et, Yt);
              Rt = +(Be - Yt).toFixed(4);
            }
          }
          if (Rt > 0 && lt.ingredients) {
            deductIngredientsFromList(lt.ingredients, Rt);
          }
        }
      }
    });
    return;
  }

  // Look for matching recipe in e
  const T = (e || []).find(ke =>
    (k.recipeId && ke.id === k.recipeId) ||
    (k.id && ke.id === k.id) ||
    (k.id && cleanId(ke.id) === cleanId(k.id)) ||
    (k.recipeId && cleanId(ke.id) === cleanId(k.recipeId)) ||
    Xn(ke.name) === C
  );

  // Look for matching finished item in inventory us
  const X = us.findIndex(ke =>
    (T && (ke.recipe_id === T.id || ke.id === T.id || cleanId(ke.id) === cleanId(T.id) || cleanId(ke.recipe_id) === cleanId(T.id))) ||
    (k.recipeId && (ke.id === k.recipeId || cleanId(ke.id) === cleanId(k.recipeId) || ke.recipe_id === k.recipeId || cleanId(ke.recipe_id) === cleanId(k.recipeId))) ||
    (k.id && (ke.id === k.id || cleanId(ke.id) === cleanId(k.id))) ||
    (ke.is_produced_internally && (Xn(ke.name) === C || (T && Xn(ke.name) === Xn(T.name)))) ||
    Xn(ke.name) === C
  );

  let remainingQty = Number(k.quantity || 1);

  // If item has finished stock in this branch, deduct available finished stock first
  if (X >= 0) {
    const rawId = String(us[X].id || "");
    const cid = cleanId(rawId);
    const finishedStock = Number(
      branchStockMap[\`\${te}_\${rawId}\`] ??
      branchStockMap[\`\${te}_\${cid}\`] ??
      branchStockMap[rawId] ??
      branchStockMap[cid] ??
      us[X].branchStock?.[te] ??
      us[X].current_stock ??
      us[X].stock ??
      0
    );
    if (finishedStock > 0) {
      const deductFromFinished = Math.min(remainingQty, finishedStock);
      Wr(X, deductFromFinished);
      remainingQty = +(remainingQty - deductFromFinished).toFixed(4);
    }
  }

  // If remaining quantity > 0 and recipe or item has ingredients, deduct each ingredient
  const ingredientsList = (T && Array.isArray(T.ingredients) && T.ingredients.length > 0) ? T.ingredients : (Array.isArray(k.ingredients) && k.ingredients.length > 0 ? k.ingredients : null);

  if (remainingQty > 0 && ingredientsList && !k.isPresentation && k.category !== "Sellados / Enlatados") {
    deductIngredientsFromList(ingredientsList, remainingQty);
    return;
  }

  // Non-elaborated direct inventory items
  if (remainingQty > 0) {
    const ie = X >= 0 ? X : us.findIndex(ke =>
      (k.recipeId && ke.id === k.recipeId) ||
      (k.id && ke.id === k.id) ||
      (k.itemId && ke.id === k.itemId) ||
      (k.sku && ke.sku && Xn(ke.sku) === Xn(k.sku)) ||
      Xn(ke.name) === C ||
      (C.length >= 3 && (Xn(ke.name).includes(C) || C.includes(Xn(ke.name))))
    );
    if (ie >= 0) {
      Wr(ie, remainingQty);
    }
  }
});

if (ws > 0) {
  ts.costoVentaFifoReal = +ws.toFixed(2);
  ts.totalCostCUP = +ws.toFixed(2);
  ts.grossProfitCUP = +(qs - ws).toFixed(2);
  ts.grossProfitMarginPct = qs > 0 ? +(((qs - ws) / qs) * 100).toFixed(1) : 0;
}

const Fe = sn || (Nt && qt);
if (Fe) {
  x(Zr);
  Os.enqueue("kitchen_order", Zr, te);
  if (Wt?.kitchenOrderIds && Wt.kitchenOrderIds.length > 0) {
    Wt.kitchenOrderIds.forEach(k => {
      if (k !== ea) {
        const C = h.find(T => T.id === k);
        if (C) {
          const T = {
            ...C,
            isPaid: true,
            status: Nt ? C.status : C.status === "lista" ? "entregada" : C.status,
            completedAt: !Nt && C.status === "lista" ? C.completedAt || fa : C.completedAt,
            updatedAt: new Date().toISOString()
          };
          x(T);
          Os.enqueue("kitchen_order", T, te);
        }
      }
    });
  }
}

N(ts);
V(us);
window.__BISTRO_OFFLINE_SYNC__?.enqueueSale(ts, te, ye?.tenant_id, zn);
if (typeof window !== "undefined") {
  window.dispatchEvent(new CustomEvent("bistro_sale_completed", { detail: ts }));
  window.dispatchEvent(new CustomEvent("bistro_elaboration_sale", { detail: ts }));
}

const m = typeof ya === "function" && ya() ? ka() : null;
const v = Da.map(k => ({ item_id: k.recipeId, quantity: Number(k.quantity) })).filter(k => k.item_id && k.quantity > 0);
if (m && v.length > 0) {
  try {
    const { data: k, error: C } = await m.rpc("process_sale_stock_deduction", {
      p_tenant_id: ye?.tenant_id || "biz-main",
      p_branch_id: te,
      p_items: v
    });
    if (C || !k?.success) {
      console.warn("[PosView] process_sale_stock_deduction notice:", C || k?.error);
    }
  } catch (k) {
    console.warn("[PosView] process_sale_stock_deduction error:", k);
  }
}

zn.forEach(({ id: k, newStock: C, newBranchStock: T, branchId: X, item: ie }) => {
  aa.updateStockOnSale(k, C, ie, X, T).catch(ke => {
    console.warn(\`[PosView] Error en mutación remota de stock para \${k}:\`, ke);
  });
});

if (m && zn.length > 0) {
  const k = ye?.tenant_id || aa.tenantId || "biz-main";
  const C = new Date().toISOString();
  for (const T of zn) {
    try {
      const { data: X } = await m.from("branch_inventory").select("id").eq("branch_id", T.branchId).eq("item_id", T.id).maybeSingle();
      if (X?.id) {
        await m.from("branch_inventory").update({ current_stock: T.newBranchStock, updated_at: C }).eq("id", X.id);
      } else {
        await m.from("branch_inventory").insert({ tenant_id: k, branch_id: T.branchId, item_id: T.id, current_stock: T.newBranchStock, updated_at: C });
      }
    } catch (X) {
      console.warn("[PosView] Direct branch_inventory update notice:", X);
    }
  }
}

if (window.__BISTRO_LOCAL_STORE__) {
  try {
    const k = window.__BISTRO_LOCAL_STORE__.getLocalInventory(te);
    if (Array.isArray(k) && k.length > 0) {
      zn.forEach(C => {
        const T = k.find(X => X.id === C.id || X.item_id === C.id);
        if (T) {
          T.current_stock = C.newBranchStock;
          T.stock = C.newBranchStock;
        }
      });
      window.__BISTRO_LOCAL_STORE__.saveLocalInventory(te, k);
    }
  } catch {}
}

if (zn.length > 0) {
  const k = {};
  zn.forEach(C => {
    const rawId = String(C.id);
    const cid = cleanId(rawId);
    k[\`\${C.branchId}_\${rawId}\`] = C.newBranchStock;
    k[\`\${C.branchId}_\${cid}\`] = C.newBranchStock;
    k[rawId] = C.newBranchStock;
    k[cid] = C.newBranchStock;
  });
  setBranchStockMap(prev => ({ ...prev, ...k }));
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("bistro_branch_stock_updated", { detail: k }));
    window.dispatchEvent(new CustomEvent("bistro_catalog_updated", { detail: { branchId: te, count: us.length } }));
  }
}
`;

try {
  esbuild.transformSync("async function test() {\n" + block + "\n}", { loader: "js" });
  console.log("ESBUILD_BLOCK_VALID_SUCCESS!");
} catch (e) {
  console.error("ESBUILD_BLOCK_ERROR:", e.message);
  process.exit(1);
}

let code = fs.readFileSync('assets/index-DCC2oYkl.js', 'utf8');
const startToken = ',sentToKitchen:sn,kitchenOrderId:sn?ea:void 0}';
const endToken = 'Os.enqueue("sale",ts,te),Os.enqueue("inventory_update",us,te);';

const idxStartAfter = code.indexOf(startToken);
if (idxStartAfter === -1) {
  console.error("startToken not found!");
  process.exit(1);
}
const idxStart = idxStartAfter + startToken.length;
const idxEnd = code.indexOf(endToken, idxStart);
if (idxEnd === -1) {
  console.error("endToken not found!");
  process.exit(1);
}

console.log("Replacing from", idxStart, "to", idxEnd);
code = code.slice(0, idxStart) + block.trim() + ";" + code.slice(idxEnd);

try {
  esbuild.transformSync(code, { loader: "js" });
  console.log("ESBUILD_WHOLE_FILE_VALID_SUCCESS!");
} catch (e) {
  console.error("ESBUILD_WHOLE_FILE_ERROR:", e.message);
  process.exit(1);
}

fs.writeFileSync('assets/index-DCC2oYkl.js', code, 'utf8');
console.log("SUCCESSFULLY_UPDATED_AND_VERIFIED!");
