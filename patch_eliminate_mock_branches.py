with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Current length:", len(code))

# 1. Eliminate mock branches in pp definition
old_pp = ',pp=[{id:"branch-main",code:"SEDE-01",name:"Sede Central Matriz",address:"Calle 23 esq. L, Vedado, Plaza de la Revolución",phone:"+53 7 832 5544",isMainWarehouse:!0,active:!0,colorTag:"emerald",workMode:"pos_directo"},{id:"branch-vedado",code:"SEDE-02",name:"Sucursal Vedado (Salón & Café)",address:"Calle G No. 452 entre 19 y 21, Vedado",phone:"+53 7 830 1122",isMainWarehouse:!1,active:!0,colorTag:"blue",workMode:"restaurante"},{id:"branch-playa",code:"SEDE-03",name:"Sucursal Miramar / Playa (Terraza Gourmet)",address:"Av. 5ta No. 2408 entre 24 y 26, Miramar, Playa",phone:"+53 7 204 9876",isMainWarehouse:!1,active:!0,colorTag:"purple",workMode:"restaurante"},{id:"branch-habana",code:"SEDE-04",name:"Sucursal Habana Vieja (Punto Express)",address:"Calle Obispo No. 312 entre Habana y Compostela",phone:"+53 7 861 3344",isMainWarehouse:!1,active:!0,colorTag:"amber",workMode:"pos_directo"}],'
new_pp = ',pp=[];'

if old_pp in code:
    code = code.replace(old_pp, new_pp, 1)
    print("1. Mock branches array pp emptied successfully")
else:
    print("1. old_pp not found directly, checking...")

# 2. In getBranches: query Supabase branches directly with is_active = true and order by name, deduplicating with Map
old_get_branches = 'const a=Sn(),{data:r,error:s}=await a.from("branches").select("*");if(!s&&Array.isArray(r)&&r.length>0){const l=r.map(m=>{let f=m.raw_data||m.data;if(typeof f=="string")try{f=JSON.parse(f)}catch{}const h=f&&typeof f=="object"?f:{};return{...h,id:m.id||h.id,name:m.name||h.name||"Sucursal",code:m.code||h.code||"SEDE",address:m.address||h.address||"",phone:m.phone||h.phone||"",isMainWarehouse:m.is_main!==void 0?!!m.is_main:!!h.isMainWarehouse,active:m.active!==void 0?!!m.active:m.is_active!==void 0?!!m.is_active:h.active!==!1,workMode:m.work_mode||h.workMode||"restaurante",colorTag:m.color_tag||h.colorTag||"blue"}}),d=new Map;l.forEach(m=>d.set(m.id,m));try{ca.getQueue().filter(f=>f.entity==="branch"&&f.action==="upsert").forEach(f=>{f.data&&f.data.id&&!d.has(f.data.id)&&d.set(f.data.id,f.data)})}catch{}const u=Array.from(d.values());if(u.length>0){if(this.setLocalCache("branches",u),typeof localStorage<"u")try{localStorage.setItem("bistro_branches",JSON.stringify(u)),localStorage.setItem("cache_branches",JSON.stringify(u))}catch{}return u}}'

new_get_branches = 'const a=Sn(),{data:r,error:s}=await a.from("branches").select("*").eq("is_active",true).order("name",{ascending:true});if(!s&&Array.isArray(r)&&r.length>0){const l=r.map(m=>{let f=m.raw_data||m.data;if(typeof f=="string")try{f=JSON.parse(f)}catch{}const h=f&&typeof f=="object"?f:{};return{...h,id:m.id||h.id,name:m.name||h.name||"Sucursal",code:m.code||h.code||"SEDE",address:m.address||h.address||"",phone:m.phone||h.phone||"",isMainWarehouse:m.is_main!==void 0?!!m.is_main:!!h.isMainWarehouse,active:!0,workMode:m.work_mode||h.workMode||"restaurante",colorTag:m.color_tag||h.colorTag||"blue"}}),d=new Map;l.forEach(m=>d.set(m.id,m));const u=Array.from(d.values());if(u.length>0){if(this.setLocalCache("branches",u),typeof localStorage<"u")try{localStorage.setItem("bistro_branches",JSON.stringify(u)),localStorage.setItem("cache_branches",JSON.stringify(u))}catch{}return u}}'

if old_get_branches in code:
    code = code.replace(old_get_branches, new_get_branches, 1)
    print("2. getBranches direct Supabase query and unique Map deduplication patched")
else:
    print("2. old_get_branches not found directly")

# 3. In App.tsx: ensure activeBranchId is strictly loaded from profile.branch_id on APK / Web
old_branch_lock = 'h.activeBranchId||"branch-main"'
# Check how activeBranchId is initialized in App.tsx
pos_abi = code.find('activeBranchId:"branch-main"')
print("pos activeBranchId branch-main:", pos_abi)

# 4. Remove automatic saving of pp to Supabase
old_save_pp = '_n.length===0&&pp.forEach(Kn=>Zt.saveBranch(Kn).catch(()=>{}))'
new_save_pp = '/* no mock branches save */'

if old_save_pp in code:
    code = code.replace(old_save_pp, new_save_pp, 1)
    print("4. Removed auto-saving pp to Supabase")
else:
    print("4. old_save_pp not found directly")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch applied successfully!")
