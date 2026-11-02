with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. WorkShiftModal: Strict branch locking for user.role !== 'admin'
# ---------------------------------------------------------------------------
# In WorkShiftModal:
# Old initialization:
# const N=i||$l,V=N.role==="kitchen"||N.role==="clerk",E=S.useMemo(...)
old_wsm_init = 'const N=i||$l,V=N.role==="kitchen"||N.role==="clerk",E=S.useMemo(()=>Array.isArray(s)&&s.length>0?s.filter(at=>at.active!==!1):r&&r.active!==!1?[r]:[],[s,r]),[k,j]=S.useState(t),[I,M]=S.useState(()=>V&&N.assignedBranchId&&N.role!=="admin"?N.assignedBranchId:r?.id||(E.length>0?E[0].id:"branch-main")),'

new_wsm_init = 'const N=i||$l,isRestricted=(N.role||"").toLowerCase()!=="admin",userBranch=N.branch_id||N.assignedBranchId||"branch-1792458194300-3i4l",V=isRestricted,E=S.useMemo(()=>Array.isArray(s)&&s.length>0?s.filter(at=>at.active!==!1):r&&r.active!==!1?[r]:[],[s,r]),[k,j]=S.useState(t),[I,M]=S.useState(()=>isRestricted?userBranch:r?.id||(E.length>0?E[0].id:userBranch)),'

if old_wsm_init in code:
    code = code.replace(old_wsm_init, new_wsm_init, 1)
    print("1.1 WorkShiftModal initialization patched")
else:
    print("1.1 old_wsm_init not found directly")

# In WorkShiftModal effect when opening shift:
old_wsm_eff = 'const at=r?.id||(V&&N.assignedBranchId&&N.role!=="admin"&&!N.canOpenShifts?N.assignedBranchId:E.length>0?E[0].id:"branch-main");M(at),'
new_wsm_eff = 'const at=isRestricted?userBranch:(r?.id||(E.length>0?E[0].id:userBranch));M(at),'

if old_wsm_eff in code:
    code = code.replace(old_wsm_eff, new_wsm_eff, 1)
    print("1.2 WorkShiftModal open effect patched")
else:
    print("1.2 old_wsm_eff not found directly")

# In WorkShiftModal branch selector rendering condition:
old_wsm_cond = 'V&&N.assignedBranchId&&N.role!=="admin"&&!Ve?'
new_wsm_cond = 'isRestricted?'

if old_wsm_cond in code:
    code = code.replace(old_wsm_cond, new_wsm_cond, 1)
    print("1.3 WorkShiftModal branch selector locked for non-admin")
else:
    print("1.3 old_wsm_cond not found directly")


# ---------------------------------------------------------------------------
# 2. IPVSheetView (NAe): Strict branch locking and direct branch_inventory query
# ---------------------------------------------------------------------------
# In NAe initialization:
old_nae_init = 'const I=m||$l,M=h||{usdRateCUP:350,lastUpdated:"2026-08-18",autoConvertCosts:!0,history:[]},P=f?.symbol||"$",z=I.role==="kitchen"||I.role==="clerk";I.role==="admin"||I.role?.toLowerCase();const F=S.useMemo(()=>e.filter(Vt=>Vt.active!==!1),[e]),[R,X]=S.useState(()=>z&&I.assignedBranchId?I.assignedBranchId:F[0]?.id||e[0]?.id||"branch-vedado");S.useEffect(()=>{z&&I.assignedBranchId&&X(I.assignedBranchId)},[z,I.assignedBranchId]);'

new_nae_init = 'const I=m||$l,isRestricted=(I.role||"").toLowerCase()!=="admin",userBranch=I.branch_id||I.assignedBranchId||"branch-1792458194300-3i4l",M=h||{usdRateCUP:350,lastUpdated:"2026-08-18",autoConvertCosts:!0,history:[]},P=f?.symbol||"$",z=isRestricted,F=S.useMemo(()=>e.filter(Vt=>Vt.active!==!1),[e]),[R,X]=S.useState(()=>isRestricted?userBranch:(I.assignedBranchId||F[0]?.id||e[0]?.id||userBranch));S.useEffect(()=>{isRestricted&&X(userBranch)},[isRestricted,userBranch]);'

if old_nae_init in code:
    code = code.replace(old_nae_init, new_nae_init, 1)
    print("2.1 NAe branch initialization patched")
else:
    print("2.1 old_nae_init not found directly")

# In NAe IPV draft loading effect: replace with Supabase branch_inventory query
old_nae_draft_eff = 'S.useEffect(()=>{const Vt=`contaresto_ipv_draft_${R}_${L}_${U}`,pn=localStorage.getItem(Vt);if(pn)try{const Rn=JSON.parse(pn);if(Array.isArray(Rn)&&Rn.length>0){Se(Rn);return}}catch(Rn){console.error("Error loading IPV draft:",Rn)}Se(ct(R))},[R,L,U]);'

