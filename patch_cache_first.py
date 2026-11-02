with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. Inject window.__BISTRO_LOCAL_STORE__ at the top
# ---------------------------------------------------------------------------
local_store_impl = '''
  var DEFAULT_BRANCHES = [
    { id: "branch-main", name: "Almacén Central & Matriz", code: "MAT", address: "Sede Central", isMainWarehouse: true, active: true, workMode: "restaurante", colorTag: "blue" },
    { id: "branch-1792458194300-3i4l", name: "Cafeteria Calle A", code: "CCA", address: "Calle A", isMainWarehouse: false, active: true, workMode: "cafeteria", colorTag: "emerald" }
  ];

  window.__BISTRO_LOCAL_STORE__ = {
    DEFAULT_BRANCHES: DEFAULT_BRANCHES,
    getLocalBranches: function() {
      try {
        var b = localStorage.getItem("bistro_branches");
        if (b) { var p = JSON.parse(b); if (Array.isArray(p) && p.length > 0) return p; }
        var c = localStorage.getItem("cache_branches");
        if (c) { var p = JSON.parse(c); if (Array.isArray(p) && p.length > 0) return p; }
        var l = localStorage.getItem("bistro_local_branches");
        if (l) { var p = JSON.parse(l); if (Array.isArray(p) && p.length > 0) return p; }
      } catch(e) {}
      return DEFAULT_BRANCHES;
    },
    saveLocalBranches: function(branches) {
      if (!Array.isArray(branches) || branches.length === 0) return;
      try {
        var str = JSON.stringify(branches);
        localStorage.setItem("bistro_branches", str);
        localStorage.setItem("cache_branches", str);
        localStorage.setItem("bistro_local_branches", str);
      } catch(e) {}
    },
    getLocalInventory: function(branchId) {
      var target = branchId || "branch-1792458194300-3i4l";
      try {
        var bCat = localStorage.getItem("bistro_local_catalog_" + target);
        if (bCat) { var p = JSON.parse(bCat); if (Array.isArray(p) && p.length > 0) return p; }
        var inv = localStorage.getItem("bistro_inventory");
        if (inv) { var p = JSON.parse(inv); if (Array.isArray(p) && p.length > 0) return p; }
        var cInv = localStorage.getItem("cache_inventory");
        if (cInv) { var p = JSON.parse(cInv); if (Array.isArray(p) && p.length > 0) return p; }
        for (var i = 0; i < localStorage.length; i++) {
          var k = localStorage.key(i);
          if (k && k.startsWith("bistro_local_catalog_")) {
            var raw = localStorage.getItem(k);
            if (raw) { var p = JSON.parse(raw); if (Array.isArray(p) && p.length > 0) return p; }
          }
        }
      } catch(e) {}
      return [];
    },
    saveLocalInventory: function(branchId, items) {
      if (!Array.isArray(items)) return;
      var target = branchId || "branch-1792458194300-3i4l";
      try {
        var str = JSON.stringify(items);
        localStorage.setItem("bistro_local_catalog_" + target, str);
        localStorage.setItem("bistro_inventory", str);
        localStorage.setItem("cache_inventory", str);
      } catch(e) {}
    }
  };
'''

# Place local_store_impl right inside the top wrapper
top_target = 'if (typeof window === "undefined") return;'
assert top_target in code, "top_target not found"
code = code.replace(top_target, top_target + local_store_impl, 1)
print("1. window.__BISTRO_LOCAL_STORE__ injected at top")

# ---------------------------------------------------------------------------
# 2. Update du and Rp() in useBranches hook: Cache-First
# ---------------------------------------------------------------------------
old_du_init = 'let du=(()=>{if(typeof localStorage>"u")return pp;try{const e=localStorage.getItem("bistro_branches");if(e){const a=JSON.parse(e);if(Array.isArray(a)&&a.length>0)return a}const t=localStorage.getItem("cache_branches");if(t){const a=JSON.parse(t);if(Array.isArray(a)&&a.length>0)return a}}catch{}return pp})();'

new_du_init = 'let du=(()=>{if(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)return window.__BISTRO_LOCAL_STORE__.getLocalBranches();if(typeof localStorage>"u")return pp;try{const e=localStorage.getItem("bistro_branches");if(e){const a=JSON.parse(e);if(Array.isArray(a)&&a.length>0)return a}const t=localStorage.getItem("cache_branches");if(t){const a=JSON.parse(t);if(Array.isArray(a)&&a.length>0)return a}}catch{}return window.__BISTRO_LOCAL_STORE__?window.__BISTRO_LOCAL_STORE__.DEFAULT_BRANCHES:pp})();'

