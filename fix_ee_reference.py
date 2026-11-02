with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'const effectiveInv=posBranchItems.length>0?posBranchItems:t;ee=ge.find(we=>we.id===he)'
replacement = 'const effectiveInv=posBranchItems.length>0?posBranchItems:t;const ee=ge.find(we=>we.id===he)'

assert target in code, f"Target not found: {target}"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed 'ee is not defined' by declaring 'const ee'! Successfully patched!")
