with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'return{rev,cogs,opex,grossProfit,netProfit,foodCostPct,netMarginPct}},[i,l,t,d,V]);k=E.totalRevenue>0?'
replacement = 'return{rev,cogs,opex,grossProfit,netProfit,foodCostPct,netMarginPct}},[i,l,t,d,V]);const k=E.totalRevenue>0?'

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed missing const for k, j, I, M, P successfully!")
