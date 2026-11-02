with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# 1. Deduplicate posItems in loadBranchInv in PosView
old_load_map = 'if(!posErr&&Array.isArray(posItems)&&posItems.length>0&&mounted){const mapped=posItems.map(item=>{'

new_load_map = '''if(!posErr&&Array.isArray(posItems)&&posItems.length>0&&mounted){const uMap=new Map();posItems.forEach(item=>{const k=item.item_id||item.inventory?.id||item.id;if(!k)return;if(!uMap.has(k)){uMap.set(k,{...item});}else{const prev=uMap.get(k);prev.current_stock=Number(prev.current_stock||0)+Number(item.current_stock||0);}});const uniquePosItems=Array.from(uMap.values());const mapped=uniquePosItems.map(item=>{'''

assert old_load_map in code, "old_load_map not found"
code = code.replace(old_load_map, new_load_map, 1)
print("1. loadBranchInv deduplication with stock sum patched")

# 2. In PosView grid:
# Change cl.map to cl.map((we,clIdx)=> ... and key `combo-${we.id}-${clIdx}`
old_cl_map = 'cl.map(we=>{'
new_cl_map = 'cl.map((we,clIdx)=>{'
assert old_cl_map in code, "old_cl_map not found"
code = code.replace(old_cl_map, new_cl_map, 1)

# Find key for cl.map
pos_cl = code.find('cl.map((we,clIdx)=>{', 3715000)
pos_cl_key = code.find('we.id,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3305', pos_cl)
assert pos_cl_key != -1, "pos_cl_key not found"
target_cl_key = 'we.id,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3305'
replacement_cl_key = '`combo-${we.id}-${clIdx}`,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3305'
code = code[:pos_cl_key] + replacement_cl_key + code[pos_cl_key+len(target_cl_key):]
print("2. cl.map key prefixed with combo-${we.id}-${clIdx}")

# 3. In PosView grid:
# Change Yl.map to Yl.map((we,ylIdx)=> ... and key `recipe-${we.id}-${ylIdx}`
old_yl_map = 'Yl.map(we=>{'
new_yl_map = 'Yl.map((we,ylIdx)=>{'
assert old_yl_map in code, "old_yl_map not found"
code = code.replace(old_yl_map, new_yl_map, 1)

pos_yl = code.find('Yl.map((we,ylIdx)=>{', 3720000)
pos_yl_key = code.find('we.id,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3393', pos_yl)
assert pos_yl_key != -1, "pos_yl_key not found"
target_yl_key = 'we.id,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3393'
replacement_yl_key = '`recipe-${we.id}-${ylIdx}`,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3393'
code = code[:pos_yl_key] + replacement_yl_key + code[pos_yl_key+len(target_yl_key):]
print("3. Yl.map key prefixed with recipe-${we.id}-${ylIdx}")

# 4. In PosView grid:
# Change Oc.map to Oc.map((we,ocIdx)=> ... and key `prod-${we.id}-${ocIdx}`
old_oc_map = 'Oc.map(we=>{'
new_oc_map = 'Oc.map((we,ocIdx)=>{'
assert old_oc_map in code, "old_oc_map not found"
code = code.replace(old_oc_map, new_oc_map, 1)

pos_oc = code.find('Oc.map((we,ocIdx)=>{', 3724000)
pos_oc_key = code.find('we.id,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3459', pos_oc)
assert pos_oc_key != -1, "pos_oc_key not found"
target_oc_key = 'we.id,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3459'
replacement_oc_key = '`prod-${we.id}-${ocIdx}`,!0,{fileName:"/app/applet/src/components/PosView.tsx",lineNumber:3459'
code = code[:pos_oc_key] + replacement_oc_key + code[pos_oc_key+len(target_oc_key):]
print("4. Oc.map key prefixed with prod-${we.id}-${ocIdx}")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Duplicate keys fix successfully applied!")
