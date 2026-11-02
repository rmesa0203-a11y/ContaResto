import sys

def run():
    target_path = 'assets/index-DCC2oYkl.js'
    with open(target_path, 'r', encoding='utf-8') as f:
        code = f.read()

    pos = 3650928

    # Fix the :re,const to :re;const
    old_str = ':re,const defaultBranchId="branch-1792458194300-3i4l"'
    new_str = ':re;const defaultBranchId="branch-1792458194300-3i4l"'
    if old_str in code:
        code = code.replace(old_str, new_str, 1)
        print("Fixed :re,const to :re;const")

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(code)

if __name__ == '__main__':
    run()