new_nae_draft_eff = '''S.useEffect(()=>{let mounted=!0;const loadInv=async()=>{const branchToQuery=(I.role||"").toLowerCase()==="admin"?R:(I.branch_id||I.assignedBranchId||"branch-1792458194300-3i4l");try{if(En()){const sClient=Sn();const{data:bItems,error:bErr}=await sClient.from("branch_inventory").select("id, current_stock, min_stock, item_id, inventory:item_id (id, name, unit, category, selling_price_cup)").eq("branch_id",branchToQuery);if(!bErr&&Array.isArray(bItems)&&bItems.length>0&&mounted){const rows=bItems.map(item=>{const inv=item.inventory||{};const name=inv.name||`Producto ${item.item_id}`;const currentStock=Number(item.current_stock||0);const price=Number(inv.selling_price_cup||100);const unit=inv.unit||"uds";const cat=inv.category||"General";return{id:`row-bi-${item.id||item.item_id}`,productId:item.item_id,productType:"sealed_canned",name:name,category:cat,unit:unit,inicio:currentStock,entrada:0,disponible:currentStock,traslado:0,rotura:0,aLaVenta:currentStock,final:currentStock,cantidadVendida:0,precio:price,importe:0,costPerUnit:0,isElaboration:!1,consumedByElaborations:0};});Se(rows);return;}}}catch(err){console.warn("[IPVSheetView] Error loading branch_inventory:",err);}if(mounted){const draftKey=`contaresto_ipv_draft_${R}_${L}_${U}`;const draft=localStorage.getItem(draftKey);if(draft){try{const parsed=JSON.parse(draft);if(Array.isArray(parsed)&&parsed.length>0){Se(parsed);return;}}catch{}}Se(ct(R));}};loadInv();return()=>{mounted=!1;};},[R,L,U,I]);'''

if old_nae_draft_eff in code:
    code = code.replace(old_nae_draft_eff, new_nae_draft_eff, 1)
    print("2.2 NAe branch_inventory Supabase query effect patched")
else:
    print("2.2 old_nae_draft_eff not found directly")

# In NAe branch selector rendering condition:
old_nae_sel_cond = 'z&&I.assignedBranchId?n.jsxDEV("div",{className:"w-full bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/60 rounded-xl px-3 py-2 text-xs font-bold text-blue-900 dark:text-blue-200 flex items-center justify-between",children:[n.jsxDEV("span",{children:e.find(Vt=>Vt.id===I.assignedBranchId)?.name||"Sede Asignada"}'
new_nae_sel_cond = 'isRestricted?n.jsxDEV("div",{className:"w-full bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/60 rounded-xl px-3 py-2 text-xs font-bold text-blue-900 dark:text-blue-200 flex items-center justify-between",children:[n.jsxDEV("span",{children:e.find(Vt=>Vt.id===userBranch)?.name||"Cafeteria Calle A"}'

if old_nae_sel_cond in code:
    code = code.replace(old_nae_sel_cond, new_nae_sel_cond, 1)
    print("2.3 NAe branch selector condition locked for non-admin")
else:
    print("2.3 old_nae_sel_cond not found directly")


# ---------------------------------------------------------------------------
# 3. Unblock Stock / Inventory View for Cashiers and Clerks
# ---------------------------------------------------------------------------
# In App.tsx: opViews check
old_op_views = 'const opViews=["pos","kitchen-kds","cash-register","ipv-sheet"];if(!opViews.includes(a)){r("pos")}'
new_op_views = 'const opViews=["pos","inventory","stock","kitchen-kds","cash-register","ipv-sheet","tables","orders"];if(!opViews.includes(a)){r("pos")}'

if old_op_views in code:
    code = code.replace(old_op_views, new_op_views, 1)
    print("3.1 App.tsx opViews includes inventory/stock")
else:
    print("3.1 old_op_views not found directly")

# In RightSideMenu: allow inventory for cajero, dependiente, clerk
old_rsm_inv = 'allowedRoles:["admin","manager"]},{id:"inventory",viewId:"inventory"'
new_rsm_inv = 'allowedRoles:["admin","manager","cajero","dependiente","clerk","kitchen"]},{id:"inventory",viewId:"inventory"'

if old_rsm_inv in code:
    code = code.replace(old_rsm_inv, new_rsm_inv, 1)
    print("3.2 RightSideMenu inventory view allowedRoles expanded")
else:
    print("3.2 old_rsm_inv not found directly")

# In App.tsx role redirect check:
old_role_chk = '=="kitchen"||u.role==="clerk")&&(["pos","inventory","kitchen-kds","ipv-sheet","cash-register"].includes(a)||r(u.role==="kitchen"?"kitchen-kds":"pos"))'
new_role_chk = '=="kitchen"||u.role==="clerk"||u.role==="cajero"||u.role==="dependiente")&&(["pos","inventory","stock","kitchen-kds","ipv-sheet","cash-register"].includes(a)||r(u.role==="kitchen"?"kitchen-kds":"pos"))'

if old_role_chk in code:
    code = code.replace(old_role_chk, new_role_chk, 1)
    print("3.3 App.tsx role redirect check updated")
else:
    print("3.3 old_role_chk not found directly")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All patches finished successfully!")
