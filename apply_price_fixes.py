with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# 1. Update yr (when opening edit modal) to read normalized price
target_yr = 'unit:_e.unit||"unidades",costPerUnit:_e.costPerUnit!==void 0&&_e.costPerUnit!==null?_e.costPerUnit:"",sellingPrice:_e.sellingPriceCUP!==void 0&&_e.sellingPriceCUP!==null?_e.sellingPriceCUP:"",wholesalePrice:_e.wholesalePriceCUP!==void 0&&_e.wholesalePriceCUP!==null?_e.wholesalePriceCUP:"",taxPct:_e.taxPct!==void 0?_e.taxPct:i?.taxConfig?.ratePct??10,taxIncluded:_e.taxIncluded!==void 0?_e.taxIncluded:!0'
assert target_yr in code, "target_yr not found"

replacement_yr = 'unit:_e.unit||"unidades",costPerUnit:_e.costPerUnit!==void 0&&_e.costPerUnit!==null?_e.costPerUnit:"",sellingPrice:(Number(_e.selling_price??_e.price??_e.sellingPriceCUP??0)||(_e.sellingPrice!==void 0?_e.sellingPrice:"")),wholesalePrice:_e.wholesalePriceCUP!==void 0&&_e.wholesalePriceCUP!==null?_e.wholesalePriceCUP:"",taxPct:_e.tax_rate!==void 0?_e.tax_rate:_e.taxPct!==void 0?_e.taxPct:i?.taxConfig?.ratePct??10,taxIncluded:!0'
code = code.replace(target_yr, replacement_yr, 1)
print("Patch 1 (yr edit modal price normalization): OK")

# 2. Update lr (handleSaveItem update existing item)
target_lr_update = 'const Yn=wt.map(xr=>xr.id===Jn?{...xr,...Kn||{},sku:xn,barcode:Ye.barcode.trim()||void 0,name:Ye.name.trim(),category:Ye.category,productType:Ye.productType,currentStock:Mt,current_stock:Mt,branchStock:(()=>{const Ze=xr.branchStock?{...xr.branchStock}:{"branch-main":Mt};return Object.keys(Ze).forEach(dn=>{Ze[dn]=Mt}),Ze})(),minStock:Pe,optimalStock:be,unit:Ye.unit,costPerUnit:Ie,costCUP:Ie,costUSD:Gn,sellingPriceCUP:Xt>0?Xt:void 0,selling_price:Xt>0?Xt:void 0,sellingPrice:Xt>0?Xt:void 0,price:Xt>0?Xt:void 0,selling_price_cup:Xt>0?Xt:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,taxPct:bt,taxIncluded:gt,finalPriceWithTax:Yt>0?Yt:void 0,totalValue:Mt*Ie,supplierName:Ye.supplierName.trim()||"Proveedor General",location:Ye.location||"Almacén Seco",lastRestockedDate:Ye.lastRestockedDate,expirationDate:Ye.expirationDate||void 0,status:Un}:xr);Te(Yn);d(Yn);try{localStorage.setItem("bistro_inventory",JSON.stringify(Yn));localStorage.setItem("cache_inventory",JSON.stringify(Yn));window.dispatchEvent(new CustomEvent("bistro_inventory_updated",{detail:Yn}))}catch(e){};'
assert target_lr_update in code, "target_lr_update not found"

