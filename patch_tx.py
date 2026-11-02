with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

pos_start = code.find('const isMockId=x=>{if(!x)return!1;')
print("pos_start:", pos_start)
pos_end = code.find('return[]};function _Ae(){', pos_start) + 10
print("pos_end:", pos_end)

print("Target found:")
print(repr(code[pos_start:pos_end]))

replacement = 'const isMockId=x=>!1;const Tx=(e,t,a)=>{if(typeof localStorage>"u")return a||[];const s=localStorage.getItem(`cache_${e}`);if(s!==null)try{const l=JSON.parse(s);if(Array.isArray(l)&&l.length>0)return l;}catch{}const i=localStorage.getItem(t);if(i!==null)try{const l=JSON.parse(i);if(Array.isArray(l)&&l.length>0)return l;}catch{}if(e==="inventory"&&typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__){const loc=window.__BISTRO_LOCAL_STORE__.getLocalInventory();if(loc.length>0)return loc;}return a||[];};'

code = code[:pos_start] + replacement + code[pos_end:]

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Tx cleanly replaced with Cache-First Stale-While-Revalidate!")
