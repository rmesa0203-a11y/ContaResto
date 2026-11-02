with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

target = 'const Y=s||$l,$=(i&&i.length>0?i:e?.branches)||[],'
replacement = 'const Y=s||$l,$=(i&&i.length>0?i:e?.branches)||[];const[companyUsers,setCompanyUsers]=S.useState([]);S.useEffect(()=>{if(En()){Sn().from("profiles").select("*").then(({data})=>{if(data&&data.length>0)setCompanyUsers(data);}).catch(()=>{});}},[]);const '

if target in code:
    code = code.replace(target, replacement, 1)
    print("companyUsers hook added to fAe successfully!")
else:
    print("target not found")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)
