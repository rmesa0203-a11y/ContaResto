import re

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Current bundle size:", len(code))

# =========================================================================
# 1. BÚSQUEDA FLEXIBLE DE EMPRESA AL REGISTRARSE (joinCompany)
# =========================================================================
target_join_orig = 'const{data:compList,error:d}=await s.from("companies").select("*").or(`company_code.eq.${i},id.eq.${i}`);if(d||!compList||compList.length===0)throw new Error(`Código de empresa no válido. Verifica el código "${i}" con tu administrador.`);const l=compList[0];'

replacement_join_new = '''const cleanCode=i.trim();let l=null;const{data:compList,error:d}=await s.from("companies").select("id, name, company_code").or(`company_code.ilike.${cleanCode},name.ilike.${cleanCode},id.eq.${cleanCode}`);if(compList&&compList.length>0){l=compList[0];}else if(cleanCode.toLowerCase()==="biz-main"){l={id:"biz-main",name:"BistroConta Pro",company_code:"biz-main"};}if(!l){alert("La empresa o código ingresado no existe en la base de datos.");throw new Error("La empresa o código ingresado no existe en la base de datos.");}'''

assert target_join_orig in code, "target_join_orig not found"
code = code.replace(target_join_orig, replacement_join_new, 1)
print("Patch 1 (Búsqueda flexible en joinCompany): OK")

# =========================================================================
# 2. REGISTRO Y PERSISTENCIA DIRECTA EN SUPABASE AUTH Y PROFILES (signUpWithPassword)
# =========================================================================
# Let's inspect the target in signUpWithPassword
target_signup = 'static async signUpWithPassword(t,a,r,s){const i=Sn(),l=t.trim().toLowerCase(),{data:d,error:u}=await i.auth.signUp({email:l,password:a,options:{data:{full_name:r||l.split("@")[0],business_name:s||"Mi Restaurante & Bar"}}});if(u)throw new Error(u.message||"Error al registrar la cuenta en Supabase.");const m=Mx(d.user,d.session);return d.session&&d.user&&this.persistLocalSession(d.session,d.user),{user:m,session:d.session}}'

replacement_signup = '''static async signUpWithPassword(t,a,r,s,companyId,companyCode){const i=Sn(),l=t.trim().toLowerCase();const targetCompId=companyId||"biz-main";const targetCompCode=companyCode||"biz-main";const{data:d,error:u}=await i.auth.signUp({email:l,password:a,options:{data:{full_name:r||l.split("@")[0],company_id:targetCompId,company_code:targetCompCode}}});if(u){alert("Error de registro: "+u.message);throw new Error("Error de registro: "+u.message);}const userId=d.user?.id;if(userId){const{error:profileError}=await i.from("profiles").upsert({id:userId,full_name:r||l.split("@")[0],company_id:targetCompId,role:"pending",status:"pending_approval",business_name:s||"BistroConta Pro",updated_at:new Date().toISOString()});if(profileError)console.error("Error al crear perfil en la nube:",profileError);try{await i.from("company_members").upsert({company_id:targetCompId,user_id:userId,email:l,role:"pending",status:"pending_approval"});}catch(e){console.warn("company_members note:",e);}}const m=Mx(d.user,d.session);return d.session&&d.user&&this.persistLocalSession(d.session,d.user),{user:m,session:d.session}}'''

assert target_signup in code, "target_signup not found"
code = code.replace(target_signup, replacement_signup, 1)
print("Patch 2 (signUpWithPassword direct Supabase Auth & profiles persistence): OK")

# =========================================================================
# 3. FORMULARIO vt EN AuthGatekeeperView: Búsqueda flexible antes de signUp
# =========================================================================
target_vt = 'if(xe){const{user:ft}=await jc.signUpWithPassword(he,ne,W.trim()||void 0,et.trim()||void 0);ft&&ft.email&&await st(ft)}'

replacement_vt = '''if(xe){const client=Sn();const cleanCode=(et||"biz-main").trim();const{data:compList,error:compErr}=await client.from("companies").select("id, name, company_code").or(`company_code.ilike.${cleanCode},name.ilike.${cleanCode},id.eq.${cleanCode}`);let targetCompany=compList&&compList.length>0?compList[0]:null;if(!targetCompany&&cleanCode.toLowerCase()==="biz-main"){targetCompany={id:"biz-main",name:"BistroConta Pro",company_code:"biz-main"};}if(!targetCompany){alert("La empresa o código ingresado no existe en la base de datos.");u("La empresa o código ingresado no existe en la base de datos.");return;}const{user:ft}=await jc.signUpWithPassword(he,ne,W.trim()||void 0,targetCompany.name,targetCompany.id,targetCompany.company_code);if(ft){V({id:ft.id,email:he.trim().toLowerCase(),role:"pending",status:"pending_approval",company_id:targetCompany.id});k(targetCompany);s("pending_approval");return;}}'''

assert target_vt in code, "target_vt not found"
code = code.replace(target_vt, replacement_vt, 1)
print("Patch 3 (vt registration flexible company check and pending approval state): OK")

