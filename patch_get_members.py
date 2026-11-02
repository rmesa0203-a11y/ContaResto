with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Bundle length:", len(code))

# 1. Patch getCompanyMembers to include profiles where company_id is null
old_profs_query = '.from("profiles").select("id, email, full_name, role, status, company_id, branch_id, created_at, updated_at").eq("company_id",t).order("created_at",{ascending:!1})'
new_profs_query = '.from("profiles").select("id, email, full_name, role, status, company_id, branch_id, created_at, updated_at").or(`company_id.eq.${t},company_id.is.null`).order("updated_at",{ascending:!1})'

if old_profs_query in code:
    code = code.replace(old_profs_query, new_profs_query, 1)
    print("1. getCompanyMembers query updated to include company_id.is.null")
else:
    print("1. old_profs_query not found directly")

# 2. Patch updateMemberStatusAndRole to explicitly set company_id: "biz-main" upon activation
old_prof_update = 'const profUpdate={status:profStatus,updated_at:new Date().toISOString()};if(r)profUpdate.role=r;if(b)profUpdate.branch_id=b;'
new_prof_update = 'const profUpdate={status:profStatus,updated_at:new Date().toISOString()};if(r)profUpdate.role=r;if(b)profUpdate.branch_id=b;if(profStatus==="active")profUpdate.company_id="biz-main";'

if old_prof_update in code:
    code = code.replace(old_prof_update, new_prof_update, 1)
    print("2. updateMemberStatusAndRole company_id assignment patched")
else:
    print("2. old_prof_update not found directly")

# 3. In AAe (UserManagementView): Ensure errorMsg is displayed clearly and empty state has retry button
# Let's inspect where error message in AAe is displayed
with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved bundle!")
