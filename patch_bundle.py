import re

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original bundle length:", len(code))

# 1. Patch RecipeCostingView: xr.map dynamic live cost calculation
target_xr_map = 'xr.map(Ze=>{const dn=Number(Ze.costPerPortion??Ze.cost_per_portion??Ze.totalCost??Ze.total_cost??0),na=Number(Ze.sellingPriceCUP??Ze.selling_price??Ze.sellingPrice??0),ma=Number(Ze.foodCostPct??Ze.food_cost_pct??(na>0?dn/na*100:0)),jn=Number(Ze.grossProfitPerUnit??na-dn),ja=H8(ma);'
assert target_xr_map in code, "target_xr_map not found"

replacement_xr_map = 'xr.map(Ze=>{let liveRawCost=0;if(Array.isArray(Ze.ingredients)&&Ze.ingredients.length>0){Ze.ingredients.forEach(ing=>{const ingId=String(ing.ingredientId||ing.inventoryId||ing.id||""),ingName=String(ing.ingredientName||ing.name||"").toLowerCase().trim(),match=z.find(Ea=>Ea.id===ingId||Ea.id===`inv_${ingId}`||Ea.id===`ing_${ingId}`||Ea.rawItem?.id===ingId||(Ea.name||"").toLowerCase().trim()===ingName),unitC=Number(match?match.unitCost:(ing.costPerUnit||ing.cost_per_unit||ing.unitCost||0));liveRawCost+=Number(ing.quantity||0)*unitC})};const yieldCount=Number(Ze.portionYield||Ze.portions||1)||1,liveCostPerPortion=liveRawCost>0?+(liveRawCost/yieldCount).toFixed(4):Number(Ze.costPerPortion??Ze.cost_per_portion??Ze.totalCost??Ze.total_cost??0),dn=liveCostPerPortion,na=Number(Ze.sellingPriceCUP??Ze.selling_price??Ze.sellingPrice??0),ma=Number(na>0?+((dn/na)*100).toFixed(1):(Ze.foodCostPct??Ze.food_cost_pct??0)),jn=Number(+(na-dn).toFixed(2)),ja=H8(ma);'

code = code.replace(target_xr_map, replacement_xr_map, 1)
print("Patch 1 (RecipeCostingView xr.map): OK")

# 2. Patch RecipeCostingView: ingredient mapping in ct
target_ct_map = 'const ma=(Ze.ingredients||[]).map((jn,ja)=>{const mr=String(jn.ingredientId||jn.inventoryId||jn.id||""),Mr=String(jn.ingredientName||jn.name||""),za=!!jn.isPackagingOrInsumo||Mr.toLowerCase().includes("vaso")||Mr.toLowerCase().includes("tapa")||Mr.toLowerCase().includes("empaque")||Mr.toLowerCase().includes("caja")||Mr.toLowerCase().includes("servilleta"),Ra=z.find(Ea=>Ea.id===mr||Ea.name.toLowerCase().trim()===Mr.toLowerCase().trim());let Rr=Number(jn.costPerUnit||jn.cost_per_unit||jn.unitCost||0);const io=Number(jn.effectiveCost||jn.subtotal||0);Rr<=0&&Number(jn.quantity||0)>0&&io>0&&(Rr=io/Number(jn.quantity)),Rr<=0&&Ra&&Ra.unitCost>0&&(Rr=Ra.unitCost);const Za=io>0?io:+(Number(jn.quantity||0)*Rr).toFixed(4);'
assert target_ct_map in code, "target_ct_map not found"

replacement_ct_map = 'const ma=(Ze.ingredients||[]).map((jn,ja)=>{const mr=String(jn.ingredientId||jn.inventoryId||jn.id||""),Mr=String(jn.ingredientName||jn.name||""),za=!!jn.isPackagingOrInsumo||Mr.toLowerCase().includes("vaso")||Mr.toLowerCase().includes("tapa")||Mr.toLowerCase().includes("empaque")||Mr.toLowerCase().includes("caja")||Mr.toLowerCase().includes("servilleta"),Ra=z.find(Ea=>Ea.id===mr||Ea.id===`inv_${mr}`||Ea.id===`ing_${mr}`||Ea.rawItem?.id===mr||(Ea.name||"").toLowerCase().trim()===Mr.toLowerCase().trim());let Rr=Ra&&Number(Ra.unitCost)>0?Number(Ra.unitCost):Number(jn.costPerUnit||jn.cost_per_unit||jn.unitCost||0);const Za=+(Number(jn.quantity||0)*Rr).toFixed(4);'

