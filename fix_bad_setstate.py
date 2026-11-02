with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. First block: edit item
target1 = 'Te(ot=>{const Yn=ot.map(xr=>xr.id===Jn?{...xr,...Kn||{},sku:xn,barcode:Ye.barcode.trim()||void 0,name:Ye.name.trim(),category:Ye.category,productType:Ye.productType,currentStock:Mt,current_stock:Mt,branchStock:(()=>{const Ze=xr.branchStock?{...xr.branchStock}:{"branch-main":Mt};return Object.keys(Ze).forEach(dn=>{Ze[dn]=Mt}),Ze})(),minStock:Pe,optimalStock:be,unit:Ye.unit,costPerUnit:Ie,costCUP:Ie,costUSD:Gn,sellingPriceCUP:Xt>0?Xt:void 0,selling_price:Xt>0?Xt:void 0,sellingPrice:Xt>0?Xt:void 0,price:Xt>0?Xt:void 0,selling_price_cup:Xt>0?Xt:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,taxPct:bt,taxIncluded:gt,finalPriceWithTax:Yt>0?Yt:void 0,totalValue:Mt*Ie,supplierName:Ye.supplierName.trim()||"Proveedor General",location:Ye.location||"Almacén Seco",lastRestockedDate:Ye.lastRestockedDate,expirationDate:Ye.expirationDate||void 0,status:Un}:xr);try{localStorage.setItem("bistro_inventory",JSON.stringify(Yn));localStorage.setItem("cache_inventory",JSON.stringify(Yn));window.dispatchEvent(new CustomEvent("bistro_inventory_updated",{detail:Yn}))}catch(e){};return d(Yn),Yn})'
assert target1 in code, "Target 1 not found"

replacement1 = 'const Yn=wt.map(xr=>xr.id===Jn?{...xr,...Kn||{},sku:xn,barcode:Ye.barcode.trim()||void 0,name:Ye.name.trim(),category:Ye.category,productType:Ye.productType,currentStock:Mt,current_stock:Mt,branchStock:(()=>{const Ze=xr.branchStock?{...xr.branchStock}:{"branch-main":Mt};return Object.keys(Ze).forEach(dn=>{Ze[dn]=Mt}),Ze})(),minStock:Pe,optimalStock:be,unit:Ye.unit,costPerUnit:Ie,costCUP:Ie,costUSD:Gn,sellingPriceCUP:Xt>0?Xt:void 0,selling_price:Xt>0?Xt:void 0,sellingPrice:Xt>0?Xt:void 0,price:Xt>0?Xt:void 0,selling_price_cup:Xt>0?Xt:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn,wholesalePriceUSD:tr,taxPct:bt,taxIncluded:gt,finalPriceWithTax:Yt>0?Yt:void 0,totalValue:Mt*Ie,supplierName:Ye.supplierName.trim()||"Proveedor General",location:Ye.location||"Almacén Seco",lastRestockedDate:Ye.lastRestockedDate,expirationDate:Ye.expirationDate||void 0,status:Un}:xr);Te(Yn);d(Yn);try{localStorage.setItem("bistro_inventory",JSON.stringify(Yn));localStorage.setItem("cache_inventory",JSON.stringify(Yn));window.dispatchEvent(new CustomEvent("bistro_inventory_updated",{detail:Yn}))}catch(e){}'
code = code.replace(target1, replacement1, 1)
print("Patch 1 (Edit item updater): OK")

# 2. Second block: create item
target2 = 'Te(Yn=>{const xr=[ot,...Yn.filter(Ze=>Ze.id!==ot.id)];return d(xr),xr})'
assert target2 in code, "Target 2 not found"
replacement2 = 'const xr=[ot,...wt.filter(Ze=>Ze.id!==ot.id)];Te(xr);d(xr)'
code = code.replace(target2, replacement2, 1)
print("Patch 2 (Create item updater): OK")

# 3. Third block: delete item
target3 = 'Te(Ie=>{const Be=Ie.filter(bt=>bt.id!==_e);return d(Be),Be})'
assert target3 in code, "Target 3 not found"
replacement3 = 'const Be=wt.filter(bt=>bt.id!==_e);Te(Be);d(Be)'
code = code.replace(target3, replacement3, 1)
print("Patch 3 (Delete item updater): OK")

# 4. Fourth block: stock adjustment
target4 = 'Te(Un=>{const xn=Un.map(Gn=>{if(Gn.id===Ie){const Tn=Gn.minStock||0;let zn="optimal";Tn>0&&(Yt<=Tn*.5?zn="critical":Yt<=Tn&&(zn="low"));const tr=Gn.branchStock?{...Gn.branchStock}:{"branch-main":Yt};return Object.keys(tr).forEach(Jn=>{tr[Jn]=Yt}),{...Gn,...Xt||{},currentStock:Yt,current_stock:Yt,branchStock:tr,totalValue:+(Yt*(Gn.costPerUnit||Gn.costCUP||0)).toFixed(2),status:zn}}return Gn});return d(xn),xn})'
assert target4 in code, "Target 4 not found"
replacement4 = 'const xn=wt.map(Gn=>{if(Gn.id===Ie){const Tn=Gn.minStock||0;let zn="optimal";Tn>0&&(Yt<=Tn*.5?zn="critical":Yt<=Tn&&(zn="low"));const tr=Gn.branchStock?{...Gn.branchStock}:{"branch-main":Yt};return Object.keys(tr).forEach(Jn=>{tr[Jn]=Yt}),{...Gn,...Xt||{},currentStock:Yt,current_stock:Yt,branchStock:tr,totalValue:+(Yt*(Gn.costPerUnit||Gn.costCUP||0)).toFixed(2),status:zn}}return Gn});Te(xn);d(xn)'
code = code.replace(target4, replacement4, 1)
print("Patch 4 (Stock adjustment updater): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All 4 bad setState in render issues successfully resolved in assets/index-DCC2oYkl.js!")
