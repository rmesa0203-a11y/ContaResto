with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'else /* no mock branches save */}).catch'
replacement = '}).catch'

assert target in code, "target not found"
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed empty else statement!")
