with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# 1. Inside PosView (rAe): define currentBranchId and add posBranchItems state + effect
old_anchor = 'const userBranchId=P.branch_id||P.assignedBranchId||"branch-1792458194300-3i4l",isRestrictedRole=(P.role||"").toLowerCase()!=="admin",he=isRestrictedRole?userBranchId:oe,'

new_anchor = '''const userBranchId=P.branch_id||P.assignedBranchId||"branch-1792458194300-3i4l",isRestrictedRole=(P.role||"").toLowerCase()!=="admin",he=isRestrictedRole?userBranchId:oe,currentBranchId=isRestrictedRole?userBranchId:(he||userBranchId);const[posBranchItems,setPosBranchItems]=S.useState([]);S.useEffect(()=>{let mounted=!0;const loadBranchInv=async()=>{try{if(En()){const sClient=Sn();const{data:posItems,error:posErr}=await sClient.from("branch_inventory").select("id, branch_id, current_stock, min_stock, item_id, inventory:item_id (id, name, category, selling_price_cup, selling_price_usd, barcode, sku, active, status)").eq("branch_id",currentBranchId);if(!posErr&&Array.isArray(posItems)&&posItems.length>0&&mounted){const mapped=posItems.map(item=>{const inv=item.inventory||{};const stockNum=Number(item.current_stock||0);const priceCup=Number(inv.selling_price_cup||inv.price||100);return{id:item.item_id||inv.id,recipeId:item.item_id||inv.id,name:inv.name||`Producto ${item.item_id}`,category:inv.category||"Sellados / Enlatados",price:priceCup,selling_price:priceCup,sellingPriceCUP:priceCup,sellingPrice:priceCup,stock:stockNum,current_stock:stockNum,currentStock:stockNum,branchStock:{[currentBranchId]:stockNum,[he]:stockNum},unit:"uds",sku:inv.sku||"",barcode:inv.barcode||"",productType:"sealed_canned",active:inv.active!==!1};});setPosBranchItems(mapped);return;}}}catch(err){console.warn("[PosView] Error fetching branch_inventory:",err);}};loadBranchInv();return()=>{mounted=!1;};},[currentBranchId,he]);const effectiveInv=posBranchItems.length>0?posBranchItems:t;'''

assert old_anchor in code, "old_anchor not found"
code = code.replace(old_anchor, new_anchor, 1)
print("1. PosView currentBranchId, posBranchItems state and fetch effect inserted")

# 2. In Oc definition: use effectiveInv instead of t
old_oc = 'Oc=S.useMemo(()=>{if(z==="elaborated"||z==="presentations")return[];const we=Hs(L);return t.filter(pt=>{if(!(pt.productType==="sealed_canned"||pt.productType==="raw_ingredient"||pt.productType==="simple"||pt.category==="Bebidas Embotelladas & Licores"||pt.productType!=="elaborated"))return!1;const _t=Hs(pt.name).includes(we),an=pt.sku?Hs(pt.sku).includes(we):!1;return!we||_t||an})},[t,L,z])'

new_oc = 'Oc=S.useMemo(()=>{if(z==="elaborated"||z==="presentations")return[];const we=Hs(L);return effectiveInv.filter(pt=>{if(!(pt.productType==="sealed_canned"||pt.productType==="raw_ingredient"||pt.productType==="simple"||pt.category==="Bebidas Embotelladas & Licores"||pt.productType!=="elaborated"))return!1;const _t=Hs(pt.name).includes(we),an=pt.sku?Hs(pt.sku).includes(we):!1;return!we||_t||an})},[effectiveInv,L,z])'

assert old_oc in code, "old_oc not found"
code = code.replace(old_oc, new_oc, 1)
print("2. Oc catalog uses effectiveInv from branch_inventory")

# 3. In fd (add inventory item to cart): validate stock using product.stock ?? product.current_stock ?? product.branchStock
old_fd = 'fd=we=>{if(!et){ye&&($("open"),B(!0));return}const pt=we.branchStock?.[he]??0,Tt=nn.find(an=>an.recipeId===we.id)?.quantity||0;if(!ve&&pt<=0){xa(`⚠️ Sin existencias en ${ee?.name||"esta sede"} (Stock Sede: 0 ${we.unit}). No se permite venta sin stock.`,"warning");return}if(!ve&&Tt+1>pt){xa(`⚠️ Stock insuficiente en ${ee?.name||"esta sede"} (Disponible: ${pt} ${we.unit}, en carrito: ${Tt}).`,"warning");return}const liveProduct=(Array.isArray(t)&&t.find(p=>p.id===we.id||(p.sku&&we.sku&&p.sku===we.sku)||p.name===we.name))||we;const currentPrice=Number(liveProduct.selling_price??liveProduct.sellingPriceCUP??liveProduct.sellingPrice??liveProduct.price??0);const _t=currentPrice>0?currentPrice:Ne(liveProduct,se);'

new_fd = 'fd=we=>{if(!et){ye&&($("open"),B(!0));return}const availableStock=Number(we.stock??we.current_stock??we.currentStock??we.branchStock?.[he]??we.branchStock?.[currentBranchId]??0);const inCart=nn.find(an=>an.recipeId===we.id||an.id===we.id)?.quantity||0;if(!ve&&availableStock<=0){xa(`⚠️ Sin existencias (${availableStock} disponibles)`,"warning");return}if(!ve&&availableStock<=inCart){xa(`⚠️ Stock insuficiente (${availableStock} disponibles, en carrito: ${inCart})`,"warning");return}const liveProduct=(Array.isArray(effectiveInv)&&effectiveInv.find(p=>p.id===we.id||(p.sku&&we.sku&&p.sku===we.sku)||p.name===we.name))||we;const currentPrice=Number(liveProduct.price??liveProduct.selling_price??liveProduct.sellingPriceCUP??liveProduct.sellingPrice??0);const _t=currentPrice>0?currentPrice:Ne(liveProduct,se);'

assert old_fd in code, "old_fd not found"
code = code.replace(old_fd, new_fd, 1)
print("3. fd stock validation patched with availableStock")

# 4. In Oc.map: calculate an using availableStock so cards don't show Agotado if stock > 0
old_oc_an = 'const pt=nn.find(Nn=>Nn.recipeId===we.id)?.quantity||0,Tt=Ne(we,se),_t=+(Tt/G).toFixed(2),an=we.branchStock?.[he]??0,Gt=!ve&&an<=0;'

new_oc_an = 'const pt=nn.find(Nn=>Nn.recipeId===we.id||Nn.id===we.id)?.quantity||0,Tt=Ne(we,se),_t=+(Tt/G).toFixed(2),an=Number(we.stock??we.current_stock??we.currentStock??we.branchStock?.[he]??we.branchStock?.[currentBranchId]??0),Gt=!ve&&an<=0;'

assert old_oc_an in code, "old_oc_an not found"
code = code.replace(old_oc_an, new_oc_an, 1)
print("4. Oc card stock calculation patched with availableStock")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch applied cleanly!")
