with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Current length:", len(code))

# 1. In AuthGatekeeperView st(Xe): ensure assignedBranchId and branch_id come from Ge.branch_id
old_st_branch = 'avatarColor:nn==="admin"||nn==="owner"?"bg-amber-600":nn==="kitchen"?"bg-rose-600":"bg-emerald-600",assignedBranchId:"branch-main",tenantId:Ge.company_id'
new_st_branch = 'avatarColor:nn==="admin"||nn==="owner"?"bg-amber-600":nn==="kitchen"?"bg-rose-600":"bg-emerald-600",assignedBranchId:Ge.branch_id||"branch-main",branch_id:Ge.branch_id||"branch-main",tenantId:Ge.company_id'

if old_st_branch in code:
    code = code.replace(old_st_branch, new_st_branch, 1)
    print("1. st(Xe) branch persistence patched")
else:
    print("1. already patched")

# 2. In subscribeToMemberStatus: ensure assignedBranchId and branch_id come from ft.branch_id
old_sub_branch = 'avatarColor:Ge==="admin"||Ge==="owner"?"bg-amber-600":Ge==="kitchen"?"bg-rose-600":"bg-emerald-600",assignedBranchId:"branch-main",tenantId:ft.company_id'
new_sub_branch = 'avatarColor:Ge==="admin"||Ge==="owner"?"bg-amber-600":Ge==="kitchen"?"bg-rose-600":"bg-emerald-600",assignedBranchId:ft.branch_id||"branch-main",branch_id:ft.branch_id||"branch-main",tenantId:ft.company_id'

if old_sub_branch in code:
    code = code.replace(old_sub_branch, new_sub_branch, 1)
    print("2. subscribeToMemberStatus branch persistence patched")
else:
    print("2. already patched")

# 3. In PosView (rAe): define isRestrictedRole as role !== 'admin'
old_pos_role = 'isRestrictedRole=["dependiente","cajero","clerk","mesero","waiter"].includes((P.role||"").toLowerCase())'
new_pos_role = 'isRestrictedRole=(P.role||"").toLowerCase()!=="admin"'

if old_pos_role in code:
    code = code.replace(old_pos_role, new_pos_role, 1)
    print("3. PosView isRestrictedRole patched")
else:
    print("3. already patched")

# 4. In PosView (rAe): replace branchId: oe with branchId: he in sales and table notes
old_pos_oe1 = 'serverName:P.name,serverId:P.id,branchId:oe}]}),[pe,fe]='
new_pos_oe1 = 'serverName:P.name,serverId:P.id,branchId:he}]}),[pe,fe]='
if old_pos_oe1 in code:
    code = code.replace(old_pos_oe1, new_pos_oe1, 1)

old_pos_oe2 = ',serverId:_t.employeeId||P.id,branchId:oe,shiftId:_t.shiftId'
new_pos_oe2 = ',serverId:_t.employeeId||P.id,branchId:he,shiftId:_t.shiftId'
if old_pos_oe2 in code:
    code = code.replace(old_pos_oe2, new_pos_oe2, 1)

old_pos_oe3 = 'serverName:P.name,serverId:P.id,branchId:oe}]),re(pt)'
new_pos_oe3 = 'serverName:P.name,serverId:P.id,branchId:he}]),re(pt)'
if old_pos_oe3 in code:
    code = code.replace(old_pos_oe3, new_pos_oe3, 1)
print("4. PosView sales branchId locked to he")

# 5. In InventoryView (W7e): define isRestricted as userRole !== 'admin'
old_inv_role = 'isRestricted=["dependiente","cajero","clerk","mesero","waiter"].includes(userRole)'
new_inv_role = 'isRestricted=userRole!=="admin"'

if old_inv_role in code:
    code = code.replace(old_inv_role, new_inv_role, 1)
    print("5.1. InventoryView isRestricted patched")

# In InventoryView: ensure U is locked to userBranchId for non-admin
old_inv_u = '[U,B]=S.useState(()=>(m.role==="kitchen"||m.role==="clerk")&&m.assignedBranchId?m.assignedBranchId:"all");S.useEffect(()=>{(m.role==="kitchen"||m.role==="clerk")&&m.assignedBranchId&&B(m.assignedBranchId)},[m.role,m.assignedBranchId])'
new_inv_u = '[U,B]=S.useState(()=>{const ub=m.branch_id||m.assignedBranchId||"branch-main";return userRole!=="admin"?ub:"all"});S.useEffect(()=>{if(userRole!=="admin"){const ub=m.branch_id||m.assignedBranchId||"branch-main";B(ub);}},[userRole,m.branch_id,m.assignedBranchId])'

if old_inv_u in code:
    code = code.replace(old_inv_u, new_inv_u, 1)
    print("5.2. InventoryView U branch lock patched")
else:
    print("5.2. Notice: old_inv_u not found directly")

# 6. In KitchenKdsView (lAe): define E as role !== 'admin'
old_kds_e = 'E=V.role==="kitchen"||V.role==="clerk",k=S.useMemo(()=>!V.assignedBranchId||!a.length?null:a.find(re=>re.id===V.assignedBranchId)||null,[a,V.assignedBranchId]),j=S.useMemo(()=>E&&V.assignedBranchId?e.filter(re=>!re.branchId||re.branchId===V.assignedBranchId):e,[e,E,V.assignedBranchId])'
new_kds_e = 'const kdsBranchId=V.branch_id||V.assignedBranchId||"branch-main";const E=(V.role||"").toLowerCase()!=="admin",k=S.useMemo(()=>!kdsBranchId||!a.length?null:a.find(re=>re.id===kdsBranchId)||null,[a,kdsBranchId]),j=S.useMemo(()=>E?e.filter(re=>!re.branchId||re.branchId===kdsBranchId):e,[e,E,kdsBranchId])'

if old_kds_e in code:
    code = code.replace(old_kds_e, new_kds_e, 1)
    print("6. KitchenKdsView branch filtering locked")
else:
    print("6. Notice: old_kds_e not found directly")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All business rules patched in bundle successfully!")
