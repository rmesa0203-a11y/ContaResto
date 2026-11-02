with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'position:"prefix"}],pp=[];WZ='
replacement = 'position:"prefix"}],pp=[],WZ='

assert target in code, f"Target not found: {target}"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed pp=[],WZ= declaration comma syntax successfully!")
