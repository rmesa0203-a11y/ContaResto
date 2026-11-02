with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'selling_price:Xt>0?Xt:null,selling_price_cup:Xt>0?Xt:null,price:Xt>0?Xt:null,selling_price_usd:Tn>0?Tn:null'
assert target in code, f"Target '{target}' not found!"

# Replace with only valid Supabase columns: selling_price_cup and selling_price_usd
replacement = 'selling_price_cup:Xt>0?Xt:null,selling_price_usd:Tn>0?Tn:null'
code = code.replace(target, replacement, 1)

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Successfully removed invalid 'price' column from Supabase update in assets/index-DCC2oYkl.js!")
