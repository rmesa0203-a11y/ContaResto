import re

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original bundle length:", len(code))

# =========================================================================
# 1. OFFLINE-FIRST ARCHITECTURE WITH AUTO-SYNC QUEUE
# =========================================================================
# Define global offlineSync helper at the top of bundle execution
offline_sync_snippet = '''
(function(){
  if(typeof window==="undefined")return;
  window.__BISTRO_OFFLINE_SYNC__={
    getPending:function(){
      try{return JSON.parse(localStorage.getItem("bistro_pending_sales")||"[]");}catch(e){return[];}
    },
    enqueue:function(sale,branchId,tenantId,deductions){
      try{
        var list=this.getPending();
        if(!list.some(function(it){return it.id===sale.id||it.sale?.id===sale.id;})){
          list.push({id:sale.id,sale:sale,branchId:branchId,tenantId:tenantId||"biz-main",stockDeductions:deductions||[],createdAt:new Date().toISOString()});
          localStorage.setItem("bistro_pending_sales",JSON.stringify(list));
        }
        window.dispatchEvent(new CustomEvent("bistro_offline_sync_updated",{detail:{count:list.length,message:"Venta guardada en modo offline. Pendiente de sincronizar"}}));
      }catch(e){console.warn("[OfflineSync] Enqueue error:",e);}
    },
    remove:function(id){
      try{
        var list=this.getPending().filter(function(it){return it.id!==id&&it.sale?.id!==id;});
        localStorage.setItem("bistro_pending_sales",JSON.stringify(list));
        window.dispatchEvent(new CustomEvent("bistro_offline_sync_updated",{detail:{count:list.length}}));
      }catch(e){}
    },
    syncAll:async function(client){
      if(typeof navigator!=="undefined"&&!navigator.onLine)return;
      var c=client||(typeof window!=="undefined"&&window.__BISTRO_SUPABASE_CLIENT__);
      if(!c)return;
      var list=this.getPending();
      if(list.length===0)return;
      var synced=0;
      for(var i=0;i<list.length;i++){
        var it=list[i];
        try{
          var payload={
            id:it.sale.id,
            tenant_id:it.tenantId||it.sale.tenant_id||"biz-main",
            branch_id:it.branchId||it.sale.branchId||it.sale.branch_id,
            sale_number:it.sale.saleNumber||it.sale.sale_number,
            date:it.sale.date,
            time:it.sale.time,
            subtotal:it.sale.subtotal||it.sale.totalAmount||0,
            tax_amount:it.sale.taxAmount||0,
            tip_amount:it.sale.tipAmount||0,
            total_amount:it.sale.totalAmount||it.sale.amountCUP||0,
            payment_method:it.sale.paymentMethod||"Efectivo",
            status:it.sale.status||"completed",
            data:it.sale
          };
          var res=await c.from("sales").upsert(payload,{onConflict:"id"});
          if(!res.error){
            this.remove(it.id);
            synced++;
          }
        }catch(e){console.warn("[OfflineSync] Sync item error:",e);}
      }
      if(synced>0){
        window.dispatchEvent(new CustomEvent("bistro_offline_sync_updated",{detail:{count:this.getPending().length,message:"Sincronización completada: "+synced+" ventas sincronizadas con Supabase"}}));
      }
    }
  };
  window.addEventListener("online",function(){
    console.log("[OfflineSync] Conexión detectada. Sincronizando ventas pendientes...");
    window.__BISTRO_OFFLINE_SYNC__.syncAll();
  });
  setInterval(function(){
    if(typeof navigator!=="undefined"&&navigator.onLine&&window.__BISTRO_OFFLINE_SYNC__.getPending().length>0){
      window.__BISTRO_OFFLINE_SYNC__.syncAll();
    }
  },20000);
})();
'''

# Inject offlineSync at the beginning of the bundle
pos_import = code.find('import')
if pos_import != -1:
    pos_line_end = code.find('\n', pos_import)
    # Put after imports or first statement
    pos_first = code.find('const ')
    code = code[:pos_first] + offline_sync_snippet + '\n' + code[pos_first:]
    print("Patch 1.1 (OfflineSync global service injected): OK")

# Wrap PosView sale insertion to catch offline/network errors and enqueue into bistro_pending_sales
target_pos_insert = 'N(Er),V(gs);const Cs=Sn(),{error:ts}=await Cs.from("sales").insert({id:Er.id,tenant_id:ee?.tenant_id||"biz-main",branch_id:he,sale_number:Er.saleNumber,date:Er.date,time:Er.time,subtotal:Er.subtotal,tax_amount:Er.taxAmount,tip_amount:Er.tipAmount,total_amount:Er.totalAmount,payment_method:Er.paymentMethod,status:"completed",data:Er});ts&&console.error("Error al insertar la venta en Supabase:",ts);'

