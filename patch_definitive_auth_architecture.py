import re

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Current bundle size:", len(code))

# =========================================================================
# 1. REMOVE MOCK BUTTON "Acceso Inmediato: Roberto Mesa" FROM ERROR BOX
# =========================================================================
mock_btn_pattern = r'd&&n\.jsxDEV\("div",\{className:"m-6 mb-0 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-300 text-xs space-y-3",children:\[n\.jsxDEV\("div",\{className:"flex items-start gap-2\.5",children:\[n\.jsxDEV\(_c,\{className:"w-4 h-4 text-rose-400 shrink-0 mt-0\.5"\},void 0,!1,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:684,columnNumber:15\},void 0\),n\.jsxDEV\("span",\{className:"leading-relaxed",children:d\},void 0,!1,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:685,columnNumber:15\},void 0\)\]\},void 0,!0,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:683,columnNumber:13\},void 0\),n\.jsxDEV\("div",\{className:"pt-2 border-t border-rose-500/20",children:n\.jsxDEV\("button",\{type:"button",id:"gatekeeper-quick-admin-btn",onClick:Te,className:"w-full py-2\.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 shadow transition active:scale-\[0\.98\]",children:\[n\.jsxDEV\(db,\{className:"w-3\.5 h-3\.5 text-amber-300"\},void 0,!1,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:694,columnNumber:17\},void 0\),n\.jsxDEV\("span",\{children:"Acceso Inmediato: Roberto Mesa \(r\.mesa0203@gmail\.com\)"\},void 0,!1,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:695,columnNumber:17\},void 0\)\]\},void 0,!0,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:688,columnNumber:15\},void 0\)\},void 0,!1,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:687,columnNumber:13\},void 0\)\]\},void 0,!0,\{fileName:"/app/applet/src/components/AuthGatekeeperView\.tsx",lineNumber:682,columnNumber:11\},void 0\)'

replacement_err_box = 'd&&n.jsxDEV("div",{className:"m-6 mb-0 p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-300 text-xs",children:n.jsxDEV("div",{className:"flex items-start gap-2.5",children:[n.jsxDEV(_c,{className:"w-4 h-4 text-rose-400 shrink-0 mt-0.5"},void 0,!1,{fileName:"/app/applet/src/components/AuthGatekeeperView.tsx",lineNumber:684,columnNumber:15},void 0),n.jsxDEV("span",{className:"leading-relaxed",children:d},void 0,!1,{fileName:"/app/applet/src/components/AuthGatekeeperView.tsx",lineNumber:685,columnNumber:15},void 0)]},void 0,!0,{fileName:"/app/applet/src/components/AuthGatekeeperView.tsx",lineNumber:683,columnNumber:13},void 0)},void 0,!1,{fileName:"/app/applet/src/components/AuthGatekeeperView.tsx",lineNumber:682,columnNumber:11},void 0)'

match_found = re.search(mock_btn_pattern, code)
if match_found:
    code = code[:match_found.start()] + replacement_err_box + code[match_found.end():]
    print("Patch 1 (Removed mock Roberto Mesa button from AuthGatekeeperView): OK")
else:
    print("Patch 1 notice: pattern not directly matched via regex, searching substring...")
    pos = code.find('gatekeeper-quick-admin-btn')
    if pos != -1:
        # find container start and end
        pos_start = code.rfind('d&&n.jsxDEV("div"', 0, pos)
        pos_end = code.find('},void 0,!1,{fileName:"/app/applet/src/components/AuthGatekeeperView.tsx",lineNumber:682,columnNumber:11},void 0)', pos) + len('},void 0,!1,{fileName:"/app/applet/src/components/AuthGatekeeperView.tsx",lineNumber:682,columnNumber:11},void 0)')
        code = code[:pos_start] + replacement_err_box + code[pos_end:]
        print("Patch 1 (Substring replacement for mock button): OK")

# =========================================================================
# 2. DISABLE Te MOCK FUNCTION
# =========================================================================
target_te = 'Te=()=>{const Xe=t.find(ft=>(ft.email||"").toLowerCase()==="r.mesa0203@gmail.com"||ft.role==="admin")||{id:"usr-admin-roberto",name:"Roberto Mesa (Administrador)",email:"r.mesa0203@gmail.com",role:"admin",roleTitle:"Director General & Administrador Global",pin:"1234",avatarColor:"bg-emerald-600",assignedBranchId:"branch-main",tenantId:"biz-main",businessId:"biz-main",businessName:"BistroConta Pro",isOwner:!0,active:!0,canOpenShifts:!0,canCloseShifts:!0,canExtractCash:!0};e(Xe,Xe.tenantId||"biz-main",Xe.businessName)}'

