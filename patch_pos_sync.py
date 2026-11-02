with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# 1. Update InventoryView Supabase update query to include selling_price and price
target_sb_update = 'selling_price_cup:Xt>0?Xt:null,selling_price_usd:Tn>0?Tn:null,supplier_name:Ye.supplierName.trim()||null'
assert target_sb_update in code, "target_sb_update not found"
replacement_sb_update = 'selling_price:Xt>0?Xt:null,selling_price_cup:Xt>0?Xt:null,price:Xt>0?Xt:null,selling_price_usd:Tn>0?Tn:null,supplier_name:Ye.supplierName.trim()||null'
code = code.replace(target_sb_update, replacement_sb_update, 1)
print("Patch 1 (InventoryView Supabase update): OK")

# 2. Update InventoryView local item map to set selling_price, price, sellingPrice, warehousePrices
target_local_update = 'sellingPriceCUP:Xt>0?Xt:void 0,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn'
assert target_local_update in code, "target_local_update not found"
replacement_local_update = 'sellingPriceCUP:Xt>0?Xt:void 0,selling_price:Xt>0?Xt:void 0,sellingPrice:Xt>0?Xt:void 0,price:Xt>0?Xt:void 0,selling_price_cup:Xt>0?Xt:null,sellingPriceUSD:Tn>0?Tn:void 0,wholesalePriceCUP:zn'
code = code.replace(target_local_update, replacement_local_update, 1)
print("Patch 2 (InventoryView local item map): OK")

# 3. Update InventoryView persistence dispatch
target_persist = 'return d(Yn),Yn}),u?.("inventory",`Artículo actualizado: ${Ye.name} (${xn})`'
assert target_persist in code, "target_persist not found"
replacement_persist = 'try{localStorage.setItem("bistro_inventory",JSON.stringify(Yn));localStorage.setItem("cache_inventory",JSON.stringify(Yn));window.dispatchEvent(new CustomEvent("bistro_inventory_updated",{detail:Yn}))}catch(e){};return d(Yn),Yn}),u?.("inventory",`Artículo actualizado: ${Ye.name} (${xn})`'
code = code.replace(target_persist, replacement_persist, 1)
print("Patch 3 (InventoryView storage & event sync): OK")

# 4. Update PosView Ne price resolver to ALWAYS resolve live product and live price
target_ne = 'const Ne=(we,pt=se)=>{const Tt=we.warehousePrices?.[he];if(pt==="mayorista"){if(Tt?.wholesalePriceCUP!==void 0&&Tt.wholesalePriceCUP>0)return Tt.wholesalePriceCUP;if(we.wholesalePriceCUP!==void 0&&we.wholesalePriceCUP>0)return we.wholesalePriceCUP}else{if(Tt?.retailPriceCUP!==void 0&&Tt.retailPriceCUP>0)return Tt.retailPriceCUP;if(we.sellingPriceCUP!==void 0&&we.sellingPriceCUP>0)return we.sellingPriceCUP}return we.sellingPriceCUP!==void 0&&we.sellingPriceCUP>0?we.sellingPriceCUP:we.costPerUnit?+(we.costPerUnit*1.6).toFixed(2):450}'
assert target_ne in code, "target_ne not found"
replacement_ne = 'const Ne=(we,pt=se)=>{const liveProduct=(Array.isArray(t)&&t.find(p=>p.id===we.id||(p.sku&&we.sku&&p.sku===we.sku)||p.name===we.name))||(Array.isArray(e)&&e.find(r=>r.id===we.id||r.name===we.name))||we;const currentPrice=Number(liveProduct.selling_price??liveProduct.sellingPriceCUP??liveProduct.sellingPrice??liveProduct.price??0);const Tt=liveProduct.warehousePrices?.[he];if(pt==="mayorista"){if(Tt?.wholesalePriceCUP!==void 0&&Number(Tt.wholesalePriceCUP)>0)return Number(Tt.wholesalePriceCUP);if(liveProduct.wholesalePriceCUP!==void 0&&Number(liveProduct.wholesalePriceCUP)>0)return Number(liveProduct.wholesalePriceCUP)}else{if(currentPrice>0)return currentPrice;if(Tt?.retailPriceCUP!==void 0&&Number(Tt.retailPriceCUP)>0)return Number(Tt.retailPriceCUP)}return currentPrice>0?currentPrice:liveProduct.costPerUnit?+(Number(liveProduct.costPerUnit)*1.6).toFixed(2):450}'
code = code.replace(target_ne, replacement_ne, 1)
print("Patch 4 (PosView Ne live product & price): OK")