replacement_pos_insert = '''N(Er),V(gs);let ts=null;if(typeof navigator!=="undefined"&&!navigator.onLine){ts={message:"OFFLINE_MODE"};window.__BISTRO_OFFLINE_SYNC__?.enqueue(Er,he,ee?.tenant_id,pi);}else{try{const Cs=Sn();const res=await Cs.from("sales").insert({id:Er.id,tenant_id:ee?.tenant_id||"biz-main",branch_id:he,sale_number:Er.saleNumber,date:Er.date,time:Er.time,subtotal:Er.subtotal,tax_amount:Er.taxAmount,tip_amount:Er.tipAmount,total_amount:Er.totalAmount,payment_method:Er.paymentMethod,status:"completed",data:Er});if(res.error){ts=res.error;window.__BISTRO_OFFLINE_SYNC__?.enqueue(Er,he,ee?.tenant_id,pi);}}catch(netErr){ts=netErr;window.__BISTRO_OFFLINE_SYNC__?.enqueue(Er,he,ee?.tenant_id,pi);}}'''

assert target_pos_insert in code, "target_pos_insert not found"
code = code.replace(target_pos_insert, replacement_pos_insert, 1)
print("Patch 1.2 (PosView offline queue on sale insert): OK")

# =========================================================================
# 2. STRICT MULTI-BRANCH SEGMENTATION
# =========================================================================
# In PosView: if user role is restricted (clerk, cajero, dependiente, mesero), lock branch to user's branch_id
target_pos_branch_init = 'const he=oe,ee=ge.find(we=>we.id===he)||l.find(we=>we.id===he)||ge[0]||l[0]'

replacement_pos_branch_init = '''const userBranchId=P.branch_id||P.assignedBranchId||"branch-main",isRestrictedRole=["dependiente","cajero","clerk","mesero","waiter"].includes((P.role||"").toLowerCase()),he=isRestrictedRole?userBranchId:oe,ee=ge.find(we=>we.id===he)||l.find(we=>we.id===he)||ge[0]||l[0]'''

assert target_pos_branch_init in code, "target_pos_branch_init not found"
code = code.replace(target_pos_branch_init, replacement_pos_branch_init, 1)
print("Patch 2.1 (PosView strict multi-branch lock for restricted roles): OK")

# =========================================================================
# 3. RBAC IN INVENTORYVIEW
# =========================================================================
target_inv_perms = 'const m=r||$l,f=m.role==="kitchen"||m.role==="clerk",h=m.role==="admin"||m.role==="owner"||m.role?.toLowerCase()==="admin",g=m.role==="clerk"'

replacement_inv_perms = '''const m=r||$l,userRole=(m.role||"").toLowerCase().trim(),isRestricted=["dependiente","cajero","clerk","mesero","waiter"].includes(userRole),canModifyInventory=["admin","superadmin","gerente","manager","owner"].includes(userRole)&&!isRestricted,h=canModifyInventory,f=isRestricted||m.role==="kitchen",g=isRestricted'''

assert target_inv_perms in code, "target_inv_perms not found"
code = code.replace(target_inv_perms, replacement_inv_perms, 1)
print("Patch 3.1 (InventoryView RBAC permissions for admin/superadmin/gerente vs restricted): OK")

# In InventoryView table rows: wrap action buttons with h &&
target_row_actions = 'children:[n.jsxDEV("button",{type:"button",onClick:()=>{yt(_e),Se(1),tn("in_purchase")},className:"p-1.5 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 text-emerald-600 rounded-lg transition",title:"Ajuste rápido de existencias (Entrada / Merma)",children:n.jsxDEV(Xr,{className:"w-3.5 h-3.5"},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2370,columnNumber:29},void 0)},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2360,columnNumber:27},void 0),n.jsxDEV("button",{type:"button",onClick:()=>yr(_e),className:"p-1.5 hover:bg-blue-50 dark:hover:bg-blue-950/50 text-blue-600 rounded-lg transition",title:"Editar artículo",children:n.jsxDEV(ud,{className:"w-3.5 h-3.5"},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2378,columnNumber:29},void 0)},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2372,columnNumber:27},void 0),n.jsxDEV("button",{type:"button",onClick:()=>rr(_e.id,_e.name),className:"p-1.5 hover:bg-rose-50 dark:hover:bg-rose-950/50 text-rose-600 rounded-lg transition",title:"Eliminar artículo",children:n.jsxDEV(br,{className:"w-3.5 h-3.5"},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2386,columnNumber:29},void 0)},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2380,columnNumber:27},void 0)]'