assert old_du_init in code, "old_du_init not found"
code = code.replace(old_du_init, new_du_init, 1)
print("2. du initialized with Cache-First getLocalBranches()")

# Update Rp() state initialization & refreshBranches
old_rp_state = 'function Rp(){const[e,t]=S.useState(du),'
new_rp_state = 'function Rp(){const[e,t]=S.useState(()=>(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches():du),'
assert old_rp_state in code, "old_rp_state not found"
code = code.replace(old_rp_state, new_rp_state, 1)

old_rp_ref = 'i=S.useCallback(async()=>{try{const f=await Zt.getBranches();if(Array.isArray(f)&&f.length>0)return Px(f),f}catch(f){console.warn("[useBranches] refreshBranches notice:",f)}return du},[])'
new_rp_ref = 'i=S.useCallback(async()=>{try{const f=await Zt.getBranches();if(Array.isArray(f)&&f.length>0){typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__?.saveLocalBranches(f);return Px(f),f;}}catch(f){console.warn("[useBranches] refreshBranches notice:",f);}const fallbackBranches=(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches():du;Px(fallbackBranches);return fallbackBranches;},[])'
assert old_rp_ref in code, "old_rp_ref not found"
code = code.replace(old_rp_ref, new_rp_ref, 1)
print("3. Rp() hook cache-first state and refreshBranches updated")

# ---------------------------------------------------------------------------
# 3. DynamicPurchaseModal (V4e): Cache-First branch selector
# ---------------------------------------------------------------------------
old_v4e_branch_state = '[G,W]=S.useState("aprobada"),[q,xe]=S.useState([]);Wv.useEffect(()=>{async function re(){if(En())try{const me=Sn(),{data:ze,error:Ve}=await me.from("branches").select("*");if(!Ve&&Array.isArray(ze)&&ze.length>0){const st=ze.filter(vt=>{const lt=vt.is_active!==void 0?vt.is_active:vt.active!==void 0?vt.active:!0,We=vt.raw_data&&vt.raw_data.active!==void 0?vt.raw_data.active:!0;return lt!==!1&&We!==!1}).map(vt=>({id:String(vt.id),name:String(vt.name||"Sucursal")}));if(st.length>0){xe(st),he(vt=>vt&&st.some(lt=>lt.id===vt)?vt:st[0].id);return}}}catch(me){console.warn("[DynamicPurchaseModal] Error loading branches:",me)}const fe=(i&&i.length>0?i:m).filter(me=>me.active!==!1);fe.length>0&&(xe(fe.map(me=>({id:me.id,name:me.name}))),he(me=>me&&fe.some(ze=>ze.id===me)?me:fe[0].id))}re();'

new_v4e_branch_state = '[G,W]=S.useState("aprobada"),[q,xe]=S.useState(()=>{const cached=(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches():(i&&i.length>0?i:m);return(cached||[]).filter(me=>me.active!==!1).map(me=>({id:String(me.id),name:String(me.name||"Sucursal")}));});Wv.useEffect(()=>{async function re(){const localB=(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches():(i&&i.length>0?i:m);const localActive=(localB||[]).filter(me=>me.active!==!1).map(me=>({id:String(me.id),name:String(me.name||"Sucursal")}));if(localActive.length>0){xe(localActive);he(vt=>vt&&localActive.some(lt=>lt.id===vt)?vt:localActive[0].id);}if(typeof navigator!=="undefined"&&navigator.onLine&&En()){try{const me=Sn(),{data:ze,error:Ve}=await me.from("branches").select("*");if(!Ve&&Array.isArray(ze)&&ze.length>0){const st=ze.filter(vt=>{const lt=vt.is_active!==void 0?vt.is_active:vt.active!==void 0?vt.active:!0,We=vt.raw_data&&vt.raw_data.active!==void 0?vt.raw_data.active:!0;return lt!==!1&&We!==!1}).map(vt=>({id:String(vt.id),name:String(vt.name||"Sucursal")}));if(st.length>0){xe(st);he(vt=>vt&&st.some(lt=>lt.id===vt)?vt:st[0].id);typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__?.saveLocalBranches(ze);return;}}}catch(me){console.warn("[DynamicPurchaseModal] Offline notice:",me);}}}re();'