code = code.replace(target_ct_map, replacement_ct_map, 1)
print("Patch 2 (RecipeCostingView ct modal): OK")

# 3. Patch PosView: freeze live cost onto sold items and totalCostCUP
target_pos_cost = 'let is=0,Zr=!1;nn.forEach(x=>{if(x.isPresentation)Zr=!0,is+=(x.unitCost||0)*x.quantity;else{const v=e.find(w=>w.id===x.recipeId);if(v)is+=(v.totalCost||0)*x.quantity;else{const w=t.find(D=>D.id===x.recipeId);w&&(is+=(w.costPerUnit||0)*x.quantity)}}});'
assert target_pos_cost in code, "target_pos_cost not found"

replacement_pos_cost = 'let is=0,Zr=!1;nn.forEach(x=>{if(x.isPresentation){Zr=!0;const unitC=Number(x.unitCost||x.cost||0);x.cost=unitC;x.unitCost=unitC;is+=unitC*x.quantity;}else{const v=e.find(w=>w.id===x.recipeId||w.id===x.id);if(v){let liveRecipeCost=0;if(Array.isArray(v.ingredients)&&v.ingredients.length>0){v.ingredients.forEach(ing=>{const ingId=String(ing.ingredientId||ing.inventoryId||ing.id||""),ingName=String(ing.ingredientName||ing.name||"").toLowerCase().trim(),invItem=t.find(D=>D.id===ingId||D.id===`inv-${ingId}`||D.id===`inv_${ingId}`||String(D.name||"").toLowerCase().trim()===ingName),unitC=Number(invItem?(invItem.costPerUnit||invItem.cost_per_unit||invItem.costCUP||0):(ing.costPerUnit||ing.cost_per_unit||0));liveRecipeCost+=Number(ing.quantity||0)*unitC;});}const pYield=Number(v.portionYield||v.portions||1)||1,liveUnitCost=liveRecipeCost>0?+(liveRecipeCost/pYield).toFixed(4):Number(v.costPerPortion??v.cost_per_portion??v.totalCost??v.total_cost??0);x.cost=liveUnitCost;x.unitCost=liveUnitCost;is+=liveUnitCost*x.quantity;}else{const w=t.find(D=>D.id===x.recipeId||D.id===x.id);const unitC=Number(w?(w.costPerUnit||w.cost_per_unit||w.costCUP||0):(x.costPerUnit||x.unitCost||x.cost||0));x.cost=unitC;x.unitCost=unitC;is+=unitC*x.quantity;}}});'

code = code.replace(target_pos_cost, replacement_pos_cost, 1)
print("Patch 3 (PosView live cost freeze): OK")

# 4. Patch FinancialStatementsView (aDe): sum real recorded item costs instead of flat 28%
target_ade_flat = 'const he=I*.28;let ee=0,ne=0,G=0,W=0,q=0,xe=0;if(f)ee=$>0?$:h*.28,ne=ae>0?ae:ee*.38,G=ge>0?ge:ee*.22,W=oe>0?oe:ee*.25,q=Ee>0?Ee:ee*.1,xe=Math.max(0,ee-ne-G-W-q);else{const yt=m.totalCOGS||m.totalRevenue*.299;ee=yt+he,ne=(m.coffeeCost||yt*.24)+he*.35,G=(m.dairyCost||yt*.2)+he*.2,W=(m.foodCost||yt*.41)+he*.3,q=(m.packagingCost||yt*.1)+he*.1,xe=Math.max(0,ee-ne-G-W-q)}'
assert target_ade_flat in code, "target_ade_flat not found"

