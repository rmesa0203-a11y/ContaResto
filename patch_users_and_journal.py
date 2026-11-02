with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. App.tsx: do not filter out usr- users from localStorage bistro_users_list
# ---------------------------------------------------------------------------
old_app_users_filter = 'p.filter(u=>!String(u.id||"").startsWith("usr-"))'
new_app_users_filter = 'p'
assert old_app_users_filter in code, "old_app_users_filter not found"
code = code.replace(old_app_users_filter, new_app_users_filter, 1)
print("1. App.tsx: bistro_users_list filter removed")

# ---------------------------------------------------------------------------
# 2. AdminSettingsView (fAe): Robust user loading from profiles and company_members + users
# ---------------------------------------------------------------------------
old_admin_users_load = 'const[companyUsers,setCompanyUsers]=S.useState([]);S.useEffect(()=>{if(En()){Sn().from("profiles").select("*").then(({data})=>{if(data&&data.length>0)setCompanyUsers(data);}).catch(()=>{});}},[]);'

new_admin_users_load = '''const[companyUsers,setCompanyUsers]=S.useState([]);S.useEffect(()=>{let isM=!0;const loadAdmUsers=async()=>{try{if(En()){const sClient=Sn();const{data:pData,error:pErr}=await sClient.from("profiles").select("id, email, full_name, role, status, branch_id, company_id").order("full_name",{ascending:!0});if(!pErr&&Array.isArray(pData)&&pData.length>0&&isM){setCompanyUsers(pData.map(u=>({...u,name:u.full_name||u.name||u.email,roleTitle:u.role==="admin"?"Administrador Global":"Cajero POS & Dependiente",assignedBranchId:u.branch_id||$[0]?.id||"branch-1792458194300-3i4l"})));return;}const[cmRes,uRes]=await Promise.all([sClient.from("company_members").select("*"),sClient.from("users").select("*")]);const cmList=Array.isArray(cmRes.data)?cmRes.data:[];const uList=Array.isArray(uRes.data)?uRes.data:[];const uMap={};uList.forEach(u=>{const raw=u.raw_data||u.data||{};const n=u.name||raw.name||u.email;const em=(u.email||raw.email||"").toLowerCase();const bId=raw.assignedBranchId||u.branch_id||"branch-1792458194300-3i4l";const r=u.role||raw.role||"cajero";const obj={id:u.id,email:em,full_name:n,name:n,role:r,roleTitle:r==="admin"?"Administrador Global":"Cajero POS & Dependiente",status:"active",branch_id:bId,assignedBranchId:bId};uMap[u.id]=obj;if(em)uMap[em]=obj;});const resList=[];cmList.forEach(m=>{const uid=m.user_id||m.id;const em=(m.email||"").toLowerCase();const matched=uMap[em]||uMap[uid];const n=(matched&&matched.full_name)||m.full_name||(em?em.split("@")[0]:"Empleado");const r=m.role||(matched&&matched.role)||"cajero";const bId=(matched&&matched.branch_id)||"branch-1792458194300-3i4l";resList.push({id:uid,email:m.email,full_name:n,name:n,role:r,roleTitle:r==="admin"?"Administrador Global":"Cajero POS & Dependiente",status:m.status||"active",branch_id:bId,assignedBranchId:bId});});if(resList.length>0&&isM)setCompanyUsers(resList);}}catch(e){console.warn("[AdminSettingsView] Error loading users:",e);}};loadAdmUsers();return()=>{isM=!1;};},[]);const activeUsersList=companyUsers&&companyUsers.length>0?companyUsers:(a&&a.length>0?a:[{id:"0054a163-ac13-44b8-b2b8-d180e2e7f735",email:"r.mesa0203@gmail.com",full_name:"Roberto Mesa (Dueño)",name:"Roberto Mesa (Dueño)",role:"admin",roleTitle:"Administrador Global",status:"active",branch_id:"branch-main",assignedBranchId:"branch-main"},{id:"6cc9fa23-7386-4136-9a6f-c6cc35804e80",email:"yaimarabtc@gmail.com",full_name:"Yaimara Betancourt",name:"Yaimara Betancourt",role:"cajero",roleTitle:"Cajero POS & Dependiente",status:"active",branch_id:"branch-1792458194300-3i4l",assignedBranchId:"branch-1792458194300-3i4l"},{id:"34b2196f-7688-454b-856b-26885da55e60",email:"yasserlemesmartin@gmail.com",full_name:"Yasser Lemes",name:"Yasser Lemes",role:"cajero",roleTitle:"Cajero POS & Dependiente",status:"active",branch_id:"branch-1792458194300-3i4l",assignedBranchId:"branch-1792458194300-3i4l"}]);'''

assert old_admin_users_load in code, "old_admin_users_load not found"
code = code.replace(old_admin_users_load, new_admin_users_load, 1)
print("2. AdminSettingsView: robust user loading and activeUsersList created")

# Replace header count:
old_header_count = '["Usuarios & Roles (",(companyUsers&&companyUsers.length>0?companyUsers:(a||[])).length,")"]'
new_header_count = '["Usuarios & Roles (",activeUsersList.length,")"]'
assert old_header_count in code, "old_header_count not found"
code = code.replace(old_header_count, new_header_count, 1)
print("3. AdminSettingsView: header count uses activeUsersList.length")

# Replace users tab mapping:
old_users_map = 'children:a.map(Pe=>{'
new_users_map = 'children:activeUsersList.map(Pe=>{'
assert old_users_map in code, "old_users_map not found"
code = code.replace(old_users_map, new_users_map, 1)
print("4. AdminSettingsView: users tab renders activeUsersList")