# 5. Update PosView fd (inventory item add-to-cart) to resolve live price and update cart unitPrice
target_fd = 'const _t=Ne(we,se);Ca(an=>{const Gt=an.findIndex(Nn=>Nn.recipeId===we.id);if(Gt>=0){const Nn=[...an],An=Nn[Gt],ya=An.quantity+1;return Nn[Gt]={...An,quantity:ya,subtotal:+(ya*An.unitPrice).toFixed(2)},Nn}else{const Nn={recipeId:we.id,name:we.name,category:"Sellados / Enlatados",unitPrice:_t,quantity:1,subtotal:_t,modifiers:[],isElaboration:!1,sentToKitchenQty:0};return[...an,Nn]}})'
assert target_fd in code, "target_fd not found"
replacement_fd = 'const liveProduct=(Array.isArray(t)&&t.find(p=>p.id===we.id||(p.sku&&we.sku&&p.sku===we.sku)||p.name===we.name))||we;const currentPrice=Number(liveProduct.selling_price??liveProduct.sellingPriceCUP??liveProduct.sellingPrice??liveProduct.price??0);const _t=currentPrice>0?currentPrice:Ne(liveProduct,se);Ca(an=>{const Gt=an.findIndex(Nn=>Nn.recipeId===we.id);if(Gt>=0){const Nn=[...an],An=Nn[Gt],ya=An.quantity+1;return Nn[Gt]={...An,unitPrice:_t,quantity:ya,subtotal:+(ya*_t).toFixed(2)},Nn}else{const Nn={recipeId:we.id,name:we.name,category:"Sellados / Enlatados",unitPrice:_t,quantity:1,subtotal:_t,modifiers:[],isElaboration:!1,sentToKitchenQty:0};return[...an,Nn]}})'
code = code.replace(target_fd, replacement_fd, 1)
print("Patch 5 (PosView fd live price on cart add/increment): OK")

# 6. Update PosView Xd (recipe add-to-cart) to resolve live price from inventory / recipe and update cart unitPrice
target_xd = 'const _t=Array.isArray(we.ingredients)&&we.ingredients.length>0,an=Number(we.sellingPriceCUP??we.selling_price??we.sellingPrice??0);Ca(Gt=>{const Nn=Gt.findIndex(An=>An.recipeId===we.id);if(Nn>=0){const An=[...Gt],ya=An[Nn],nr=ya.quantity+1;return An[Nn]={...ya,quantity:nr,subtotal:+(nr*ya.unitPrice).toFixed(2)},An}else{const An={recipeId:we.id,name:we.name,category:we.category,unitPrice:an,quantity:1,subtotal:an,modifiers:[],isElaboration:_t,sentToKitchenQty:0};return[...Gt,An]}})'
assert target_xd in code, "target_xd not found"
replacement_xd = 'const _t=Array.isArray(we.ingredients)&&we.ingredients.length>0,liveRecipe=(Array.isArray(e)&&e.find(r=>r.id===we.id||r.name===we.name))||we,liveInv=Array.isArray(t)&&t.find(p=>p.id===we.id||p.recipe_id===we.id||p.name===we.name),an=Number(liveInv?.selling_price??liveInv?.sellingPriceCUP??liveInv?.price??liveRecipe.selling_price??liveRecipe.sellingPriceCUP??liveRecipe.sellingPrice??liveRecipe.price??0);Ca(Gt=>{const Nn=Gt.findIndex(An=>An.recipeId===we.id);if(Nn>=0){const An=[...Gt],ya=An[Nn],nr=ya.quantity+1;return An[Nn]={...ya,unitPrice:an>0?an:ya.unitPrice,quantity:nr,subtotal:+(nr*(an>0?an:ya.unitPrice)).toFixed(2)},An}else{const An={recipeId:we.id,name:we.name,category:we.category,unitPrice:an,quantity:1,subtotal:an,modifiers:[],isElaboration:_t,sentToKitchenQty:0};return[...Gt,An]}})'
code = code.replace(target_xd, replacement_xd, 1)
print("Patch 6 (PosView Xd live price on recipe cart add/increment): OK")

# 7. Add Cart dynamic price synchronization hook in PosView
target_cart_hook = 'const Ge=S.useMemo(()=>Ae.find(we=>we.id===pe)||Ae[0]||null,[Ae,pe]),Dt='
assert target_cart_hook in code, "target_cart_hook not found"
replacement_cart_hook = 'S.useEffect(()=>{if(Ae&&Ae.length>0&&Array.isArray(t)&&t.length>0){let changed=false;const updatedTabs=Ae.map(tab=>{if(!tab.items||tab.items.length===0)return tab;let tabChanged=false;const updatedItems=tab.items.map(item=>{const liveP=t.find(p=>p.id===item.recipeId||(p.sku&&item.sku&&p.sku===item.sku)||p.name===item.name);if(liveP){const freshP=Number(liveP.selling_price??liveP.sellingPriceCUP??liveP.sellingPrice??liveP.price??0);if(freshP>0&&freshP!==item.unitPrice){tabChanged=true;return{...item,unitPrice:freshP,subtotal:+(item.quantity*freshP).toFixed(2)}}};return item;});if(tabChanged){changed=true;return{...tab,items:updatedItems,updatedAt:new Date().toISOString()}};return tab;});if(changed){re(updatedTabs);try{localStorage.setItem(`bistro_pos_tabs_${oe}`,JSON.stringify(updatedTabs))}catch(e){}}}},[t,oe]);const Ge=S.useMemo(()=>Ae.find(we=>we.id===pe)||Ae[0]||null,[Ae,pe]),Dt='
code = code.replace(target_cart_hook, replacement_cart_hook, 1)
print("Patch 7 (PosView active cart auto-sync on inventory change): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All 7 patches applied successfully to assets/index-DCC2oYkl.js!")
