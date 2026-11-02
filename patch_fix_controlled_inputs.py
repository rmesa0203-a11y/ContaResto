with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original bundle length:", len(code))

# 1. Patch Ce edit user call
old_ce = 'Ce({name:Pe.name,email:Pe.email,role:Pe.role,roleTitle:Pe.roleTitle,pin:Pe.pin,assignedBranchId:Pe.assignedBranchId||$[0]?.id||"branch-main",phone:Pe.phone||"",canOpenShifts:Pe.canOpenShifts??!0,canCloseShifts:Pe.canCloseShifts??!0,canExtractCash:Pe.canExtractCash??!0})'
new_ce = 'Ce({name:Pe.name||Pe.full_name||"",email:Pe.email||"",role:Pe.role||"clerk",roleTitle:Pe.roleTitle||"",pin:Pe.pin||"1234",assignedBranchId:Pe.assignedBranchId||Pe.branch_id||$[0]?.id||"branch-main",phone:Pe.phone||"",canOpenShifts:Pe.canOpenShifts??!0,canCloseShifts:Pe.canCloseShifts??!0,canExtractCash:Pe.canExtractCash??!0})'

if old_ce in code:
    code = code.replace(old_ce, new_ce, 1)
    print("1. Ce edit user call patched")
else:
    print("1. old_ce not found directly, checking...")

# 2. Patch Oe inputs
replacements = [
    ('value:Oe.name,', 'value:Oe.name||"",'),
    ('value:Oe.email,', 'value:Oe.email||"",'),
    ('value:Oe.roleTitle,', 'value:Oe.roleTitle||"",'),
    ('value:Oe.pin,', 'value:Oe.pin||"",'),
    ('value:Oe.phone,', 'value:Oe.phone||"",'),
    ('value:Dt.name,', 'value:Dt.name||"",'),
    ('value:Dt.code,', 'value:Dt.code||"",'),
    ('value:Dt.phone,', 'value:Dt.phone||"",'),
    ('value:Dt.address,', 'value:Dt.address||"",'),
    ('value:Dt.managerName,', 'value:Dt.managerName||"",'),
    ('value:Dt.email,', 'value:Dt.email||"",'),
    ('value:B.name,', 'value:B.name||"",'),
    ('value:B.code,', 'value:B.code||"",'),
    ('value:B.phone,', 'value:B.phone||"",'),
    ('value:B.address,', 'value:B.address||"",'),
    ('value:B.managerName,', 'value:B.managerName||"",'),
    ('value:B.email,', 'value:B.email||"",'),
    ('value:W.name,', 'value:W.name||"",'),
    ('value:W.position,', 'value:W.position||"",'),
    ('value:W.phone,', 'value:W.phone||"",'),
    ('value:W.nationalId,', 'value:W.nationalId||"",'),
    ('value:u.serverHostUrl,', 'value:u.serverHostUrl||"",'),
    ('value:u.deviceName,', 'value:u.deviceName||"",'),
    ('value:N.name,', 'value:N.name||"",'),
    ('value:N.ipAddress,', 'value:N.ipAddress||"",'),
]

for old, new in replacements:
    count = code.count(old)
    if count > 0:
        code = code.replace(old, new)
        print(f"Replaced {old} -> {new} ({count} times)")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Protected all controlled inputs with default fallback successfully!")
