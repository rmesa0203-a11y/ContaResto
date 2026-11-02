with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. PosView: NEVER sum multiple rows in loadBranchInv, always order by updated_at.desc
# ---------------------------------------------------------------------------
old_pos_query = 'const{data:posItems,error:posErr}=await sClient.from("branch_inventory").select("id, branch_id, current_stock, min_stock, item_id, inventory:item_id (id, name, category, selling_price_cup, selling_price_usd, barcode, sku, active, status)").eq("branch_id",currentBranchId);if(!posErr&&Array.isArray(posItems)&&posItems.length>0&&mounted){const uMap=new Map();posItems.forEach(item=>{const k=item.item_id||item.inventory?.id||item.id;if(!k)return;if(!uMap.has(k)){uMap.set(k,{...item});}else{const prev=uMap.get(k);prev.current_stock=Number(prev.current_stock||0)+Number(item.current_stock||0);}});'

new_pos_query = 'const{data:posItems,error:posErr}=await sClient.from("branch_inventory").select("id, branch_id, current_stock, min_stock, item_id, updated_at, inventory:item_id (id, name, category, selling_price_cup, selling_price_usd, barcode, sku, active, status)").eq("branch_id",currentBranchId).order("updated_at",{ascending:!1});if(!posErr&&Array.isArray(posItems)&&posItems.length>0&&mounted){const uMap=new Map();posItems.forEach(item=>{const k=item.item_id||item.inventory?.id||item.id;if(!k)return;if(!uMap.has(k)){uMap.set(k,item);}});'

assert old_pos_query in code, "old_pos_query not found"
code = code.replace(old_pos_query, new_pos_query, 1)
print("1. PosView loadBranchInv query updated: NEVER sum, order by updated_at.desc")


# ---------------------------------------------------------------------------
# 2. IPVSheetView (NAe): order branch_inventory by updated_at.desc and NEVER sum
# ---------------------------------------------------------------------------
old_nae_query = 'const{data:bItems,error:bErr}=await sClient.from("branch_inventory").select("id, current_stock, min_stock, item_id, inventory:item_id (id, name, unit, category, selling_price_cup)").eq("branch_id",branchToQuery);if(!bErr&&Array.isArray(bItems)&&bItems.length>0&&mounted){const rows=bItems.map(item=>{'

new_nae_query = 'const{data:bItems,error:bErr}=await sClient.from("branch_inventory").select("id, current_stock, min_stock, item_id, updated_at, inventory:item_id (id, name, unit, category, selling_price_cup)").eq("branch_id",branchToQuery).order("updated_at",{ascending:!1});if(!bErr&&Array.isArray(bItems)&&bItems.length>0&&mounted){const uMap=new Map();bItems.forEach(item=>{const k=item.item_id||item.inventory?.id||item.id;if(k&&!uMap.has(k))uMap.set(k,item);});const uniqueBItems=Array.from(uMap.values());const rows=uniqueBItems.map(item=>{'

assert old_nae_query in code, "old_nae_query not found"
code = code.replace(old_nae_query, new_nae_query, 1)
print("2. IPVSheetView loadInv updated: order by updated_at.desc and deduplicate")


# ---------------------------------------------------------------------------
# 3. Zt.getBranchInventory: order by updated_at.desc
# ---------------------------------------------------------------------------
old_gbi = 'let r=Sn().from("branch_inventory").select("*");t&&t!=="all"&&(r=r.eq("branch_id",t));'
new_gbi = 'let r=Sn().from("branch_inventory").select("*").order("updated_at",{ascending:!1});t&&t!=="all"&&(r=r.eq("branch_id",t));'

assert old_gbi in code, "old_gbi not found"
code = code.replace(old_gbi, new_gbi, 1)
print("3. Zt.getBranchInventory updated: order by updated_at.desc")


