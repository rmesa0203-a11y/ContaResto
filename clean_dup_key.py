with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

dup = 'className:"font-bold text-xs text-blue-700 dark:text-blue-300 flex items-center gap-1",className:"current-branch-badge font-bold text-xs text-blue-700 dark:text-blue-300 flex items-center gap-1.5"'
clean = 'className:"current-branch-badge font-bold text-xs text-blue-700 dark:text-blue-300 flex items-center gap-1.5"'

if dup in code:
    code = code.replace(dup, clean, 1)
    print("Cleaned duplicate className key successfully!")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)
