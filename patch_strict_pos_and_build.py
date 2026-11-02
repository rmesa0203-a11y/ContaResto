with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Current bundle length:", len(code))

# 1. PosView branch selector: STRICTLY P.role === "admin"
old_pos_cond = '!De&&P.assignedBranchId&&!ye?'
new_pos_cond = 'P.role!=="admin"?'

if old_pos_cond in code:
    code = code.replace(old_pos_cond, new_pos_cond, 1)
    print("1. PosView branch selector condition patched to P.role !== 'admin'")
else:
    print("1. old_pos_cond not found directly, checking...")

# Also update the badge text in PosView to match prompt: "Sucursal: {P.branch_name || ee?.name || 'Asignada'}"
old_badge = 'children:[ee?.name||"Sede Asignada",n.jsxDEV("span",{className:"text-[10px] bg-blue-200/60 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 px-1 py-0.2 rounded font-bold",children:"🔒 Asignada"}'
new_badge = 'className:"current-branch-badge font-bold text-xs text-blue-700 dark:text-blue-300 flex items-center gap-1.5",children:[`Sucursal: ${P.branch_name||ee?.name||"Asignada"}`,n.jsxDEV("span",{className:"text-[10px] bg-blue-200/60 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 px-1.5 py-0.5 rounded font-bold",children:"🔒 Fija"}'

if old_badge in code:
    code = code.replace(old_badge, new_badge, 1)
    print("1.1. PosView branch badge styled and updated")
else:
    print("1.1. Notice: old_badge not found directly")

# 2. In App.tsx: Add automatic route protection and redirection to /pos for non-admin
# Find S.useEffect in _Ae
old_app_effect = 'En()&&l&&Zt.pullInitialState()'
new_app_effect = 'if(l&&(l.role||"").toLowerCase()!=="admin"){const opViews=["pos","kitchen-kds","cash-register","ipv-sheet"];if(!opViews.includes(a)){r("pos")}};En()&&l&&Zt.pullInitialState()'

if old_app_effect in code:
    code = code.replace(old_app_effect, new_app_effect, 1)
    print("2. App route redirection for non-admin patched")
else:
    print("2. old_app_effect not found")

# 3. Guard ExecutableExportModal (l7e) in App.tsx with currentUser?.role === 'admin'
old_export_modal = 'n.jsxDEV(l7e,{isOpen:ae,onClose:()=>ge(!1)'
new_export_modal = 'l?.role==="admin"&&n.jsxDEV(l7e,{isOpen:ae,onClose:()=>ge(!1)'

if old_export_modal in code:
    code = code.replace(old_export_modal, new_export_modal, 1)
    print("3. ExecutableExportModal wrapped in admin role check")
else:
    print("3. old_export_modal not found")

# 4. Guard AdminSettingsView in App.tsx: only admin
old_admin_settings = 'a==="admin-settings"&&n.jsxDEV(fAe,'
new_admin_settings = 'a==="admin-settings"&&l?.role==="admin"&&n.jsxDEV(fAe,'

if old_admin_settings in code:
    code = code.replace(old_admin_settings, new_admin_settings, 1)
    print("4. AdminSettingsView guarded with admin role check")
else:
    print("4. old_admin_settings not found")

# 5. Guard UserManagementView in App.tsx: only admin
old_users_view = 'a==="user-management"&&n.jsxDEV(AAe,'
new_users_view = 'a==="user-management"&&l?.role==="admin"&&n.jsxDEV(AAe,'

if old_users_view in code:
    code = code.replace(old_users_view, new_users_view, 1)
    print("5. UserManagementView guarded with admin role check")
else:
    print("5. old_users_view not found")

# 6. Guard APK / Build button in RightSideMenu: only admin
old_rsm_apk = 'category:"sistema",allowedRoles:["admin","manager"],onClick:X}'
new_rsm_apk = 'category:"sistema",allowedRoles:["admin"],onClick:X}'

if old_rsm_apk in code:
    code = code.replace(old_rsm_apk, new_rsm_apk, 1)
    print("6. RightSideMenu APK button restricted exclusively to admin")
else:
    print("6. old_rsm_apk not found")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patching completed successfully!")
