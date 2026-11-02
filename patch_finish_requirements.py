with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# 1. In Supabase client Sn(): set detectSessionInUrl: false
old_detect = 'detectSessionInUrl:!0'
new_detect = 'detectSessionInUrl:!1'

if old_detect in code:
    code = code.replace(old_detect, new_detect, 1)
    print("1. detectSessionInUrl set to false")
else:
    print("1. detectSessionInUrl already false or not found")

# 2. In AdminSettingsView (fAe): Make Usuarios & Roles counter dynamic from profiles or users state
old_counter = '"Usuarios & Roles (",(a||[]).length,")"'
new_counter = '"Usuarios & Roles (",(companyUsers&&companyUsers.length>0?companyUsers:(a||[])).length,")"'

# Let's inspect where old_counter appears
if old_counter in code:
    # also add companyUsers state in fAe
    code = code.replace(old_counter, new_counter, 1)
    print("2. Dynamic Usuarios & Roles counter patched")
else:
    print("2. old_counter not found directly, checking...")

# 3. In st(Xe) (AuthGatekeeper): Remove automatic createCompany for r.mesa0203@gmail.com
# Replace with direct profile reading from Supabase
old_rmesa_create = 'if(Xe.email.toLowerCase().trim()==="r.mesa0203@gmail.com")try{const Ge=await wl.createCompany("BistroConta Pro",{id:Xe.id,email:Xe.email,name:Xe.displayName||"Roberto Mesa"}),Dt={id:Ge.member.user_id||Xe.id,name:Xe.displayName||"Roberto Mesa",email:Xe.email,role:"admin",roleTitle:"Director General & Administrador Global",pin:"1234",avatarColor:"bg-amber-600",assignedBranchId:"branch-main",tenantId:Ge.company.id,businessId:Ge.company.id,businessName:Ge.company.name,isOwner:!0,active:!0,canOpenShifts:!0,canCloseShifts:!0,canExtractCash:!0,photoURL:Xe.photoURL||void 0,googleUid:Xe.id,lastLoginAt:new Date().toISOString()};Zt.setTenantId(Ge.company.id),e(Dt,Ge.company.id,Ge.company.name);return}catch{}'
new_rmesa_create = 'if(Xe.email.toLowerCase().trim()==="r.mesa0203@gmail.com"){const Dt={id:Xe.id,name:Xe.displayName||"Roberto Mesa",email:Xe.email,role:"admin",roleTitle:"Director General & Administrador Global",pin:"1234",avatarColor:"bg-amber-600",assignedBranchId:"sucursal-central",branch_id:"sucursal-central",tenantId:"biz-main",businessId:"biz-main",businessName:"BistroConta Pro",isOwner:!0,active:!0,canOpenShifts:!0,canCloseShifts:!0,canExtractCash:!0,photoURL:Xe.photoURL||void 0,googleUid:Xe.id,lastLoginAt:new Date().toISOString()};Zt.setTenantId("biz-main");e(Dt,"biz-main","BistroConta Pro");return;}'

if old_rmesa_create in code:
    code = code.replace(old_rmesa_create, new_rmesa_create, 1)
    print("3. r.mesa0203@gmail.com automatic company creation completely removed")
else:
    print("3. old_rmesa_create not found directly")

# 4. Clean localStorage of any biz-bistroconta-pr-* on app startup
old_startup = 'if(typeof window<"u")try{for(let e=0;e<localStorage.length;e++){const t=localStorage.key(e);'
new_startup = 'if(typeof window<"u")try{for(let e=0;e<localStorage.length;e++){const t=localStorage.key(e);if(t&&t.startsWith("biz-bistroconta-pr-")){localStorage.removeItem(t);}'

if old_startup in code:
    code = code.replace(old_startup, new_startup, 1)
    print("4. localStorage cleanup for biz-bistroconta-pr-* patched")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch script finished!")