replacement_te = 'Te=()=>{console.log("Mock bypass disabled. Please log in with Supabase Auth credentials.");}'

if target_te in code:
    code = code.replace(target_te, replacement_te, 1)
    print("Patch 2 (Te mock admin bypass neutralized): OK")
else:
    print("Patch 2 notice: target_te already neutralized or slightly different")

# =========================================================================
# 3. UPDATE PROFILES TABLE ON MEMBER APPROVAL / REJECTION
# =========================================================================
target_update_member = 'static async updateMemberStatusAndRole(t,a,r,b){const s=Sn(),i={status:a};r&&(i.role=r);b&&(i.branch_id=b);const{data:l,error:d}=await s.from("company_members").update(i).eq("id",t).select().single();if(d)throw console.error("[SupabaseCompany] Error updating member status:",d),new Error(`Error al actualizar miembro: ${d.message}`);return l}'

replacement_update_member = 'static async updateMemberStatusAndRole(t,a,r,b){const s=Sn(),i={status:a};r&&(i.role=r);b&&(i.branch_id=b);const{data:l,error:d}=await s.from("company_members").update(i).eq("id",t).select().single();if(d)throw console.error("[SupabaseCompany] Error updating member status:",d),new Error(`Error al actualizar miembro: ${d.message}`);try{const profUpdate={status:a,updated_at:new Date().toISOString()};r&&(profUpdate.role=r);b&&(profUpdate.branch_id=b);if(l?.user_id){await s.from("profiles").update(profUpdate).eq("id",l.user_id);}else if(l?.email){await s.from("profiles").update(profUpdate).ilike("email",l.email);}}catch(pe){console.warn("[updateMemberStatusAndRole] Notice updating profiles table:",pe);}return l;}'

if target_update_member in code:
    code = code.replace(target_update_member, replacement_update_member, 1)
    print("Patch 3 (updateMemberStatusAndRole synchronizes public.profiles status, role & branch): OK")
else:
    print("Patch 3 notice: target_update_member not found directly")

# =========================================================================
# 4. ENHANCE PENDING APPROVAL SCREEN WITH "Comprobar Estado" BUTTON
# =========================================================================
target_pending_screen = 'n.jsxDEV("button",{type:"button",onClick:async()=>{localStorage.removeItem("bistro_user");d(null);try{await Sn().auth.signOut()}catch(e){}},className:"w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition cursor-pointer",children:"Cerrar Sesión / Salir"},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2010,columnNumber:11},this)'

replacement_pending_screen = 'n.jsxDEV("div",{className:"space-y-2 w-full",children:[n.jsxDEV("button",{type:"button",onClick:async()=>{try{const pRes=await Sn().from("profiles").select("*").eq("id",l.id).maybeSingle();if(pRes?.data&&pRes.data.status==="active"){const up={...l,...pRes.data,status:"active",role:pRes.data.role||"cajero",assignedBranchId:pRes.data.branch_id||"branch-main"};d(up);localStorage.setItem("bistro_user",JSON.stringify(up));}else{alert("Tu cuenta aún se encuentra pendiente de aprobación por el administrador.");}}catch(e){alert("Error comprobando estado: "+e.message);}},className:"w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20",children:"Comprobar Estado"},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2010,columnNumber:11},this),n.jsxDEV("button",{type:"button",onClick:async()=>{localStorage.removeItem("bistro_user");d(null);try{await Sn().auth.signOut()}catch(e){}},className:"w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center gap-2",children:"Cerrar Sesión"},void 0,!1,{fileName:"/app/applet/src/App.tsx",lineNumber:2011,columnNumber:11},this)]},void 0,!0,{fileName:"/app/applet/src/App.tsx",lineNumber:2009,columnNumber:10},this)'

if target_pending_screen in code:
    code = code.replace(target_pending_screen, replacement_pending_screen, 1)
    print("Patch 4 (Added Comprobar Estado refreshProfile button to pending screen): OK")
else:
    print("Patch 4 notice: target_pending_screen not found directly")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patching complete!")
