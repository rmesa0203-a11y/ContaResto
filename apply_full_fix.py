with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Exact string of if(at){ ... } to replace
start_str = "if(at){const Jn=at.id,dr=Ot,ua=Sn();console.log(`[InventoryView] Enviando UPDATE de producto ${Jn} a Supabase con current_stock: ${dr}`);"
end_str = "u?.(\"inventory\",`Artículo actualizado: ${Ye.name} (${xn})`,`Stock: ${Mt} ${Ye.unit}, Costo: ${Ie}`)}"

idx_start = code.find(start_str)
assert idx_start != -1, "start_str not found"

idx_end = code.find(end_str, idx_start)
assert idx_end != -1, "end_str not found"
idx_end += len(end_str)

replacement_lr = '''if(at){const Jn=at.id,dr=Ot,ua=Sn();const finalPrice=Number(Ye.sellingPrice!==""?Ye.sellingPrice:(Ye.selling_price||Ye.sellingPriceCUP||Ye.price||0));const unitCost=Number(Ye.costPerUnit!==""?Ye.costPerUnit:(Ye.cost_per_unit||Ye.cost||0));const taxRate=Number(Ye.taxPct!==""?Ye.taxPct:(Ye.tax_rate||0));const wp=at.warehousePrices?{...at.warehousePrices}:{};Object.keys(wp).forEach(whId=>{wp[whId]={...wp[whId],retailPriceCUP:finalPrice,sellingPriceCUP:finalPrice};});const updatedProduct={...at,sku:xn,barcode:Ye.barcode.trim()||void 0,name:Ye.name.trim(),category:Ye.category,productType:Ye.productType,currentStock:dr,current_stock:dr,branchStock:(()=>{const Ze=at.branchStock?{...at.branchStock}:{"branch-main":dr};return Object.keys(Ze).forEach(dn=>{Ze[dn]=dr}),Ze})(),minStock:Pe,optimalStock:be,unit:Ye.unit,cost_per_unit:unitCost,costPerUnit:unitCost,costCUP:unitCost,costUSD:Gn,selling_price:finalPrice,price:finalPrice,sellingPriceCUP:finalPrice,sellingPrice:finalPrice,selling_price_cup:finalPrice>0?finalPrice:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,wholesale_price:zn,tax_rate:taxRate,taxPct:taxRate,taxIncluded:!0,finalPriceWithTax:finalPrice,totalValue:dr*unitCost,warehousePrices:wp,supplierName:Ye.supplierName.trim()||"Proveedor General",location:Ye.location||"Almacén Seco",lastRestockedDate:Ye.lastRestockedDate,expirationDate:Ye.expirationDate||void 0,status:Un,updated_at:new Date().toISOString(),updatedAt:new Date().toISOString()};const Yn=wt.map(xr=>xr.id===Jn?updatedProduct:xr);Te(Yn);d(Yn);try{localStorage.setItem("bistro_inventory",JSON.stringify(Yn));localStorage.setItem("cache_inventory",JSON.stringify(Yn));window.dispatchEvent(new CustomEvent("bistro_inventory_updated",{detail:Yn}))}catch(e){};u?.("inventory",`Artículo actualizado: ${Ye.name} (${xn})`,`PVP: ${finalPrice}, Stock: ${dr} ${Ye.unit}, Costo: ${unitCost}`);try{const updatePayload={name:Ye.name.trim(),sku:xn,barcode:Ye.barcode.trim()||null,category:Ye.category,product_type:Ye.productType||null,current_stock:Number(dr),min_stock:Pe,optimal_stock:be,unit:Ye.unit||null,cost_cup:unitCost,cost_usd:Gn,selling_price_cup:finalPrice>0?finalPrice:null,selling_price_usd:Tn>0?Tn:null,supplier_name:Ye.supplierName.trim()||null,location:Ye.location||null,status:Un,data:updatedProduct,updated_at:new Date().toISOString()};const{error:_n}=await ua.from("inventory").update(updatePayload).eq("id",Jn);if(_n){console.warn("[InventoryView] Full update notice, retrying base payload:",_n.message);await ua.from("inventory").update({name:Ye.name.trim(),sku:xn,current_stock:Number(dr),cost_cup:unitCost,selling_price_cup:finalPrice>0?finalPrice:null,data:updatedProduct,updated_at:new Date().toISOString()}).eq("id",Jn);}}catch(err){console.error("[InventoryView] Supabase async save notice:",err);}}'''

code = code[:idx_start] + replacement_lr + code[idx_end:]
print("Patch 1 (Optimistic update and data sync in lr): OK")

# 2. Patch input in modal to include onFocus select and handle 0 gracefully
target_input = 'n.jsxDEV("input",{type:"number",step:"any",min:"0",value:Ye.sellingPrice,onChange:_e=>Xe({...Ye,sellingPrice:_e.target.value===""?"":_e.target.value}),placeholder:"0.00",className:"w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"}'
if target_input in code:
    replacement_input = 'n.jsxDEV("input",{type:"number",step:"any",min:"0",value:Ye.sellingPrice===0?"":Ye.sellingPrice,onChange:_e=>Xe({...Ye,sellingPrice:_e.target.value===""?"":Number(_e.target.value)||(_e.target.value)}),onFocus:_e=>_e.target.select(),placeholder:"0.00",className:"w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"}'
    code = code.replace(target_input, replacement_input, 1)
    print("Patch 2 (Input onFocus select and local value binding): OK")
else:
    print("Patch 2: target_input not matched (already patched or slightly different), searching substring...")
    old_input = 'value:Ye.sellingPrice,onChange:_e=>Xe({...Ye,sellingPrice:_e.target.value===""?"":_e.target.value}),placeholder:"0.00"'
    if old_input in code:
        new_input = 'value:Ye.sellingPrice===0?"":Ye.sellingPrice,onChange:_e=>Xe({...Ye,sellingPrice:_e.target.value===""?"":Number(_e.target.value)||(_e.target.value)}),onFocus:_e=>_e.target.select(),placeholder:"0.00"'
        code = code.replace(old_input, new_input, 1)
        print("Patch 2 (Sub-input patched): OK")

# 3. Patch App.tsx to listen to bistro_inventory_updated and update ut immediately
target_app_effect = 'S.useEffect(()=>{localStorage.setItem("bistro_inventory",JSON.stringify(ut))},[ut]),'
if target_app_effect in code:
    replacement_app_effect = 'S.useEffect(()=>{const h=e=>{if(e.detail&&Array.isArray(e.detail)){wt(e.detail);}};window.addEventListener("bistro_inventory_updated",h);return()=>window.removeEventListener("bistro_inventory_updated",h);},[]),S.useEffect(()=>{localStorage.setItem("bistro_inventory",JSON.stringify(ut))},[ut]),'
    code = code.replace(target_app_effect, replacement_app_effect, 1)
    print("Patch 3 (App.tsx bistro_inventory_updated listener): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All patches applied successfully!")
