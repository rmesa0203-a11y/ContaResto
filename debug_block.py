with open('apply_clean_deduction.cjs', 'r') as f:
    text = f.read()

start_block = text.find('const block = `') + len('const block = `')
end_block = text.rfind('`;')
block = text[start_block:end_block]

# wrap with "function wrap() {" + block + "}"
full_src = "function wrap() {" + block + "}"
# character 3462 in full_src is around 3440 in block
col = 3462 - len("function wrap() {")
print("Target col in block:", col)
print("Snippet from col-60 to col+60:")
print(repr(block[col-60:col+60]))