# =========================================================================
# 4. CARGA GLOBAL DEL PERFIL Y SUCURSAL TRAS INICIAR SESIÓN (onAuthStateChange en App)
# =========================================================================
target_app_auth = 'return ua=jc.onAuthStateChange(Pn=>{Pn&&Pn.email?jc.analyzeGoogleUser(Pn,m).then(_n=>{_n.status==="authenticated"&&_n.profile&&(d(Kn=>Kn||_n.profile),localStorage.setItem("bistro_user",JSON.stringify(_n.profile)))}).catch(_n=>console.warn("Supabase auth state user sync warning:",_n)):!Pn&&!localStorage.getItem("bistro_user")&&d(null)}),'

replacement_app_auth = '''return ua=jc.onAuthStateChange(async Pn=>{if(Pn&&(Pn.email||Pn.id)){try{const client=Sn();const uid=Pn.id||Pn.uid;const{data:profile}=await client.from("profiles").select("*").eq("id",uid).maybeSingle();if(profile){let compName=profile.business_name||"BistroConta Pro";if(profile.company_id){try{const{data:comp}=await client.from("companies").select("*").eq("id",profile.company_id).maybeSingle();if(comp?.name)compName=comp.name;}catch{}}let brName="Sede Principal";if(profile.branch_id){try{const{data:br}=await client.from("branches").select("*").eq("id",profile.branch_id).maybeSingle();if(br?.name)brName=br.name;}catch{}}const fullProfile={...profile,name:profile.full_name||Pn.email?.split("@")[0],email:Pn.email,businessName:compName,tenantId:profile.company_id||"biz-main",assignedBranchId:profile.branch_id||"branch-main",branchName:brName};d(fullProfile);localStorage.setItem("bistro_user",JSON.stringify(fullProfile));if(profile.company_id){t(profile.company_id);localStorage.setItem("bistro_tenant_id",profile.company_id);}}}catch(err){console.warn("Error cargando perfil vivo desde Supabase profiles:",err);}}else if(!Pn&&!localStorage.getItem("bistro_user")){d(null);}}),'''

assert target_app_auth in code, "target_app_auth not found"
code = code.replace(target_app_auth, replacement_app_auth, 1)
print("Patch 4 (onAuthStateChange queries profiles and sets full profile with branch): OK")

# =========================================================================
# 5. PANTALLA DE ESPERA DE APROBACIÓN EN EL ROOT DE App (bloqueo si pending_approval)
# =========================================================================
target_render_gate = 'if(!l)return n.jsxDEV(SAe,{registeredUsers:m,branches:N,onLoginSuccess:(be,Ie,Be)=>{Zt.setTenantId(Ie),Zt.setTenantId(Ie),t(Ie),d(be),localStorage.setItem("bistro_user",JSON.stringify(be)),localStorage.setItem("bistro_tenant_id",Ie),be.name&&qn("login",`Inicio de sesión exitoso: ${be.name} (${be.roleTitle}) en ${Be||Ie}`)}},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2003,columnNumber:7},this);'

replacement_render_gate = '''if(!l)return n.jsxDEV(SAe,{registeredUsers:m,branches:N,onLoginSuccess:(be,Ie,Be)=>{Zt.setTenantId(Ie),Zt.setTenantId(Ie),t(Ie),d(be),localStorage.setItem("bistro_user",JSON.stringify(be)),localStorage.setItem("bistro_tenant_id",Ie),be.name&&qn("login",`Inicio de sesión exitoso: ${be.name} (${be.roleTitle}) en ${Be||Ie}`)}},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2003,columnNumber:7},this);if(l&&(l.status==="pending_approval"||l.status==="pending"))return n.jsxDEV("div",{className:"min-h-screen bg-slate-950 flex items-center justify-center p-4",children:n.jsxDEV("div",{className:"max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center space-y-4 shadow-2xl",children:[n.jsxDEV("div",{className:"w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto text-3xl",children:"⏳"},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2006,columnNumber:11},this),n.jsxDEV("h2",{className:"text-xl font-bold text-white",children:"Solicitud de Acceso Enviada al Administrador"},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2007,columnNumber:11},this),n.jsxDEV("p",{className:"text-xs text-slate-300 leading-relaxed",children:"Solicitud de acceso enviada al administrador. Tu cuenta se activará cuando asignen tu rol y sucursal."},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2008,columnNumber:11},this),n.jsxDEV("div",{className:"p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-slate-400",children:`Registrado como: ${l.email||l.name} (${l.businessName||"Empresa"})`},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2009,columnNumber:11},this),n.jsxDEV("button",{type:"button",onClick:async()=>{localStorage.removeItem("bistro_user");d(null);try{await Sn().auth.signOut()}catch(e){}},className:"w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition cursor-pointer",children:"Cerrar Sesión / Salir"},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2010,columnNumber:11},this)]},void 0,!0,{fileName:"/app/applet/src/App.tsx",lineNumber:2005,columnNumber:9},this)},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2004,columnNumber:7},this);'''

assert target_render_gate in code, "target_render_gate not found"
code = code.replace(target_render_gate, replacement_render_gate, 1)
print("Patch 5 (Pending approval screen blocks operation until approved): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("ALL 5 PATCHES APPLIED TO assets/index-DCC2oYkl.js SUCCESSFULLY!")
