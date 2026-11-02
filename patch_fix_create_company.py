with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original bundle length:", len(code))

# 1. Patch generateCompanyId
pos_gen = code.find('static generateCompanyId(t){')
pos_mem = code.find('static async getMemberForUser(', pos_gen)
old_gen = code[pos_gen:pos_mem]

new_gen = 'static generateCompanyId(t){const low=(t||"").toLowerCase();if(low.includes("bistroconta")||low==="biz-main")return"biz-main";const a=t.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").replace(/[^a-z0-9]/g,"-").replace(/-+/g,"-").replace(/^-|-$/g,"").substring(0,14);return`biz-${a||"resto"}`}'
code = code[:pos_gen] + new_gen + code[pos_mem:]
print("1. generateCompanyId patched")

# 2. Patch getMemberForUser
pos_mem2 = code.find('static async getMemberForUser(')
pos_create = code.find('static async createCompany(', pos_mem2)
old_mem = code[pos_mem2:pos_create]

new_mem = '''static async getMemberForUser(t,a){if(!En())return null;try{const r=Sn(),s=a?a.toLowerCase().trim():"";let pQ=r.from("profiles").select("*");if(t&&s)pQ=pQ.or(`id.eq.${t},email.ilike.${s}`);else if(t)pQ=pQ.eq("id",t);else if(s)pQ=pQ.ilike("email",s);else return null;const{data:pList}=await pQ.order("created_at",{ascending:!1});if(pList&&pList.length>0){const p=pList.find(x=>x.status==="active")||pList[0];if(p.company_id){const{data:c}=await r.from("companies").select("*").eq("id",p.company_id).maybeSingle();const comp=c||{id:p.company_id,name:p.business_name||"BistroConta Pro",company_code:p.company_id};const st=(p.status==="pending_approval"||p.status==="pending")?"pending":p.status;return{member:{id:p.id,user_id:p.id,company_id:p.company_id,email:p.email||s,role:p.role||"cajero",status:st,branch_id:p.branch_id||"branch-main",company_name:comp.name,full_name:p.full_name||s.split("@")[0]},company:comp};}}let i=r.from("company_members").select("*");if(t&&s)i=i.or(`user_id.eq.${t},email.ilike.${s}`);else if(t)i=i.eq("user_id",t);else if(s)i=i.ilike("email",s);else return null;const{data:l,error:d}=await i.order("created_at",{ascending:!1});if(d)return console.warn("[SupabaseCompany] Error buscando membresía:",d.message),null;if(!l||l.length===0)return null;const u=l.find(f=>f.status==="active")||l[0];if(!u.user_id&&t)try{await r.from("company_members").update({user_id:t}).eq("id",u.id),u.user_id=t}catch{}let m=null;if(u.company_id){const{data:f}=await r.from("companies").select("*").eq("id",u.company_id).maybeSingle();f&&(m=f);}return{member:{...u,company_name:m?.name||u.company_id},company:m};}catch(r){return console.error("[SupabaseCompany] getMemberForUser exception:",r),null;}}'''

code = code[:pos_mem2] + new_mem + code[pos_create:]
print("2. getMemberForUser patched")

# 3. Patch createCompany
pos_create2 = code.find('static async createCompany(')
pos_join = code.find('static async joinCompany(', pos_create2)
old_create = code[pos_create2:pos_join]

new_create = '''static async createCompany(t,a){const r=Sn(),s=t.trim();if(!s)throw new Error("El nombre de la empresa o restaurante es obligatorio.");const l=a.email.toLowerCase().trim(),low=s.toLowerCase();let d=null;if(low.includes("bistroconta")||low==="biz-main"||l==="r.mesa0203@gmail.com"){const{data:existing}=await r.from("companies").select("*").eq("id","biz-main").maybeSingle();d=existing||{id:"biz-main",name:"BistroConta Pro",company_code:"biz-main"};}else{const{data:found}=await r.from("companies").select("*").or(`company_code.ilike.${s},name.ilike.${s}`).maybeSingle();if(found){d=found;}else{const compId=this.generateCompanyId(s);const{data:newComp,error:u}=await r.from("companies").insert([{id:compId,name:s,company_code:compId,owner_id:a.id||null}]).select().single();if(u){console.error("[SupabaseCompany] Error al crear empresa:",u);throw new Error(`Error al registrar la empresa: ${u.message}`);}d=newComp;}}if(a.id){try{await r.from("profiles").upsert({id:a.id,email:l,full_name:a.name||l.split("@")[0],company_id:d.id,role:"admin",status:"active",business_name:d.name,updated_at:new Date().toISOString()});}catch(pe){}}let m={company_id:d.id,user_id:a.id||null,email:l,role:"admin",status:"active"};try{const{data:saved}=await r.from("company_members").upsert([m]).select().maybeSingle();if(saved)m=saved;}catch(fe){}return{company:d,member:{...m,company_name:d.name,full_name:a.name||l.split("@")[0]}};}'''

code = code[:pos_create2] + new_create + code[pos_join:]
print("3. createCompany patched")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch applied to index-DCC2oYkl.js successfully!")