assert old_v4e_branch_state in code, "old_v4e_branch_state not found"
code = code.replace(old_v4e_branch_state, new_v4e_branch_state, 1)
print("4. DynamicPurchaseModal: Cache-First branch selector applied")

# ---------------------------------------------------------------------------
# 4. InvoicesView (D4e): Cache-First branch selector
# ---------------------------------------------------------------------------
old_d4e_branch_state = 'const{activeBranches:d}=Rp(),[u,m]=S.useState([]),[f,h]=S.useState("invoices"),[g,N]=S.useState(""),[V,E]=S.useState("all"),[k,j]=S.useState(""),[I,M]=S.useState("all");Wv.useEffect(()=>{let Ve=!0;async function st(){if(En())try{const lt=Sn(),{data:We,error:ut}=await lt.from("branches").select("*");if(!ut&&Array.isArray(We)&&We.length>0){const wt=We.filter(Te=>{const kt=Te.is_active!==void 0?Te.is_active:Te.active!==void 0?Te.active:!0,at=Te.raw_data&&Te.raw_data.active!==void 0?Te.raw_data.active:!0;return kt!==!1&&at!==!1}).map(Te=>({id:String(Te.id),name:String(Te.name||"Sucursal")}));if(Ve&&wt.length>0){m(wt),N(Te=>Te&&wt.some(kt=>kt.id===Te)?Te:wt[0].id);return}}}catch{}const vt=(s&&s.length>0?s:d).filter(lt=>lt.active!==!1);vt.length>0&&(m(vt.map(lt=>({id:lt.id,name:lt.name}))),N(lt=>lt&&vt.some(We=>We.id===lt)?lt:vt[0].id))}st()},[s,d]);'

new_d4e_branch_state = 'const{activeBranches:d}=Rp(),[u,m]=S.useState(()=>{const cached=(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches():d;return(cached||[]).filter(lt=>lt.active!==!1).map(lt=>({id:String(lt.id),name:String(lt.name||"Sucursal")}));}),[f,h]=S.useState("invoices"),[g,N]=S.useState(()=>((typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches()[0]?.id:"branch-main")),[V,E]=S.useState("all"),[k,j]=S.useState(""),[I,M]=S.useState("all");Wv.useEffect(()=>{let Ve=!0;async function st(){const localB=(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalBranches():(s&&s.length>0?s:d);const vt=(localB||[]).filter(lt=>lt.active!==!1).map(lt=>({id:String(lt.id),name:String(lt.name||"Sucursal")}));if(Ve&&vt.length>0){m(vt);N(lt=>lt&&vt.some(We=>We.id===lt)?lt:vt[0].id);}if(typeof navigator!=="undefined"&&navigator.onLine&&En()){try{const lt=Sn(),{data:We,error:ut}=await lt.from("branches").select("*");if(!ut&&Array.isArray(We)&&We.length>0){const wt=We.filter(Te=>{const kt=Te.is_active!==void 0?Te.is_active:Te.active!==void 0?Te.active:!0,at=Te.raw_data&&Te.raw_data.active!==void 0?Te.raw_data.active:!0;return kt!==!1&&at!==!1}).map(Te=>({id:String(Te.id),name:String(Te.name||"Sucursal")}));if(Ve&&wt.length>0){m(wt);N(Te=>Te&&wt.some(kt=>kt.id===Te)?Te:wt[0].id);typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__?.saveLocalBranches(We);return;}}}catch(err){console.warn("[InvoicesView] Offline notice:",err);}}}st();},[s,d]);'

assert old_d4e_branch_state in code, "old_d4e_branch_state not found"
code = code.replace(old_d4e_branch_state, new_d4e_branch_state, 1)
print("5. InvoicesView: Cache-First branch selector applied")