# ---------------------------------------------------------------------------
# 4. InventoryView (W7e): eliminate blinking with isLoadingInventory state & spinner
# ---------------------------------------------------------------------------
# In W7e state declaration:
old_w7e_init = 'V=s&&s.length>0?s.filter(_e=>_e.active!==!1):N,[E,k]=S.useState({});S.useEffect(()=>{let _e=!0;Zt.getBranchInventory().then(Pe=>{if(!_e||!Array.isArray(Pe))return;const be={};Pe.forEach(Ie=>{Ie.branch_id&&Ie.item_id&&(be[`${Ie.branch_id}_${Ie.item_id}`]=Number(Ie.current_stock)||0)}),k(be)}).catch(Pe=>console.warn("[InventoryView] getBranchInventory notice:",Pe));const Ot=Zt.subscribeBranchInventory(Pe=>{_e&&k(be=>({...be,[`${Pe.branch_id}_${Pe.item_id}`]:Number(Pe.current_stock)||0}))});return()=>{_e=!1,Ot()}},[]);'

new_w7e_init = 'V=s&&s.length>0?s.filter(_e=>_e.active!==!1):N,[E,k]=S.useState({}),[isLoadingStock,setIsLoadingStock]=S.useState(!0);S.useEffect(()=>{let _e=!0;const targetBr=userRole!=="admin"?(m.branch_id||m.assignedBranchId||"branch-1792458194300-3i4l"):null;Zt.getBranchInventory(targetBr).then(Pe=>{if(!_e||!Array.isArray(Pe))return;const be={};Pe.forEach(Ie=>{const key=`${Ie.branch_id}_${Ie.item_id}`;if(Ie.branch_id&&Ie.item_id&&be[key]===void 0){be[key]=Number(Ie.current_stock)||0;}});k(be);setIsLoadingStock(!1);}).catch(Pe=>{console.warn("[InventoryView] getBranchInventory notice:",Pe);_e&&setIsLoadingStock(!1);});const Ot=Zt.subscribeBranchInventory(Pe=>{_e&&k(be=>({...be,[`${Pe.branch_id}_${Pe.item_id}`]:Number(Pe.current_stock)||0}))});return()=>{_e=!1,Ot()}},[userRole,m.branch_id,m.assignedBranchId]);'

assert old_w7e_init in code, "old_w7e_init not found"
code = code.replace(old_w7e_init, new_w7e_init, 1)
print("4. InventoryView isLoadingStock and deduped fetch inserted")

# In InventoryView ft (stock calculation): NEVER read Ot.currentStock for a branch, only E
old_w7e_ft = 'else{const xn=`${U}_${Ot.id}`;xn in E?Pe=E[xn]:Pe=Ot.branchStock?.[U]??0}'
new_w7e_ft = 'else{const xn=`${U}_${Ot.id}`;Pe=xn in E?E[xn]:0;}'

assert old_w7e_ft in code, "old_w7e_ft not found"
code = code.replace(old_w7e_ft, new_w7e_ft, 1)
print("5. InventoryView ft calculation: strictly branch_inventory (never fallback)")

# In InventoryView return statement: render loading skeleton if isLoadingStock is true
old_w7e_ret = 'return n.jsxDEV("div",{className:"space-y-6 animate-fadeIn pb-12",children:[j&&'
new_w7e_ret = 'if(isLoadingStock)return n.jsxDEV("div",{className:"min-h-[400px] flex flex-col items-center justify-center p-12 text-center space-y-3",children:[n.jsxDEV("div",{className:"w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"},void 0,!1,{},void 0),n.jsxDEV("h3",{className:"text-sm font-bold text-slate-800 dark:text-white",children:"Sincronizando existencias de sucursal..."},void 0,!1,{},void 0),n.jsxDEV("p",{className:"text-xs text-slate-500 dark:text-slate-400",children:"Consultando existencias reales de branch_inventory."},void 0,!1,{},void 0)]},void 0,!0,{},void 0);return n.jsxDEV("div",{className:"space-y-6 animate-fadeIn pb-12",children:[j&&'

assert old_w7e_ret in code, "old_w7e_ret not found"
code = code.replace(old_w7e_ret, new_w7e_ret, 1)
print("6. InventoryView loading spinner inserted to eliminate blinking")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Single source of truth patch applied cleanly!")