replacement_ade_flat = 'let realSalesCOGS=0;t.forEach(yt=>{if(!j.has(yt.id)){if(yt.totalCostCUP&&Number(yt.totalCostCUP)>0){realSalesCOGS+=Number(yt.totalCostCUP);}else if(Array.isArray(yt.itemsList)&&yt.itemsList.length>0){yt.itemsList.forEach(it=>{realSalesCOGS+=Number(it.cost||it.unitCost||0)*Number(it.quantity||1);});}}});const he=realSalesCOGS>0?realSalesCOGS:(I*.28);let ee=0,ne=0,G=0,W=0,q=0,xe=0;if(f){let allSalesCOGS=0;t.forEach(yt=>{if(yt.totalCostCUP&&Number(yt.totalCostCUP)>0){allSalesCOGS+=Number(yt.totalCostCUP);}else if(Array.isArray(yt.itemsList)&&yt.itemsList.length>0){yt.itemsList.forEach(it=>{allSalesCOGS+=Number(it.cost||it.unitCost||0)*Number(it.quantity||1);});}});ee=allSalesCOGS>0?allSalesCOGS:($>0?$:h*.28);ne=ae>0?ae:ee*.38;G=ge>0?ge:ee*.22;W=oe>0?oe:ee*.25;q=Ee>0?Ee:ee*.1;xe=Math.max(0,ee-ne-G-W-q);}else{const yt=m.totalCOGS||m.totalRevenue*.299;ee=yt+he;ne=(m.coffeeCost||yt*.24)+he*.35;G=(m.dairyCost||yt*.2)+he*.2;W=(m.foodCost||yt*.41)+he*.3;q=(m.packagingCost||yt*.1)+he*.1;xe=Math.max(0,ee-ne-G-W-q);}'

code = code.replace(target_ade_flat, replacement_ade_flat, 1)
print("Patch 4 (FinancialStatementsView real COGS): OK")

# 5. Patch DynamicPurchaseModal (V4e): auto-update inventory costs with weighted average / last price on purchase
target_purch_save = 'const pe={id:`purch-${Date.now()}`,purchaseNumber:`COM-${Date.now().toString().slice(-6)}`,date:F,supplierName:P.trim()||(g?"Proveedor Fiscal":"Compra en Efectivo / Plaza Local"),hasInvoice:g,invoiceNumber:g?V:void 0,documentType:k,categoryType:I,items:ve.filter(fe=>fe.name.trim().length>0),subtotal:Ke,taxAmount:et,totalAmount:H,shippingFreightCost:ce,destinationWarehouseId:Ee,branchId:Ee,paymentMethod:X,paymentStatus:J,status:G,approvedAt:G==="aprobada"?new Date().toISOString():void 0,dueDate:J==="Pendiente"?B||F:void 0,registeredBy:"Administración",notes:ee};u(pe),t()'
assert target_purch_save in code, "target_purch_save not found"

replacement_purch_save = 'const pe={id:`purch-${Date.now()}`,purchaseNumber:`COM-${Date.now().toString().slice(-6)}`,date:F,supplierName:P.trim()||(g?"Proveedor Fiscal":"Compra en Efectivo / Plaza Local"),hasInvoice:g,invoiceNumber:g?V:void 0,documentType:k,categoryType:I,items:ve.filter(fe=>fe.name.trim().length>0),subtotal:Ke,taxAmount:et,totalAmount:H,shippingFreightCost:ce,destinationWarehouseId:Ee,branchId:Ee,paymentMethod:X,paymentStatus:J,status:G,approvedAt:G==="aprobada"?new Date().toISOString():void 0,dueDate:J==="Pendiente"?B||F:void 0,registeredBy:"Administración",notes:ee};if(Array.isArray(a)&&pe.items.length>0){pe.items.forEach(purchItem=>{const targetInv=a.find(inv=>inv.id===purchItem.matchedInventoryId||inv.id===purchItem.id||(inv.name||"").toLowerCase().trim()===(purchItem.name||"").toLowerCase().trim());if(targetInv){const oldStock=Math.max(0,Number(targetInv.currentStock||targetInv.current_stock||0)),oldCost=Number(targetInv.costPerUnit||targetInv.cost_per_unit||targetInv.costCUP||0),purchQty=Number(purchItem.quantity||0),purchCost=Number(purchItem.unitCost||0);let newCost=purchCost;if(purchItem.updateMethod!=="ultimo_costo"&&(oldStock+purchQty)>0&&oldCost>0){newCost=+(((oldStock*oldCost)+(purchQty*purchCost))/(oldStock+purchQty)).toFixed(4);}targetInv.costPerUnit=newCost;targetInv.cost_per_unit=newCost;targetInv.costCUP=newCost;targetInv.currentStock=+(oldStock+purchQty).toFixed(2);targetInv.current_stock=targetInv.currentStock;}});try{localStorage.setItem("bistro_inventory",JSON.stringify(a));window.dispatchEvent(new CustomEvent("bistro_inventory_updated",{detail:a}));}catch(err){console.warn("[DynamicPurchaseModal] Error updating local inventory:",err);}}u(pe),t()'

code = code.replace(target_purch_save, replacement_purch_save, 1)
print("Patch 5 (DynamicPurchaseModal inventory auto-cost update): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All 5 patches applied successfully to assets/index-DCC2oYkl.js!")
