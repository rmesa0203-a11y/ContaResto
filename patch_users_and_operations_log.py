with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. App.tsx: Do not filter out usr- from bistro_users_list
# ---------------------------------------------------------------------------
old_app_m = '[m,f]=S.useState(()=>{if(typeof localStorage==="undefined")return[];try{const be=localStorage.getItem("bistro_users_list");if(!be)return[];const p=JSON.parse(be);return Array.isArray(p)?p.filter(u=>!String(u.id||"").startsWith("usr-")):[]}catch{return[]}})'

new_app_m = '[m,f]=S.useState(()=>{if(typeof localStorage==="undefined")return[];try{const be=localStorage.getItem("bistro_users_list");if(!be)return[];const p=JSON.parse(be);return Array.isArray(p)?p:[]}catch{return[]}})'

assert old_app_m in code, "old_app_m not found"
code = code.replace(old_app_m, new_app_m, 1)
print("1. App.tsx m state filter removed")


# ---------------------------------------------------------------------------
# 2. AdminSettingsView (fAe): Load profiles with fallback to company_members + users
# ---------------------------------------------------------------------------
old_fAe_load = 'const[companyUsers,setCompanyUsers]=S.useState([]);S.useEffect(()=>{if(En()){Sn().from("profiles").select("*").then(({data})=>{if(data&&data.length>0)setCompanyUsers(data);}).catch(()=>{});}},[]);'

new_fAe_load = '''const[companyUsers,setCompanyUsers]=S.useState([]);S.useEffect(()=>{let mounted=!0;const loadUsers=async()=>{if(!En())return;try{const sClient=Sn();let list=[];try{const{data:pUsers,error:pErr}=await sClient.from("profiles").select("id, email, full_name, role, status, branch_id, company_id").order("full_name",{ascending:!0});if(!pErr&&Array.isArray(pUsers)&&pUsers.length>0){list=pUsers;}}catch(e){}if(!list||list.length===0){try{const{data:cmData}=await sClient.from("company_members").select("*");const{data:uData}=await sClient.from("users").select("*");const uMap={};if(Array.isArray(uData)){uData.forEach(u=>{const raw=u.raw_data||{};const name=u.name||raw.name||(u.email?u.email.split("@")[0]:"");if(u.id)uMap[u.id]={...u,name,full_name:name,branch_id:raw.assignedBranchId||u.branch_id};if(u.email)uMap[u.email.toLowerCase()]={...u,name,full_name:name,branch_id:raw.assignedBranchId||u.branch_id};});}if(Array.isArray(cmData)&&cmData.length>0){list=cmData.map(m=>{const uid=m.user_id||m.id;const em=(m.email||"").toLowerCase();const matched=uMap[em]||uMap[uid];const name=matched?.full_name||matched?.name||(em?em.split("@")[0]:"Usuario");const role=m.role||matched?.role||"cajero";const bId=matched?.branch_id||"branch-1792458194300-3i4l";return{id:uid,email:m.email,full_name:name,name:name,role:role,roleTitle:role==="admin"?"Administrador":role==="kitchen"?"Cocina KDS":"Cajero POS & Dependiente",status:m.status||"active",branch_id:bId,assignedBranchId:bId,company_id:m.company_id||"biz-main"};});}}catch(e){}}if(mounted&&Array.isArray(list)&&list.length>0){setCompanyUsers(list);if(typeof r==="function")r(list);try{localStorage.setItem("bistro_users_list",JSON.stringify(list));}catch{}}}catch(e){console.warn("[AdminSettingsView] Error loading users:",e);}};loadUsers();return()=>{mounted=!1;};},[]);const effectiveUsers=companyUsers&&companyUsers.length>0?companyUsers:(a&&a.length>0?a:[]);'''

assert old_fAe_load in code, "old_fAe_load not found"
code = code.replace(old_fAe_load, new_fAe_load, 1)
print("2. AdminSettingsView user loading and effectiveUsers patched")


# In AdminSettingsView tab badge: use effectiveUsers.length
old_fAe_tab_badge = '["Usuarios & Roles (",(companyUsers&&companyUsers.length>0?companyUsers:(a||[])).length,")"]'
new_fAe_tab_badge = '["Usuarios & Roles (",effectiveUsers.length,")"]'

assert old_fAe_tab_badge in code, "old_fAe_tab_badge not found"
code = code.replace(old_fAe_tab_badge, new_fAe_tab_badge, 1)
print("3. AdminSettingsView tab badge count patched")


# In AdminSettingsView users tab content: map effectiveUsers instead of a
old_fAe_users_map = ':grid-cols-3 gap-4",children:a.map(Pe=>{'
new_fAe_users_map = ':grid-cols-3 gap-4",children:effectiveUsers.map(Pe=>{'

assert old_fAe_users_map in code, "old_fAe_users_map not found"
code = code.replace(old_fAe_users_map, new_fAe_users_map, 1)
print("4. AdminSettingsView users tab maps effectiveUsers")