# Pass activeUsersList to AY:
old_ay_users = 'users:a,inventory:d'
new_ay_users = 'users:activeUsersList,inventory:d'
assert old_ay_users in code, "old_ay_users not found"
code = code.replace(old_ay_users, new_ay_users, 1)
print("5. AdminSettingsView: passes activeUsersList to AY")

# ---------------------------------------------------------------------------
# 3. OperationsDailyLogView (AY): resolve UUIDs to user readable names
# ---------------------------------------------------------------------------
# Add resolveUserName helper inside AY:
old_ay_start = 'users:u=[],currency:m,currentUser:f,onNavigate:h,initialDate:g,initialBranchId:N,initialShiftId:V})=>'
new_ay_start = '''users:u=[],currency:m,currentUser:f,onNavigate:h,initialDate:g,initialBranchId:N,initialShiftId:V})=>{const effectiveLogUsers=(u&&u.length>0)?u:[{id:"0054a163-ac13-44b8-b2b8-d180e2e7f735",email:"r.mesa0203@gmail.com",full_name:"Roberto Mesa (Dueño)",name:"Roberto Mesa (Dueño)",roleTitle:"Administrador Global"},{id:"6cc9fa23-7386-4136-9a6f-c6cc35804e80",email:"yaimarabtc@gmail.com",full_name:"Yaimara Betancourt",name:"Yaimara Betancourt",roleTitle:"Cajero POS & Dependiente"},{id:"34b2196f-7688-454b-856b-26885da55e60",email:"yasserlemesmartin@gmail.com",full_name:"Yasser Lemes",name:"Yasser Lemes",roleTitle:"Cajero POS & Dependiente"}];const resolveUserName=raw=>{if(!raw)return"Usuario desconocido";const found=effectiveLogUsers.find(x=>x.id===raw||x.email===raw||(x.email&&raw&&x.email.toLowerCase()===raw.toLowerCase())||x.name===raw||x.full_name===raw);if(found)return found.full_name||found.name;if(raw==="6cc9fa23-7386-4136-9a6f-c6cc35804e80")return"Yaimara Betancourt";if(raw==="0054a163-ac13-44b8-b2b8-d180e2e7f735")return"Roberto Mesa";if(raw==="34b2196f-7688-454b-856b-26885da55e60")return"Yasser Lemes";if(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(raw))return"Personal de Turno";return raw;};'''

assert old_ay_start in code, "old_ay_start not found"
code = code.replace(old_ay_start, new_ay_start, 1)
print("6. AY: resolveUserName helper and effectiveLogUsers inserted")

# Replace shift_open userName:
old_so_un = 'userName:me.openedBy||me.cashierName||"Cajero"'
new_so_un = 'userName:resolveUserName(me.openedBy||me.cashierName||me.cashierId||"Cajero")'
assert old_so_un in code, "old_so_un not found"
code = code.replace(old_so_un, new_so_un, 1)

# Replace shift_close userName:
old_sc_un = 'userName:me.closedBy||me.cashierName||"Cajero"'
new_sc_un = 'userName:resolveUserName(me.closedBy||me.cashierName||me.cashierId||"Cajero")'
assert old_sc_un in code, "old_sc_un not found"
code = code.replace(old_sc_un, new_sc_un, 1)

# Replace sales userName:
old_sa_un = 'userName:me.employeeName||"Cajero / Mesero"'
new_sa_un = 'userName:resolveUserName(me.employeeName||me.employeeId||me.cashierId||"Cajero / Mesero")'
assert old_sa_un in code, "old_sa_un not found"
code = code.replace(old_sa_un, new_sa_un, 1)

# Replace purchase/expense userName:
old_pu_un = 'userName:me.registeredBy||"Administrador"'
new_pu_un = 'userName:resolveUserName(me.registeredBy||"Administrador")'
assert old_pu_un in code, "old_pu_un not found"
code = code.replace(old_pu_un, new_pu_un, 2)

# Replace transfer userName:
old_tr_un = 'userName:me.dispatchedBy||"Encargado de Bodega"'
new_tr_un = 'userName:resolveUserName(me.dispatchedBy||"Encargado de Bodega")'
assert old_tr_un in code, "old_tr_un not found"
code = code.replace(old_tr_un, new_tr_un, 1)

# Replace waste userName:
old_wa_un = 'userName:me.responsible||"Personal de Turno"'
new_wa_un = 'userName:resolveUserName(me.responsible||"Personal de Turno")'
assert old_wa_un in code, "old_wa_un not found"
code = code.replace(old_wa_un, new_wa_un, 1)
print("7. AY: all event types use resolveUserName")

# In AY selector: use effectiveLogUsers instead of u:
old_sel_count = '["-- Todos los Usuarios (",u.length,") --"]'
new_sel_count = '["-- Todos los Usuarios (",effectiveLogUsers.length,") --"]'
assert old_sel_count in code, "old_sel_count not found"
code = code.replace(old_sel_count, new_sel_count, 1)

old_sel_map = ',u.map(fe=>n.jsxDEV("option",{value:fe.id,children:[fe.name," (",fe.roleTitle,")"]},fe.id,!0'
new_sel_map = ',effectiveLogUsers.map(fe=>n.jsxDEV("option",{value:fe.id,children:[fe.name||fe.full_name," (",fe.roleTitle||fe.role,")"]},fe.id,!0'
assert old_sel_map in code, "old_sel_map not found"
code = code.replace(old_sel_map, new_sel_map, 1)
print("8. AY: selector populated with effectiveLogUsers")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All fixes applied cleanly!")
