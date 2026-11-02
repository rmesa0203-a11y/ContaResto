with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

pos_inv = code.find('const userBranchId=m.branch_id')
print('pos_inv:', pos_inv)
if pos_inv != -1:
    print(repr(code[pos_inv-50:pos_inv+250]))

pos_kds = code.find('const kdsBranchId=V.branch_id')
print('pos_kds:', pos_kds)
if pos_kds != -1:
    print(repr(code[pos_kds-50:pos_kds+250]))