# In AdminSettingsView render of AY: pass users: effectiveUsers
old_fAe_ay_render = 'ae==="operations_log"&&n.jsxDEV(AY,{workShifts:j,sales:I,expenses:M,invoices:P,wasteLogs:z,transfers:F,cashClosings:R,branches:$,users:a,'
new_fAe_ay_render = 'ae==="operations_log"&&n.jsxDEV(AY,{workShifts:j,sales:I,expenses:M,invoices:P,wasteLogs:z,transfers:F,cashClosings:R,branches:$,users:effectiveUsers,'

assert old_fAe_ay_render in code, "old_fAe_ay_render not found"
code = code.replace(old_fAe_ay_render, new_fAe_ay_render, 1)
print("5. AdminSettingsView passes effectiveUsers to AY")


# ---------------------------------------------------------------------------
# 3. OperationsDailyLogView (AY): Resolve UUIDs to readable user names
# ---------------------------------------------------------------------------
# Inside AY, define usersMap and resolveUserName helper right at the top
old_ay_head = ',AY=({workShifts:e=[],sales:t=[],expenses:a=[],invoices:r=[],wasteLogs:s=[],transfers:i=[],cashClosings:l=[],branches:d=[],users:u=[],currency:m,currentUser:f,onNavigate:h,initialDate:g,initialBranchId:N,initialShiftId:V})=>{'

new_ay_head = ''',AY=({workShifts:e=[],sales:t=[],expenses:a=[],invoices:r=[],wasteLogs:s=[],transfers:i=[],cashClosings:l=[],branches:d=[],users:u=[],currency:m,currentUser:f,onNavigate:h,initialDate:g,initialBranchId:N,initialShiftId:V})=>{const usersMap=S.useMemo(()=>{const mp={};(u||[]).forEach(usr=>{if(usr.id){mp[usr.id]=usr;mp[String(usr.id).toLowerCase()]=usr;}if(usr.user_id){mp[usr.user_id]=usr;mp[String(usr.user_id).toLowerCase()]=usr;}if(usr.email){mp[usr.email.toLowerCase()]=usr;}});return mp;},[u]);const resolveName=(uid,fallback)=>{const usr=usersMap[uid]||usersMap[fallback];if(usr&&(usr.full_name||usr.name))return usr.full_name||usr.name;if(fallback&&!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(fallback))return fallback;if(uid&&!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(uid))return uid;return usr?.email?usr.email.split("@")[0]:"Cajero Asignado";};'''

assert old_ay_head in code, "old_ay_head not found"
code = code.replace(old_ay_head, new_ay_head, 1)
print("6. OperationsDailyLogView usersMap and resolveName helper inserted")


# In AY shift_open event generation:
old_ay_open = 'userId:me.cashierId,userName:me.openedBy||me.cashierName||"Cajero",title:`Apertura de Turno:'
new_ay_open = 'userId:me.cashierId,userName:resolveName(me.cashierId,me.openedBy||me.cashierName),title:`Apertura de Turno:'

assert old_ay_open in code, "old_ay_open not found"
code = code.replace(old_ay_open, new_ay_open, 1)
print("7. AY shift_open userName uses resolveName")


# In AY shift_close event generation:
old_ay_close = 'userId:me.cashierId,userName:me.closedBy||me.cashierName||"Cajero",title:`Cierre y Arqueo:'
new_ay_close = 'userId:me.cashierId,userName:resolveName(me.cashierId,me.closedBy||me.cashierName),title:`Cierre y Arqueo:'

assert old_ay_close in code, "old_ay_close not found"
code = code.replace(old_ay_close, new_ay_close, 1)
print("8. AY shift_close userName uses resolveName")


# In AY sales event generation:
old_ay_sale = 'userId:me.employeeId,userName:me.employeeName||"Cajero / Mesero",title:`${lt?"⏳ N'
new_ay_sale = 'userId:me.employeeId,userName:resolveName(me.employeeId,me.employeeName||me.cashierName),title:`${lt?"⏳ N'

assert old_ay_sale in code, "old_ay_sale not found"
code = code.replace(old_ay_sale, new_ay_sale, 1)
print("9. AY sales userName uses resolveName")


# In AY expenses event generation:
old_ay_exp = 'shiftName:"General",userName:me.registeredBy||"Administrador",title:`Extracción '
new_ay_exp = 'shiftName:"General",userName:resolveName(me.userId,me.registeredBy||"Administrador"),title:`Extracción '

assert old_ay_exp in code, "old_ay_exp not found"
code = code.replace(old_ay_exp, new_ay_exp, 1)
print("10. AY expenses userName uses resolveName")


# In AY filter option list: display full_name or name
old_ay_opt = 'u.map(fe=>n.jsxDEV("option",{value:fe.id,children:[fe.name," (",fe.roleTitle,")"]},fe.id,!0,'
new_ay_opt = 'u.map(fe=>n.jsxDEV("option",{value:fe.id,children:[fe.full_name||fe.name||fe.email," (",fe.roleTitle||fe.role,")"]},fe.id,!0,'

assert old_ay_opt in code, "old_ay_opt not found"
code = code.replace(old_ay_opt, new_ay_opt, 1)
print("11. AY filter option labels display full_name")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All patches for Users & Roles and Libro Diario applied successfully!")
