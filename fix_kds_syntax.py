with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = ',const kdsBranchId=V.branch_id||V.assignedBranchId||"branch-main";const E=(V.role||"").toLowerCase()!=="admin",'
replacement = ',kdsBranchId=V.branch_id||V.assignedBranchId||"branch-main",E=(V.role||"").toLowerCase()!=="admin",'

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("kds declaration syntax fixed!")
