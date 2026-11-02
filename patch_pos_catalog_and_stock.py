import sys

def run():
    target_path = 'assets/index-DCC2oYkl.js'
    with open(target_path, 'r', encoding='utf-8') as f:
        code = f.read()

    pos = 3650928
    
    # 1. Target block 1: from [oe,be]=S.useState to he = S.useMemo(...)
    target1_start_str = '[oe,be]=S.useState(()=>P.role==="admin"||P.role?.toLowerCase()==="admin"'
    idx_target1_start = code.find(target1_start_str, pos)
    if idx_target1_start == -1:
        print("ERROR: Could not find target1_start_str")
        sys.exit(1)
        
    target1_end_str = 'const ye = ve.find(Ee=>Ee.id===te)||l.find(Ee=>'
    idx_target1_end = code.find(target1_end_str, idx_target1_start)
    if idx_target1_end == -1:
        print("ERROR: Could not find target1_end_str")
        sys.exit(1)

    replacement1 = '''const defaultBranchId="branch-1792458194300-3i4l",[oe,be]=S.useState(()=>{const saved=localStorage.getItem("bistro_active_branch_id")||localStorage.getItem("active_branch_id")||localStorage.getItem("selected_branch_id");if(saved&&(saved===defaultBranchId||(ve&&ve.some(b=>b.id===saved))))return saved;if(o?.activeBranchId)return o.activeBranchId;const cafeBranch=(ve||[]).find(b=>b.id===defaultBranchId||(b.name&&b.name.toLowerCase().includes("calle a")));if(cafeBranch)return cafeBranch.id;return ve[0]?.id||defaultBranchId});S.useEffect(()=>{const Ee=(P.role||"").toLowerCase()!=="admin",Nt=P.branch_id||P.assignedBranchId;Ee&&Nt&&(be(Nt),localStorage.setItem("active_branch_id",Nt),localStorage.setItem("selected_branch_id",Nt))},[P.branch_id,P.assignedBranchId,P.role,P.roleTitle]);const De=localStorage.getItem("selected_branch_id")||localStorage.getItem("active_branch_id")||P.branch_id||P.assignedBranchId||defaultBranchId,se=(P.role||"").toLowerCase()!=="admin",te=oe||De||defaultBranchId,H=te,[branchStockMap,setBranchStockMap]=S.useState(()=>{const initMap={};try{const loc=window.__BISTRO_LOCAL_STORE__?window.__BISTRO_LOCAL_STORE__.getLocalInventory(te):[];(loc||[]).forEach(it=>{const cid=String(it.id||it.item_id||"").replace(/^(inv_|ing_)/,""),stock=Number(it.current_stock??it.stock??0);if(cid){initMap[`${te}_${cid}`]=stock;initMap[cid]=stock}})}catch{}return initMap});S.useEffect(()=>{let mounted=true;const loadBranchInv=async()=>{try{if(ya()){const sClient=ka(),branchIds=Array.from(new Set([te,defaultBranchId].filter(Boolean))),{data:posItems,error:posErr}=await sClient.from("branch_inventory").select("id, branch_id, current_stock, min_stock, item_id, updated_at").in("branch_id",branchIds);if(!posErr&&Array.isArray(posItems)&&mounted){const mapObj={};posItems.forEach(item=>{if(item.branch_id&&item.item_id){const rawId=String(item.item_id),cid=rawId.replace(/^(inv_|ing_)/,""),stockNum=Number(item.current_stock)||0;mapObj[`${item.branch_id}_${rawId}`]=stockNum;mapObj[`${item.branch_id}_${cid}`]=stockNum;if(item.branch_id===te){mapObj[rawId]=stockNum;mapObj[cid]=stockNum}}});setBranchStockMap(prev=>({...prev,...mapObj}))}}}catch(err){console.warn("[PosView] Error fetching branch_inventory:",err)}};loadBranchInv();const onBranchStockUpdated=(ev)=>{if(mounted&&ev?.detail&&typeof ev.detail==="object"){setBranchStockMap(prev=>({...prev,...ev.detail}))}};window.addEventListener("bistro_branch_stock_updated",onBranchStockUpdated);return()=>{mounted=false;window.removeEventListener("bistro_branch_stock_updated",onBranchStockUpdated)}},[H,te]);const he=S.useMemo(()=>{return(t||[]).map(it=>{const rawId=String(it.id||""),cid=rawId.replace(/^(inv_|ing_)/,""),stockVal=Number(branchStockMap[`${te}_${rawId}`]??branchStockMap[`${te}_${cid}`]??branchStockMap[rawId]??branchStockMap[cid]??it.branchStock?.[te]??it.current_stock??0);return{...it,current_stock:stockVal,currentStock:stockVal,stock:stockVal,branchStock:{...(it.branchStock||{}),[te]:stockVal}}})},[t,branchStockMap,te]);const ye=ve.find(Ee=>Ee.id===te)||l.find(Ee=>'''

    # Apply replacement 1
    code = code[:idx_target1_start] + replacement1 + code[idx_target1_end + len(target1_end_str):]
    print("Replacement 1 applied!")

    # 2. Target block 2: Lo to posCatalog
    target2_start_str = 'Lo = S.useMemo(() => {'
    idx_target2_start = code.find(target2_start_str, pos)
    if idx_target2_start == -1:
        print("ERROR: Could not find target2_start_str")
        sys.exit(1)

    target2_end_str = 'return list;\n}, [he, e, W, B, F, branchStockMap, te]),'
    idx_target2_end = code.find(target2_end_str, idx_target2_start)
    if idx_target2_end == -1:
        # try without newline
        target2_end_str = 'return list;}, [he, e, W, B, F, branchStockMap, te]),'
        idx_target2_end = code.find(target2_end_str, idx_target2_start)
    if idx_target2_end == -1:
        print("ERROR: Could not find target2_end_str")
        sys.exit(1)

    replacement2 = '''Lo=S.useMemo(()=>{const catSet=new Set();(he||[]).forEach(it=>{if(!it||it.active===false)return;const isSupplies=!Boolean(it.category==="Elaboraciones"||it.productType==="elaborated"||it.recipe_id)&&(it.category==="Desechables & Packaging"||it.category==="Limpieza y Suministros"||it.category==="Útiles y Desechables"||it.category==="Ingredientes Frescos"||it.category==="Materias Primas"),itemPrice=Number(it.selling_price_cup??it.sellingPriceCUP??it.selling_price??it.price??0);if(isSupplies&&!(itemPrice>0))return;const matched=(e||[]).find(r=>r&&(r.id===it.recipe_id||r.id===it.id||Ss(r.name)===Ss(it.name))),cat=matched?.category||it.category;if(cat)catSet.add(cat)});return Array.from(catSet)},[he,e]),cleanId=Ee=>String(Ee||"").replace(/^(inv_|ing_)/,"").trim(),Ss=Ee=>String(Ee||"").toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").trim(),getElaborationAvailability=(item,matchedRecipe)=>{const isElab=Boolean(matchedRecipe||item.category==="Elaboraciones"||item.productType==="elaborated"||item.product_type==="elaborated"||item.is_produced_internally),rawId=String(item.id||""),cid=cleanId(rawId);if(!isElab){const rawStock=Number(branchStockMap[`${te}_${rawId}`]??branchStockMap[`${te}_${cid}`]??branchStockMap[rawId]??branchStockMap[cid]??item.branchStock?.[te]??item.current_stock??0),isEx=Boolean(!Xe&&rawStock<=0);return{isElab:false,availableStock:rawStock,isExhausted:isEx,badgeText:isEx?"Agotado":"Sellado",stockLabel:isEx?"Agotado en sede":`Stock Sede: ${rawStock} ${item.unit||"uds"}`}}const finishedStock=Number(branchStockMap[`${te}_${rawId}`]??branchStockMap[`${te}_${cid}`]??(matchedRecipe&&(branchStockMap[`${te}_${matchedRecipe.id}`]??branchStockMap[matchedRecipe.id]))??item.branchStock?.[te]??item.current_stock??0);let racionStock=0,racionLabel="Ración Café";const racionId="rec-1792924420963",racionBranchStock=Number(branchStockMap[`${te}_${racionId}`]??branchStockMap[`${defaultBranchId}_${racionId}`]??branchStockMap[racionId]??0);if(racionBranchStock>0){racionStock=racionBranchStock;racionLabel="Ración Café"}if(matchedRecipe&&Array.isArray(matchedRecipe.ingredients)){for(const ing of matchedRecipe.ingredients){const ingName=Ss(ing.ingredientName||ing.name||""),ingId=String(ing.ingredientId||ing.inventoryId||ing.id||""),ingCid=cleanId(ingId),isCoffeeOrSubElab=ingName.includes("cafe")||ing.isElaboration||ing.type==="elaboration";if(isCoffeeOrSubElab){const subStock=Number(branchStockMap[`${te}_${ingId}`]??branchStockMap[`${te}_${ingCid}`]??branchStockMap[`${defaultBranchId}_${ingId}`]??branchStockMap[ingId]??(t||[]).find(it=>it.id===ingId)?.current_stock??0),reqQty=Math.max(0.001,Math.abs(Number(ing.quantity||1))),possiblePortions=Math.floor(subStock/reqQty);if(possiblePortions>0){racionStock=Math.max(racionStock,possiblePortions);racionLabel=ing.name||ing.ingredientName||"Ración Café"}}}}if(racionStock<=0){const rawRacion=(t||[]).find(it=>it&&(it.id===racionId||Ss(it.name).includes("racion de cafe")));if(rawRacion){const rStock=Number(branchStockMap[`${te}_${rawRacion.id}`]??branchStockMap[`${defaultBranchId}_${rawRacion.id}`]??rawRacion.branchStock?.[te]??rawRacion.current_stock??0);if(rStock>0){racionStock=rStock;racionLabel=rawRacion.name||"Ración Café"}}}const portionsAvailable=finishedStock>0?(finishedStock+racionStock):racionStock,isEx=Boolean(!Xe&&finishedStock<=0&&racionStock<=0);let sLabel="";if(finishedStock>0&&racionStock>0){sLabel=`Stock: ${finishedStock} (+${racionStock} a pedido)`}else if(finishedStock>0){sLabel=`Stock: ${finishedStock} ${item.unit||"porciones"}`}else if(racionStock>0){sLabel=`A pedido: ${racionStock} disp. (${racionLabel})`}else{sLabel=isEx?"Agotado en sede":"Elaboración a pedido"}return{isElab:true,availableStock:portionsAvailable,finishedStock,racionStock,isExhausted:isEx,badgeText:isEx?"Agotado":"A Pedido",stockLabel:sLabel}},posCatalog=S.useMemo(()=>{const searchNorm=Ss(F),seenIds=new Set(),seenNames=new Set(),list=[];(he||[]).forEach(it=>{if(!it||it.active===false)return;const cId=cleanId(it.id),cName=Ss(it.name);if(seenIds.has(cId)||(cName&&seenNames.has(cName)))return;const isSupplies=!Boolean(it.category==="Elaboraciones"||it.productType==="elaborated"||it.recipe_id)&&(it.category==="Desechables & Packaging"||it.category==="Limpieza y Suministros"||it.category==="Útiles y Desechables"||it.category==="Ingredientes Frescos"||it.category==="Materias Primas"),itemPrice=Number(it.selling_price_cup??it.sellingPriceCUP??it.selling_price??it.price??0);if(isSupplies&&!(itemPrice>0))return;const matchedRecipe=(e||[]).find(r=>r&&(r.id===it.recipe_id||r.id===it.id||r.id===cId||Ss(r.name)===cName)),isElab=Boolean(matchedRecipe||it.category==="Elaboraciones"||it.productType==="elaborated"||it.product_type==="elaborated"||it.is_produced_internally);if(W==="elaborated"&&!isElab)return;if(W==="sealed_canned"&&isElab)return;if(W==="presentations")return;const itemCat=it.category||"",recipeCat=matchedRecipe?.category||"",displayCat=recipeCat||(itemCat==="Elaboraciones"&&recipeCat?recipeCat:itemCat)||"General",matchesCat=B==="all"||itemCat.toLowerCase()===B.toLowerCase()||recipeCat.toLowerCase()===B.toLowerCase()||displayCat.toLowerCase()===B.toLowerCase();if(!matchesCat)return;const matchesSearch=!searchNorm||cName.includes(searchNorm)||(it.sku&&Ss(it.sku).includes(searchNorm));if(!matchesSearch)return;seenIds.add(cId);if(cName)seenNames.add(cName);const finalPrice=itemPrice>0?itemPrice:Number(matchedRecipe?.selling_price_cup??matchedRecipe?.selling_price??matchedRecipe?.sellingPriceCUP??matchedRecipe?.sellingPrice??0);list.push({rawItem:it,matchedRecipe:matchedRecipe,id:it.id,recipe_id:matchedRecipe?.id||it.recipe_id||it.id,name:it.name,category:displayCat,unit:it.unit||(isElab?"porciones":"unidades"),price:finalPrice,sku:it.sku||"",isElab:isElab})});return list},[he,e,W,B,F,branchStockMap,te]),'''

    # Apply replacement 2
    code = code[:idx_target2_start] + replacement2 + code[idx_target2_end + len(target2_end_str):]
    print("Replacement 2 applied!")

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("File saved successfully!")

if __name__ == '__main__':
    run()
