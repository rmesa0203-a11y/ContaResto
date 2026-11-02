import sys

def run():
    target_path = 'assets/index-DCC2oYkl.js'
    with open(target_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Fix infinite loop: replace ia(Ot) with Ja(Ot) in posCatalog.map
    old_ia = 'children: ia(Ot)'
    new_ia = 'children: Ja(Ot)'
    if old_ia in code:
        code = code.replace(old_ia, new_ia, 1)
        print("Fixed ia(Ot) to Ja(Ot) in posCatalog.map!")
    else:
        print("ERROR: old_ia not found!")
        sys.exit(1)

    # 2. Fix PGRST303 error logging in SupabaseHydration
    old_pgrst = 'if(V.value&&V.value.error){const y=V.value.error;return console.error(`[SupabaseHydration: ${N}] Error exacto de Supabase ${y.code||""}: ${y.message||""}`,{code:y.code,message:y.message,details:y.details,hint:y.hint}),!1}'
    new_pgrst = 'if(V.value&&V.value.error){const y=V.value.error;if(y.code==="PGRST303"){console.warn(`[SupabaseHydration: ${N}] Desfase de reloj (PGRST303). Usando caché local.`);return!1}return console.error(`[SupabaseHydration: ${N}] Error exacto de Supabase ${y.code||""}: ${y.message||""}`,{code:y.code,message:y.message,details:y.details,hint:y.hint}),!1}'
    if old_pgrst in code:
        code = code.replace(old_pgrst, new_pgrst, 1)
        print("Fixed PGRST303 handling in SupabaseHydration!")
    else:
        print("WARNING: old_pgrst not found directly, let's search flexible...")
        idx = code.find('Error exacto de Supabase')
        if idx != -1:
            print("Found nearby:", code[idx-100:idx+150])

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Saved file successfully!")

if __name__ == '__main__':
    run()
