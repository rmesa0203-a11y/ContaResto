with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'q&&xe&&n.jsxDEV("div",{className:"hidden lg:flex items-center space-x-1.5 px-2.5 py-1 bg-sky-950/80 border border-sky-600/5'
replacement = '(W.role||"").toLowerCase()!=="admin"&&n.jsxDEV("div",{className:"hidden lg:flex items-center space-x-1.5 px-2.5 py-1 bg-emerald-950/80 border border-emerald-500/50 text-emerald-300'

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Navbar badge for non-admin patched!")
