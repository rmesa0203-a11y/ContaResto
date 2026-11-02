import re

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Current bundle size:", len(code))

# =========================================================================
# 1. ELIMINAR LOS MOCKS (Ox = [])
# =========================================================================
# Find Ox=[{id:"usr-admin", ... }]
pos_ox = code.find('totalValueUSD:178.4}],Ox=[{id:"usr-admin"')
if pos_ox != -1:
    pos_ox_start = code.find('Ox=[', pos_ox)
    pos_ox_end = code.find('phone:"+53 5 334 1278",active:!0}]', pos_ox_start) + len('phone:"+53 5 334 1278",active:!0}]')
    code = code[:pos_ox_start] + 'Ox=[]' + code[pos_ox_end:]
    print("Patch 1.1 (Ox mock users array cleared to []): OK")
else:
    print("Patch 1.1 warning: Ox mock array start not matched directly")

# In App.tsx: ensure localStorage bistro_users_list doesn't restore mock users
target_users_init = 'const[m,f]=S.useState(()=>{const be=localStorage.getItem("bistro_users_list");return be?JSON.parse(be):Ox})'
replacement_users_init = 'const[m,f]=S.useState(()=>{if(typeof localStorage==="undefined")return[];try{const be=localStorage.getItem("bistro_users_list");if(!be)return[];const parsed=JSON.parse(be);return Array.isArray(parsed)?parsed.filter(u=>!String(u.id||"").startsWith("usr-")):[]}catch{return[]}})'

if target_users_init in code:
    code = code.replace(target_users_init, replacement_users_init, 1)
    print("Patch 1.2 (m users state sanitized against mock users in localStorage): OK")
else:
    print("Patch 1.2 warning: target_users_init not found directly")

# =========================================================================
# 2. CARGA REAL DESDE PROFILES EN wl.getCompanyMembers
# =========================================================================
target_get_members = 'static async getCompanyMembers(t){if(!En()||!t)return[];try{const a=Sn(),{data:r,error:s}=await a.from("company_members").select("*").eq("company_id",t).order("created_at",{ascending:!1});return s?(console.warn("[SupabaseCompany] Error fetching company members:",s.message),[]):r||[]}catch(a){return console.error("[SupabaseCompany] getCompanyMembers exception:",a),[]}}'

replacement_get_members = '''static async getCompanyMembers(t){if(!En()||!t)return[];try{const a=Sn();const{data:profs}=await a.from("profiles").select("id, email, full_name, role, status, company_id, branch_id, created_at, updated_at").eq("company_id",t).order("created_at",{ascending:!1});const{data:cmList}=await a.from("company_members").select("*").eq("company_id",t).order("created_at",{ascending:!1});const merged=new Map();if(Array.isArray(cmList)){cmList.forEach(m=>{const uid=m.user_id||m.id;merged.set(uid,{...m,id:m.id||uid,user_id:uid,status:m.status==="pending_approval"?"pending":m.status});});}if(Array.isArray(profs)){profs.forEach(p=>{const existing=merged.get(p.id);const email=p.email||existing?.email||(p.full_name?p.full_name.toLowerCase().replace(/[^a-z0-9]/g,"")+"@gmail.com":"colaborador@bistro.com");const st=(p.status==="pending_approval"||p.status==="pending")?"pending":p.status;merged.set(p.id,{id:p.id,user_id:p.id,email:email,full_name:p.full_name||email,name:p.full_name||email,role:p.role||"cajero",status:st,company_id:p.company_id||t,branch_id:p.branch_id||"branch-main",created_at:p.created_at||new Date().toISOString()});});}return Array.from(merged.values());}catch(a){console.error("[SupabaseCompany] getCompanyMembers exception:",a);return[];}}'''

if target_get_members in code:
    code = code.replace(target_get_members, replacement_get_members, 1)
    print("Patch 2 (wl.getCompanyMembers queries profiles and company_members): OK")
else:
    print("Patch 2 warning: target_get_members not found directly")