replacement_lr_update = 'const finalPrice=Number(Ye.sellingPrice!==\"\"?Ye.sellingPrice:(Ye.selling_price||Ye.sellingPriceCUP||Ye.price||0));const unitCost=Number(Ye.costPerUnit!==\"\"?Ye.costPerUnit:(Ye.cost_per_unit||Ye.cost||0));const taxRate=Number(Ye.taxPct!==\"\"?Ye.taxPct:(Ye.tax_rate||0));const Yn=wt.map(xr=>{if(xr.id!==Jn)return xr;const wp=xr.warehousePrices?{...xr.warehousePrices}:{};Object.keys(wp).forEach(whId=>{wp[whId]={...wp[whId],retailPriceCUP:finalPrice,sellingPriceCUP:finalPrice};});return{...xr,...Kn||{},sku:xn,barcode:Ye.barcode.trim()||void 0,name:Ye.name.trim(),category:Ye.category,productType:Ye.productType,currentStock:Mt,current_stock:Mt,branchStock:(()=>{const Ze=xr.branchStock?{...xr.branchStock}:{\"branch-main\":Mt};return Object.keys(Ze).forEach(dn=>{Ze[dn]=Mt}),Ze})(),minStock:Pe,optimalStock:be,unit:Ye.unit,cost_per_unit:unitCost,costPerUnit:unitCost,costCUP:unitCost,costUSD:Gn,selling_price:finalPrice,price:finalPrice,sellingPriceCUP:finalPrice,sellingPrice:finalPrice,selling_price_cup:finalPrice>0?finalPrice:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,wholesale_price:zn,tax_rate:taxRate,taxPct:taxRate,taxIncluded:!0,finalPriceWithTax:finalPrice,totalValue:Mt*unitCost,warehousePrices:wp,supplierName:Ye.supplierName.trim()||\"Proveedor General\",location:Ye.location||\"Almacén Seco\",lastRestockedDate:Ye.lastRestockedDate,expirationDate:Ye.expirationDate||void 0,status:Un,updated_at:new Date().toISOString(),updatedAt:new Date().toISOString()};});Te(Yn);d(Yn);try{localStorage.setItem(\"bistro_inventory\",JSON.stringify(Yn));localStorage.setItem(\"cache_inventory\",JSON.stringify(Yn));window.dispatchEvent(new CustomEvent(\"bistro_inventory_updated\",{detail:Yn}))}catch(e){};'
code = code.replace(target_lr_update, replacement_lr_update, 1)
print("Patch 2 (lr update existing item): OK")

# 3. Update lr create new item branch
target_lr_create = 'sellingPriceCUP:Xt>0?Xt:void 0,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,taxPct:bt,taxIncluded:gt,finalPriceWithTax:Yt>0?Yt:void 0,totalValue:Ot*Ie'
assert target_lr_create in code, "target_lr_create not found"

replacement_lr_create = 'selling_price:Xt,price:Xt,sellingPriceCUP:Xt,sellingPrice:Xt,selling_price_cup:Xt>0?Xt:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,wholesale_price:zn,tax_rate:bt,taxPct:bt,taxIncluded:!0,finalPriceWithTax:Xt,totalValue:Ot*Ie'
code = code.replace(target_lr_create, replacement_lr_create, 1)
print("Patch 3 (lr create new item mapping): OK")

# 4. Update InventoryView Table row rendering of selling price and margin
target_table_cell = '_e.finalPriceWithTax||_e.sellingPriceCUP?n.jsxDEV("div",{children:[n.jsxDEV("div",{children:Ha(_e.finalPriceWithTax||_e.sellingPriceCUP||0)}'
assert target_table_cell in code, "target_table_cell not found"

replacement_table_cell = 'Number(_e.selling_price??_e.price??_e.sellingPriceCUP??0)>0?n.jsxDEV("div",{children:[n.jsxDEV("div",{children:Ha(Number(_e.selling_price??_e.price??_e.sellingPriceCUP??0))}'
code = code.replace(target_table_cell, replacement_table_cell, 1)

# Also update the margin calculation in that same table row
target_table_margin = 'Math.round(((_e.finalPriceWithTax||_e.sellingPriceCUP||0)-_e.costPerUnit)/_e.costPerUnit*100)'
assert target_table_margin in code, "target_table_margin not found"

replacement_table_margin = 'Math.round(((Number(_e.selling_price??_e.price??_e.sellingPriceCUP??0)-_e.costPerUnit)/Number(_e.selling_price??_e.price??_e.sellingPriceCUP??1))*100)'
code = code.replace(target_table_margin, replacement_table_margin, 1)
print("Patch 4 (Inventory Table row price and real margin rendering): OK")

# 5. Update PosView Ne price lookup to check selling_price, price, sellingPriceCUP consistently
target_pos_ne = 'const currentPrice=Number(liveProduct.selling_price??liveProduct.sellingPriceCUP??liveProduct.sellingPrice??liveProduct.price??0);'
assert target_pos_ne in code, "target_pos_ne not found"

replacement_pos_ne = 'const currentPrice=Number(liveProduct.selling_price??liveProduct.price??liveProduct.sellingPriceCUP??liveProduct.sellingPrice??0);'
code = code.replace(target_pos_ne, replacement_pos_ne, 1)
print("Patch 5 (PosView Ne price lookup): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All 5 patches successfully applied to assets/index-DCC2oYkl.js!")
