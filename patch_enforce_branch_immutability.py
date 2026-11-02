with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# 1. In getMemberForUser: default branch_id to branch-1792458194300-3i4l instead of branch-main
old_gm_branch = 'branch_id:p.branch_id||"branch-main"'
new_gm_branch = 'branch_id:p.branch_id||"branch-1792458194300-3i4l"'

if old_gm_branch in code:
    code = code.replace(old_gm_branch, new_gm_branch)
    print("1. getMemberForUser branch fallback patched")
else:
    print("1. old_gm_branch not found")

# 2. In st(Xe) (login handler): ensure assignedBranchId and branch_id take Ge.branch_id
old_st_branch = 'assignedBranchId:Ge.branch_id||"branch-main",branch_id:Ge.branch_id||"branch-main"'
new_st_branch = 'assignedBranchId:Ge.branch_id||"branch-1792458194300-3i4l",branch_id:Ge.branch_id||"branch-1792458194300-3i4l"'

if old_st_branch in code:
    code = code.replace(old_st_branch, new_st_branch, 1)
    print("2. st login handler branch fallback patched")
else:
    print("2. old_st_branch not found")

# Also in st(Xe), store active_branch_id and selected_branch_id to localStorage on login
old_st_set = 'Zt.setTenantId(Ge.company_id),e(on,Ge.company_id,Dt?.name||Ge.company_name);return}'
new_st_set = 'Zt.setTenantId(Ge.company_id);if(nn!=="admin"&&on.branch_id){localStorage.setItem("active_branch_id",on.branch_id);localStorage.setItem("selected_branch_id",on.branch_id);localStorage.setItem("bistro_active_branch",on.branch_id);}e(on,Ge.company_id,Dt?.name||Ge.company_name);return}'

if old_st_set in code:
    code = code.replace(old_st_set, new_st_set, 1)
    print("2.1 st login localStorage branch sync patched")
else:
    print("2.1 old_st_set not found")

# 3. In App.tsx: when user (l) loads, enforce selected_branch_id and active_branch_id
old_app_l_eff = 'S.useEffect(()=>{if(l){localStorage.setItem("bistro_user",JSON.stringify(l));const ab=l.branch_id||l.assignedBranchId;if(ab){localStorage.setItem("active_branch_id",ab);localStorage.setItem("bistro_active_branch",ab);g(Kn=>({...Kn,activeBranchId:ab}));}}else{localStorage.removeItem("bistro_user");}},[l])'

new_app_l_eff = 'S.useEffect(()=>{if(l){localStorage.setItem("bistro_user",JSON.stringify(l));const isNotAdmin=(l.role||"").toLowerCase()!=="admin";const ab=l.branch_id||l.assignedBranchId;if(isNotAdmin&&ab){localStorage.setItem("active_branch_id",ab);localStorage.setItem("selected_branch_id",ab);localStorage.setItem("bistro_active_branch",ab);g(Kn=>({...Kn,activeBranchId:ab}));}}else{localStorage.removeItem("bistro_user");}},[l])'

if old_app_l_eff in code:
    code = code.replace(old_app_l_eff, new_app_l_eff, 1)
    print("3. App.tsx l effect branch sync patched")
else:
    print("3. old_app_l_eff not found")

# 4. In PosView.tsx:
# Replace ge.length>0&&!ge.some(we=>we.id===oe)&&Ee(ge[0].id) so it does NOT overwrite for non-admins
old_pos_eff = 'S.useEffect(()=>{ge.length>0&&!ge.some(we=>we.id===oe)&&Ee(ge[0].id)},[ge,oe])'
new_pos_eff = 'S.useEffect(()=>{const isEmp=(P.role||"").toLowerCase()!=="admin";if(!isEmp&&ge.length>0&&!ge.some(we=>we.id===oe)){Ee(ge[0].id)}},[ge,oe,P.role])'

if old_pos_eff in code:
    code = code.replace(old_pos_eff, new_pos_eff, 1)
    print("4.1 PosView ge[0] overwrite prevented for non-admin")
