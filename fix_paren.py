import subprocess
import sys

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_s = 'window.dispatchEvent(new CustomEvent("bistro_catalog_updated",{detail:{branchId:te,count:us.length}})))};'
new_s = 'window.dispatchEvent(new CustomEvent("bistro_catalog_updated",{detail:{branchId:te,count:us.length}}))};'

if old_s in code:
    code = code.replace(old_s, new_s, 1)
    print("Replaced extra paren!")
    with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
        f.write(code)
else:
    print("old_s not found!")
    sys.exit(1)

res = subprocess.run([
    'node', '-e',
    'const fs=require("fs"), esbuild=require("esbuild"); const code=fs.readFileSync("assets/index-DCC2oYkl.js","utf8"); esbuild.transformSync(code, {loader:"js"}); console.log("AST_SUCCESS");'
], capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print("ERROR:", res.stderr)
    sys.exit(1)
