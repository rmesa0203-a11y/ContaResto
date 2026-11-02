import sys

def run():
    target_path = 'assets/index-DCC2oYkl.js'
    with open(target_path, 'r', encoding='utf-8') as f:
        code = f.read()

    old_tail = 'window.dispatchEvent(new CustomEvent("bistro_catalog_updated",{detail:{branchId:te,count:us.length}}))}Os.en'
    new_tail = 'window.dispatchEvent(new CustomEvent("bistro_catalog_updated",{detail:{branchId:te,count:us.length}})))}Os.en'

    # Let's check the exact string
    idx = code.find('bistro_catalog_updated",{detail:{branchId:te,count:us.length}}')
    if idx != -1:
        print("Found around:", code[idx-30:idx+90])
        # let's replace
        old_part = code[idx-30:idx+90]
        # It has:
        # window.dispatchEvent(new CustomEvent("bistro_catalog_updated",{detail:{branchId:te,count:us.length}}))}Os.en
        # notice:
        # typeof window<"u"&&(
        # window.dispatchEvent(new CustomEvent(...)),
        # window.dispatchEvent(new CustomEvent(...))
        # )
        # }
        # ;
        corrected = old_part.replace(')))}Os.en', ')));}Os.en').replace('))}Os.en', '));}Os.en')
        code = code[:idx-30] + corrected + code[idx+90:]
        print("Corrected!")

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(code)

if __name__ == '__main__':
    run()
