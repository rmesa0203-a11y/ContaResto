with open('apply_clean_deduction.cjs', 'r') as f:
    text = f.read()

start_block = text.find('const block = `') + len('const block = `')
end_block = text.rfind('`;')
block = text[start_block:end_block]

col = 3462
print('Block length:', len(block))
print('Around 3462:')
print(repr(block[max(0, col-100):min(len(block), col+100)]))