# ---------------------------------------------------------------------------
# 5. InventoryView (W7e): Cache-First stock map and offline resilience
# ---------------------------------------------------------------------------
old_w7e_stock = '[E,k]=S.useState({}),[isLoadingStock,setIsLoadingStock]=S.useState(!0);S.useEffect(()=>{let _e=!0;const targetBr=userRole!=="admin"?(m.branch_id||m.assignedBranchId||"branch-1792458194300-3i4l"):null;Zt.getBranchInventory(targetBr).then(Pe=>{if(!_e||!Array.isArray(Pe))return;const be={};Pe.forEach(Ie=>{const key=`${Ie.branch_id}_${Ie.item_id}`;if(Ie.branch_id&&Ie.item_id&&be[key]===void 0){be[key]=Number(Ie.current_stock)||0;}});k(be);setIsLoadingStock(!1);}).catch(Pe=>{console.warn("[InventoryView] getBranchInventory notice:",Pe);_e&&setIsLoadingStock(!1);});'

new_w7e_stock = '[E,k]=S.useState(()=>{const initialMap={};try{const targetBr=userRole!=="admin"?(m.branch_id||m.assignedBranchId||"branch-1792458194300-3i4l"):"branch-main";const cached=(typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__)?window.__BISTRO_LOCAL_STORE__.getLocalInventory(targetBr):[];(cached||[]).forEach(it=>{const sid=it.id||it.item_id;if(sid){const st=Number(it.current_stock??it.stock??0);initialMap[`${targetBr}_${sid}`]=st;initialMap[`all_${sid}`]=st;initialMap[`branch-main_${sid}`]=st;initialMap[`branch-1792458194300-3i4l_${sid}`]=st;}});}catch(e){}return initialMap;}),[isLoadingStock,setIsLoadingStock]=S.useState(!1);S.useEffect(()=>{let _e=!0;const targetBr=userRole!=="admin"?(m.branch_id||m.assignedBranchId||"branch-1792458194300-3i4l"):null;if(typeof navigator!=="undefined"&&!navigator.onLine){setIsLoadingStock(!1);return;}Zt.getBranchInventory(targetBr).then(Pe=>{if(!_e||!Array.isArray(Pe))return;const be={...E};Pe.forEach(Ie=>{const key=`${Ie.branch_id}_${Ie.item_id}`;if(Ie.branch_id&&Ie.item_id){be[key]=Number(Ie.current_stock)||0;be[`all_${Ie.item_id}`]=Number(Ie.current_stock)||0;}});k(be);setIsLoadingStock(!1);}).catch(Pe=>{console.warn("[InventoryView] getBranchInventory offline notice:",Pe);_e&&setIsLoadingStock(!1);});'

assert old_w7e_stock in code, "old_w7e_stock not found"
code = code.replace(old_w7e_stock, new_w7e_stock, 1)
print("6. InventoryView: Cache-First stock map applied")

# ---------------------------------------------------------------------------
# 6. Tx in App.tsx: Remove isMockId filter on inventory & branches
# ---------------------------------------------------------------------------
old_tx_filter = 'const isMockId=x=>{const id=String(x?.id||"");return id.startsWith("mock-")||id.startsWith("prod-")||id.startsWith("rec-")||id.startsWith("ing-")};const Tx=(e,t,a)=>{if(typeof localStorage>"u")return[];const s=localStorage.getItem(`cache_${e}`);if(s!==null)try{const l=JSON.parse(s);if(Array.isArray(l)){const c=l.filter(x=>!isMockId(x));if(c.length>0||l.length===0)return c}}catch{}const i=localStorage.getItem(t);if(i!==null)try{const l=JSON.parse(i);if(Array.isArray(l)){const c=l.filter(x=>!isMockId(x));if(c.length>0||l.length===0)return c}}catch{}return[]};'

new_tx_filter = 'const isMockId=x=>{const id=String(x?.id||"");return id.startsWith("mock-dummy-");};const Tx=(e,t,a)=>{if(typeof localStorage>"u")return a||[];const s=localStorage.getItem(`cache_${e}`);if(s!==null)try{const l=JSON.parse(s);if(Array.isArray(l)&&l.length>0)return l;}catch{}const i=localStorage.getItem(t);if(i!==null)try{const l=JSON.parse(i);if(Array.isArray(l)&&l.length>0)return l;}catch{}if(e==="inventory"&&typeof window!=="undefined"&&window.__BISTRO_LOCAL_STORE__){const loc=window.__BISTRO_LOCAL_STORE__.getLocalInventory();if(loc.length>0)return loc;}return a||[];};'

assert old_tx_filter in code, "old_tx_filter not found"
code = code.replace(old_tx_filter, new_tx_filter, 1)
print("7. Tx: isMockId destructive filter removed and fallback restored")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All Cache-First / Stale-While-Revalidate patches cleanly applied!")