# =========================================================================
# 3. ACTUALIZAR PROFILES AL APROBAR O RECHAZAR EN wl.updateMemberStatusAndRole
# =========================================================================
# Let's find the current implementation of updateMemberStatusAndRole
pos_update = code.find('static async updateMemberStatusAndRole(')
if pos_update != -1:
    pos_end_fn = code.find('static async removeMember(', pos_update)
    current_fn = code[pos_update:pos_end_fn].strip()
    new_fn = '''static async updateMemberStatusAndRole(t,a,r,b){const s=Sn();const profStatus=(a==="pending"||a==="pending_approval")?"pending_approval":a;const profUpdate={status:profStatus,updated_at:new Date().toISOString()};if(r)profUpdate.role=r;if(b)profUpdate.branch_id=b;const{data:profData,error:profErr}=await s.from("profiles").update(profUpdate).eq("id",t).select().maybeSingle();try{const cmUpdate={status:a};if(r)cmUpdate.role=r;if(b)cmUpdate.branch_id=b;await s.from("company_members").update(cmUpdate).or(`id.eq.${t},user_id.eq.${t}`);}catch(e){}if(profErr){console.warn("[updateMemberStatusAndRole] Notice:",profErr.message);}return profData||{id:t,...profUpdate};}'''
    code = code[:pos_update] + new_fn + '\n' + code[pos_end_fn:]
    print("Patch 3 (wl.updateMemberStatusAndRole updates profiles directly): OK")
else:
    print("Patch 3 warning: pos_update not found")

# =========================================================================
# 4. CARGA DE SUCURSALES Y ASIGNACIÓN EN AAe (UserManagementView)
# =========================================================================
target_aae_init = 'const AAe=({currentUser:e,currentTenantId:t,companyName:a,onLogAudit:r,onPendingCountChange:s})=>'

replacement_aae_init = '''const AAe=({currentUser:e,currentTenantId:t,companyName:a,onLogAudit:r,onPendingCountChange:s,branches:branchesProp=[]})=>{const[companyBranches,setCompanyBranches]=S.useState(branchesProp&&branchesProp.length>0?branchesProp:[]);const[chosenBranch,setChosenBranch]=S.useState({});S.useEffect(()=>{if(En()&&t){Sn().from("branches").select("id, name").or(`company_id.eq.${t},tenant_id.eq.${t}`).eq("is_active",true).then(({data:brs})=>{if(brs&&brs.length>0)setCompanyBranches(brs);else setCompanyBranches([{id:"branch-main",name:"Almacén Central & Matriz"}]);}).catch(()=>{setCompanyBranches([{id:"branch-main",name:"Almacén Central & Matriz"}]);});}},[t]);'''

# In AAe approval function:
target_approve_call = 'try{await wl.updateMemberStatusAndRole(W.id,"active",q,W.branch_id||"branch-main")'
replacement_approve_call = 'try{const assignedBranch=chosenBranch[W.id]||W.branch_id||(companyBranches[0]?.id)||"branch-main";await wl.updateMemberStatusAndRole(W.id,"active",q,assignedBranch)'

if target_approve_call in code:
    code = code.replace(target_approve_call, replacement_approve_call, 1)
    print("Patch 4.1 (AAe approval passes chosenBranch): OK")
else:
    print("Patch 4.1 warning: target_approve_call not found")

if target_aae_init in code:
    code = code.replace(target_aae_init, replacement_aae_init, 1)
    print("Patch 4.2 (AAe state for companyBranches and chosenBranch): OK")
else:
    print("Patch 4.2 warning: target_aae_init not found")

# In AAe pending card: add branch dropdown before approve button
target_btn_container = 'n.jsxDEV("div",{className:"flex items-center gap-2",children:[n.jsxDEV("button",{type:"button",onClick:()=>ae(W),disabled:xe'

replacement_btn_container = '''n.jsxDEV("div",{className:"space-y-1 mb-2.5",children:[n.jsxDEV("label",{className:"text-[10px] font-bold uppercase text-slate-400 block",children:"Sucursal a Asignar:"}),n.jsxDEV("select",{value:chosenBranch[W.id]||W.branch_id||(companyBranches[0]?.id)||"branch-main",onChange:e=>setChosenBranch(prev=>({...prev,[W.id]:e.target.value})),className:"w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-xl text-xs font-semibold text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500",children:(companyBranches||[]).map(b=>n.jsxDEV("option",{value:b.id,children:b.name},b.id,!1,{fileName:"/app/applet/src/components/UserManagementView.tsx",lineNumber:458,columnNumber:29},void 0))},void 0,!1,{fileName:"/app/applet/src/components/UserManagementView.tsx",lineNumber:456,columnNumber:25},void 0)]},void 0,!0,{fileName:"/app/applet/src/components/UserManagementView.tsx",lineNumber:454,columnNumber:21},void 0),n.jsxDEV("div",{className:"flex items-center gap-2",children:[n.jsxDEV("button",{type:"button",onClick:()=>ae(W),disabled:xe'''

if target_btn_container in code:
    code = code.replace(target_btn_container, replacement_btn_container, 1)
    print("Patch 4.3 (Branch select dropdown added to pending request cards): OK")
else:
    print("Patch 4.3 warning: target_btn_container not found")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All patches written to assets/index-DCC2oYkl.js!")