replacement_row_actions = 'children:h?[n.jsxDEV("button",{type:"button",onClick:()=>{yt(_e),Se(1),tn("in_purchase")},className:"p-1.5 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 text-emerald-600 rounded-lg transition",title:"Ajuste rápido de existencias (Entrada / Merma)",children:n.jsxDEV(Xr,{className:"w-3.5 h-3.5"},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2370,columnNumber:29},void 0)},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2360,columnNumber:27},void 0),n.jsxDEV("button",{type:"button",onClick:()=>yr(_e),className:"p-1.5 hover:bg-blue-50 dark:hover:bg-blue-950/50 text-blue-600 rounded-lg transition",title:"Editar artículo",children:n.jsxDEV(ud,{className:"w-3.5 h-3.5"},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2378,columnNumber:29},void 0)},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2372,columnNumber:27},void 0),n.jsxDEV("button",{type:"button",onClick:()=>rr(_e.id,_e.name),className:"p-1.5 hover:bg-rose-50 dark:hover:bg-rose-950/50 text-rose-600 rounded-lg transition",title:"Eliminar artículo",children:n.jsxDEV(br,{className:"w-3.5 h-3.5"},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2386,columnNumber:29},void 0)},void 0,!1,{fileName:"/app/applet/src/components/InventoryView.tsx",lineNumber:2380,columnNumber:27},void 0)]:[]'

assert target_row_actions in code, "target_row_actions not found"
code = code.replace(target_row_actions, replacement_row_actions, 1)
print("Patch 3.2 (InventoryView row action buttons protected by RBAC): OK")

# =========================================================================
# 4. COMBOS CLEAN EMPTY STATE (CERO MOCKS)
# =========================================================================
target_combos_empty = 'children:"No se encontraron presentaciones de producto"'
replacement_combos_empty = 'children:"No hay combos activos registrados"'

assert target_combos_empty in code, "target_combos_empty not found"
code = code.replace(target_combos_empty, replacement_combos_empty, 1)
print("Patch 4 (Combos clean empty state): OK")

# =========================================================================
# 5. STRICT AUTHENTICATION (SUPABASE AUTH WITH PASSWORD)
# =========================================================================
# Remove PIN static bypass (se.pin===Ne||Ne==="1234"||se.role==="admin"&&Ne==="0000")
target_pin_bypass = 'if(se.pin===Ne||Ne==="1234"||se.role==="admin"&&Ne==="0000")'
replacement_pin_bypass = 'if(se.pin&&Ne&&se.pin===Ne)'

assert target_pin_bypass in code, "target_pin_bypass not found"
code = code.replace(target_pin_bypass, replacement_pin_bypass, 1)
print("Patch 5 (Removed PIN bypass, strictly match actual user pin or require password): OK")

# =========================================================================
# 6. REGISTRATION WITH COMPANY CODE & ADMIN APPROVAL WITH BRANCH ASSIGNMENT
# =========================================================================
# In joinCompany: query SELECT id FROM companies WHERE company_code = enteredCode OR id = enteredCode
target_join_comp = 'const{data:l,error:d}=await s.from("companies").select("*").eq("id",i).single();if(d||!l)throw new Error(`No se encontró ninguna empresa con el código "${i}". Verifica el código con tu administrador.`);'

replacement_join_comp = 'const{data:compList,error:d}=await s.from("companies").select("*").or(`company_code.eq.${i},id.eq.${i}`);if(d||!compList||compList.length===0)throw new Error(`Código de empresa no válido. Verifica el código "${i}" con tu administrador.`);const l=compList[0];'

assert target_join_comp in code, "target_join_comp not found"
code = code.replace(target_join_comp, replacement_join_comp, 1)
print("Patch 6.1 (Company code validation in joinCompany): OK")

# In AAe (Admin member approval): allow assigning branch_id alongside role
target_aae_approve = 'await wl.updateMemberStatusAndRole(W.id,"active",q)'
replacement_aae_approve = 'await wl.updateMemberStatusAndRole(W.id,"active",q,W.branch_id||"branch-main")'

assert target_aae_approve in code, "target_aae_approve not found"
code = code.replace(target_aae_approve, replacement_aae_approve, 1)
print("Patch 6.2 (Admin member approval assigns branch): OK")

# Update updateMemberStatusAndRole in class wl to accept branch_id
target_update_member = 'static async updateMemberStatusAndRole(t,a,r){const s=Sn(),i={status:a};r&&(i.role=r);const{data:l,error:d}=await s.from("company_members").update(i).eq("id",t).select().single();'

replacement_update_member = 'static async updateMemberStatusAndRole(t,a,r,b){const s=Sn(),i={status:a};r&&(i.role=r);b&&(i.branch_id=b);const{data:l,error:d}=await s.from("company_members").update(i).eq("id",t).select().single();'

assert target_update_member in code, "target_update_member not found"
code = code.replace(target_update_member, replacement_update_member, 1)
print("Patch 6.3 (updateMemberStatusAndRole accepts branch_id): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All architecture solutions successfully applied to assets/index-DCC2oYkl.js!")
