with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

import re
pos_aae = code.find('const AAe=')
sub = code[pos_aae:pos_aae+30000]
matches = [m.start() for m in re.finditer(r'n\.jsxDEV\([\"\']input[\"\'],\{', sub)]
print('Inputs in AAe count:', len(matches))
for p in matches:
    chunk = sub[p:p+300]
    val_m = re.search(r'value:([^,}]+)', chunk)
    print(val_m.group(1) if val_m else 'NO VALUE', '-->', chunk[:120])