else:
    print("4.1 old_pos_eff not found")

# In PosView.tsx: ensure userBranchId sync effect checks P.branch_id
old_pos_user_eff = 'S.useEffect(()=>{!(P.role==="admin"||P.role?.toLowerCase()==="admin"||(P.roleTitle||"").toLowerCase().includes("admin"))&&P.assignedBranchId&&Ee(P.assignedBranchId)},[P.assignedBranchId,P.role,P.roleTitle])'
new_pos_user_eff = 'S.useEffect(()=>{const isEmp=(P.role||"").toLowerCase()!=="admin";const bId=P.branch_id||P.assignedBranchId;if(isEmp&&bId){Ee(bId);localStorage.setItem("active_branch_id",bId);localStorage.setItem("selected_branch_id",bId);}},[P.branch_id,P.assignedBranchId,P.role,P.roleTitle])'

if old_pos_user_eff in code:
    code = code.replace(old_pos_user_eff, new_pos_user_eff, 1)
    print("4.2 PosView user branch sync effect patched")
else:
    print("4.2 old_pos_user_eff not found")

# In PosView.tsx: replace userBranchId fallback
old_pos_user_bid = 'const userBranchId=P.branch_id||P.assignedBranchId||"branch-main"'
new_pos_user_bid = 'const userBranchId=P.branch_id||P.assignedBranchId||"branch-1792458194300-3i4l"'

if old_pos_user_bid in code:
    code = code.replace(old_pos_user_bid, new_pos_user_bid, 1)
    print("4.3 PosView userBranchId fallback patched")
else:
    print("4.3 old_pos_user_bid not found")

# 5. In CashRegisterView.tsx: ensure r takes user's branch when non-admin
old_cr_r = 'V&&N.assignedBranchId?N.assignedBranchId:d||i[0]?.id'
new_cr_r = '(N.role||"").toLowerCase()!=="admin"?N.branch_id||N.assignedBranchId||"branch-1792458194300-3i4l":d||i[0]?.id'

if old_cr_r in code:
    code = code.replace(old_cr_r, new_cr_r)
    print("5. CashRegisterView r branch calculation patched")
else:
    print("5. old_cr_r not found")

# 6. In WorkShiftModal.tsx: ensure effect does not reset to E[0].id when isRestricted
old_wsm_e0 = 'E.length>0&&I&&!E.some(at=>at.id===I)&&M(E[0].id)'
new_wsm_e0 = '!isRestricted&&E.length>0&&I&&!E.some(at=>at.id===I)&&M(E[0].id)'

if old_wsm_e0 in code:
    code = code.replace(old_wsm_e0, new_wsm_e0, 1)
    print("6. WorkShiftModal E[0] overwrite prevented for isRestricted")
else:
    print("6. old_wsm_e0 not found")

# 7. In Navbar.tsx: show assigned branch badge for ANY non-admin role
old_nav_cond = 'q&&xe&&n.jsxDEV("div",{className:"hidden lg:flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800'
new_nav_cond = '(W.role||"").toLowerCase()!=="admin"&&n.jsxDEV("div",{className:"hidden lg:flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-950/40 border border-emerald-500/40 text-emerald-400'

if old_nav_cond in code:
    code = code.replace(old_nav_cond, new_nav_cond, 1)
    print("7. Navbar non-admin branch badge patched")
else:
    print("7. old_nav_cond not found")

# Also in Navbar.tsx: branch label in the badge
old_nav_name = 'xe.name'
# Look around line 822329
pos_nb = code.find('Navbar.tsx', 812000)
pos_xe_name = code.find('xe.name', pos_nb)
if pos_xe_name != -1 and pos_xe_name < pos_nb + 15000:
    code = code[:pos_xe_name] + '((P||[]).find(b=>b.id===(W.branch_id||W.assignedBranchId))?.name||"Cafeteria Calle A")' + code[pos_xe_name+7:]
    print("7.1 Navbar branch name resolution patched")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch script completed successfully!")
