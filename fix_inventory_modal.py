with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'children:Bt.name})]}),void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2906,columnNumber:17},void 0)'
replacement = 'children:Bt.name},void 0,!1)]},void 0,!0,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2906,columnNumber:17},void 0)'

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed inventory modal closing structure!")
