with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. POSView: Generate crypto.randomUUID for sales
# ---------------------------------------------------------------------------
old_an = 'An=Ge?.saleId||`sale-${Date.now()}`;'
new_an = 'An=Ge?.saleId||(typeof crypto!=="undefined"&&crypto.randomUUID?crypto.randomUUID():`sale-${Date.now()}-${Math.random().toString(36).slice(2,8)}`);'
assert old_an in code, "old_an not found"
code = code.replace(old_an, new_an, 1)
print("1. POSView: crypto.randomUUID for sale IDs applied")

# ---------------------------------------------------------------------------
# 2. POSView: Offline-First instant confirmation & immediate local stock decrement
# ---------------------------------------------------------------------------
old_pos_complete = 'N(Er),V(gs);let ts=null;if(typeof navigator!=="undefined"&&!navigator.onLine){ts={message:"OFFLINE_MODE"};window.__BISTRO_OFFLINE_SYNC__?.enqueue(Er,he,ee?.tenant_id,pi);}else{try{const Cs=Sn();const res=await Cs.from("sales").insert({id:Er.id,tenant_id:ee?.tenant_id||"biz-main",branch_id:he,sale_number:Er.saleNumber,date:Er.date,time:Er.time,subtotal:Er.subtotal,tax_amount:Er.taxAmount,tip_amount:Er.tipAmount,total_amount:Er.totalAmount,payment_method:Er.paymentMethod,status:"completed",data:Er});if(res.error){ts=res.error;window.__BISTRO_OFFLINE_SYNC__?.enqueue(Er,he,ee?.tenant_id,pi);}}catch(netErr){ts=netErr;window.__BISTRO_OFFLINE_SYNC__?.enqueue(Er,he,ee?.tenant_id,pi);}}'

new_pos_complete = 'N(Er),V(gs);window.__BISTRO_OFFLINE_SYNC__?.enqueueSale(Er,he,ee?.tenant_id,pi);'

assert old_pos_complete in code, "old_pos_complete not found"
code = code.replace(old_pos_complete, new_pos_complete, 1)
print("2. POSView: Offline-First non-blocking sales enqueue applied")

# ---------------------------------------------------------------------------
# 3. Navbar: Hook listeners for bistro_sync_status_changed & bistro_offline_sync_updated
# ---------------------------------------------------------------------------
old_nav_sub = 'S.useEffect(()=>{let Ne=!0;const De=ca.subscribe(ye=>{setTimeout(()=>{Ne&&(ge(ye.pendingCount),$(ye.isSyncing))},0)});return()=>{Ne=!1,De()}},[]);const G=async()=>{$(!0);try{E?await E():await ca.syncPendingQueue()}catch(Ne){console.warn("Sync notice:",Ne)}finally{$(!1)}}'

new_nav_sub = 'S.useEffect(()=>{let Ne=!0;const syncL=e=>{if(!Ne)return;const d=e.detail||{};if(d.pendingCount!==void 0)ge(d.pendingCount);else if(d.count!==void 0)ge(d.count);if(d.isSyncing!==void 0)$(d.isSyncing);};window.addEventListener("bistro_sync_status_changed",syncL);window.addEventListener("bistro_offline_sync_updated",syncL);const De=ca.subscribe(ye=>{setTimeout(()=>{Ne&&(ge(ye.pendingCount),$(ye.isSyncing))},0)});return()=>{Ne=!1;De();window.removeEventListener("bistro_sync_status_changed",syncL);window.removeEventListener("bistro_offline_sync_updated",syncL);}},[]);const G=async()=>{$(!0);try{if(window.__BISTRO_OFFLINE_SYNC__){await window.__BISTRO_OFFLINE_SYNC__.flushQueue();}else{E?await E():await ca.syncPendingQueue();}}catch(Ne){console.warn("Sync notice:",Ne)}finally{$(!1)}}'

assert old_nav_sub in code, "old_nav_sub not found"
code = code.replace(old_nav_sub, new_nav_sub, 1)
print("3. Navbar: sync listeners & manual trigger wired")

# ---------------------------------------------------------------------------
# 4. Navbar: Visual Connection Badge (Green, Yellow/Orange, Blinking Blue)
# ---------------------------------------------------------------------------
old_badge_chunk = 'children:u?n.jsxDEV(n.Fragment,{children:[n.jsxDEV(Uf,{className:"w-3.5 h-3.5 text-emerald-400 shrink-0"},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:445,columnNumber:21},void 0),n.jsxDEV("span",{className:"hidden md:inline text-[11px] text-emerald-400 font-semibold",children:"Online"},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:446,columnNumber:21},void 0),ae>0?n.jsxDEV("span",{className:"text-[9px] font-bold px-1 rounded-full bg-amber-500 text-slate-950 font-black",children:ae},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:448,columnNumber:23},void 0):n.jsxDEV("span",{className:"hidden xl:inline text-[9px] text-sky-300/80 font-medium",children:"Cloud"},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:452,columnNumber:23},void 0)]},void 0,!0,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:444,columnNumber:19},void 0):n.jsxDEV(n.Fragment,{children:[n.jsxDEV(PC,{className:"w-3.5 h-3.5 text-amber-400 animate-pulse shrink-0"},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:457,columnNumber:21},void 0),n.jsxDEV("span",{className:"hidden md:inline text-[11px] text-amber-400 font-bold",children:"Offline"},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:458,columnNumber:21},void 0),ae>0&&n.jsxDEV("span",{className:"text-[9px] font-bold px-1 rounded-full bg-amber-500 text-slate-950 font-black",children:ae},void 0,!1,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:460,columnNumber:23},void 0)]},void 0,!0,{fileName:"/app/applet/src/components/Navbar.tsx",lineNumber:456,columnNumber:19},void 0)}'

new_badge_chunk = 'children:Y?n.jsxDEV("span",{className:"flex items-center gap-1.5 px-2 py-0.5 rounded-lg text-xs font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30 animate-pulse",children:[n.jsxDEV("span",{className:"w-2 h-2 rounded-full bg-blue-400 animate-ping"},void 0,!1,{},void 0),n.jsxDEV("span",{className:"text-[10px] sm:text-[11px] font-semibold",children:"Sincronizando operaciones..."},void 0,!1,{},void 0)]},void 0,!0,{},void 0):(!u||ae>0)?n.jsxDEV("span",{className:"flex items-center gap-1.5 px-2 py-0.5 rounded-lg text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30",children:[n.jsxDEV("span",{className:"w-2 h-2 rounded-full bg-amber-400"},void 0,!1,{},void 0),n.jsxDEV("span",{className:"text-[10px] sm:text-[11px] font-semibold",children:["Modo Offline (",ae," pendientes)"]},void 0,!0,{},void 0)]},void 0,!0,{},void 0):n.jsxDEV("span",{className:"flex items-center gap-1.5 px-2 py-0.5 rounded-lg text-xs font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",children:[n.jsxDEV("span",{className:"w-2 h-2 rounded-full bg-emerald-400"},void 0,!1,{},void 0),n.jsxDEV("span",{className:"text-[10px] sm:text-[11px] font-semibold",children:"En línea (Sincronizado)"},void 0,!1,{},void 0)]},void 0,!0,{},void 0)'

assert old_badge_chunk in code, "old_badge_chunk not found"
code = code.replace(old_badge_chunk, new_badge_chunk, 1)
print("4. Navbar: visual connection badge states inserted")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Offline-First integration successfully completed!")
