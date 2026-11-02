with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Bundle length before:", len(code))

# 1. In getBranches: filter out legacy mock IDs and deduplicate strictly with Map
old_u_ret = 'const u=Array.from(d.values());if(u.length>0){'
new_u_ret = 'const u=Array.from(new Map(Array.from(d.values()).filter(m=>m.id!=="branch-vedado"&&m.id!=="branch-playa"&&m.id!=="branch-habana").map(m=>[m.id,m])).values());if(u.length>0){'

if old_u_ret in code:
    code = code.replace(old_u_ret, new_u_ret, 1)
    print("1. getBranches deduplication and mock ID filter patched")
else:
    print("1. old_u_ret not found directly")

# 2. In App.tsx: when user profile (l) loads, assign and lock activeBranchId to profile.branch_id
old_l_effect = 'S.useEffect(()=>{l?localStorage.setItem("bistro_user",JSON.stringify(l)):localStorage.removeItem("bistro_user")},[l])'
new_l_effect = 'S.useEffect(()=>{if(l){localStorage.setItem("bistro_user",JSON.stringify(l));const ab=l.branch_id||l.assignedBranchId;if(ab){localStorage.setItem("active_branch_id",ab);localStorage.setItem("bistro_active_branch",ab);g(Kn=>({...Kn,activeBranchId:ab}));}}else{localStorage.removeItem("bistro_user");}},[l])'

if old_l_effect in code:
    code = code.replace(old_l_effect, new_l_effect, 1)
    print("2. App.tsx l effect activeBranchId assignment and locking patched")
else:
    print("2. old_l_effect not found directly")

# 3. Clean any cached mock branches from localStorage on app boot
old_boot_clean = 'if(typeof window<"u")try{for(let e=0;e<localStorage.length;e++){const t=localStorage.key(e);if(t&&t.startsWith("biz-bistroconta-pr-")){localStorage.removeItem(t);}'
new_boot_clean = 'if(typeof window<"u")try{const bb=localStorage.getItem("bistro_branches");if(bb&&bb.includes("branch-vedado")){localStorage.removeItem("bistro_branches");localStorage.removeItem("cache_branches");};for(let e=0;e<localStorage.length;e++){const t=localStorage.key(e);if(t&&(t.startsWith("biz-bistroconta-pr-")||t==="cache_branches"&&localStorage.getItem(t)?.includes("branch-vedado"))){localStorage.removeItem(t);}'

if old_boot_clean in code:
    code = code.replace(old_boot_clean, new_boot_clean, 1)
    print("3. Clean legacy mock cache from localStorage on startup patched")
else:
    print("3. old_boot_clean not found directly")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patching finished successfully!")
