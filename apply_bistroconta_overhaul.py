import re

with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Initial bundle length:", len(code))

# =========================================================================
# PATCH 1: Eradicate Mock Data from bx to Ck
# =========================================================================
pos_bx = code.find('bx=[{id:"inv-item-14"')
pos_Ck_end = code.find(';function XZ()', 449000)

assert pos_bx != -1, "bx not found"
assert pos_Ck_end != -1, "Ck end not found"

clean_mock_replacement = (
    'bx=[],M4=[],oI=[],KZ=[],kk=[],Sk=[],iw=[],ow=[],R4=[],lI=[],QZ=[],jk=[],lw=[],'
    'T4={month:new Date().toISOString().slice(0,7),coffeeSales:0,foodSales:0,pastrySales:0,drinksSales:0,deliverySales:0,totalRevenue:0,'
    'coffeeCost:0,dairyCost:0,foodCost:0,packagingCost:0,otherSuppliesCost:0,totalCOGS:0,grossMargin:0,grossMarginPct:0,foodCostPct:0,'
    'baristaSalaries:0,kitchenSalaries:0,serviceSalaries:0,payrollTaxes:0,totalLaborCost:0,laborCostPct:0,primeCost:0,primeCostPct:0,'
    'rent:0,utilitiesElectricity:0,utilitiesWaterGas:0,maintenanceEspresso:0,posSoftwareFees:0,marketing:0,cleaningSupplies:0,'
    'deliveryCommissions:0,otherOpex:0,totalOpex:0,ebitda:0,ebitdaMarginPct:0,depreciation:0,taxes:0,netProfit:0,netMarginPct:0},'
    'qU=[],cI=[],YZ=[],Ck=[]'
)

code = code[:pos_bx] + clean_mock_replacement + code[pos_Ck_end:]
print("Patch 1 (Eradicate mock arrays): OK. New length:", len(code))

# =========================================================================
# PATCH 2: Patch Tx to clean localStorage cache and never return mock fallbacks
# =========================================================================
target_Tx = 'const Tx=(e,t,a)=>{if(typeof localStorage>"u")return[];const r=localStorage.getItem("bistro_clean_mode")==="true",s=localStorage.getItem(`cache_${e}`);if(s!==null)try{const l=JSON.parse(s);if(Array.isArray(l))return l}catch{}const i=localStorage.getItem(t);if(i!==null)try{const l=JSON.parse(i);if(Array.isArray(l))return l}catch{}return r?[]:typeof navigator<"u"&&!navigator.onLine?a:[]};'

replacement_Tx = 'const isMockId=x=>{if(!x)return!1;const id=String(x.id||x.saleNumber||x.expenseNumber||x.orderNumber||"");return id.startsWith("sale-20")||id.startsWith("exp-30")||id.startsWith("k-ord-")||id.startsWith("cash-10")||id.startsWith("shift-arch-")||id.startsWith("ipv-shift-")||id.startsWith("prs-caja-")||id.startsWith("w-1")||id.startsWith("w-2")||id.startsWith("aud-1")||id.startsWith("inv-01")||id.startsWith("rec-")||id.startsWith("ing-")};const Tx=(e,t,a)=>{if(typeof localStorage>"u")return[];const s=localStorage.getItem(`cache_${e}`);if(s!==null)try{const l=JSON.parse(s);if(Array.isArray(l)){const c=l.filter(x=>!isMockId(x));if(c.length>0||l.length===0)return c}}catch{}const i=localStorage.getItem(t);if(i!==null)try{const l=JSON.parse(i);if(Array.isArray(l)){const c=l.filter(x=>!isMockId(x));if(c.length>0||l.length===0)return c}}catch{}return[]};'

assert target_Tx in code, "target_Tx not found"
code = code.replace(target_Tx, replacement_Tx, 1)
print("Patch 2 (Tx clean cache and no mock fallback): OK")

# =========================================================================
# PATCH 3: Patch App.tsx state initializers to filter out mock IDs from localStorage
# =========================================================================
target_korders = 'return kk.map(Ie=>({...Ie,status:"entregada"}))'
if target_korders in code:
    code = code.replace(target_korders, 'return[]', 1)
    print("Patch 3.1 (kitchen_orders fallback): OK")

target_recipes_init = 'const be=localStorage.getItem("bistro_recipes");return be?JSON.parse(be):ow'
if target_recipes_init in code:
    code = code.replace(target_recipes_init, 'const be=localStorage.getItem("bistro_recipes");if(be)try{const l=JSON.parse(be);if(Array.isArray(l))return l.filter(x=>!isMockId(x))}catch{}return[]', 1)
    print("Patch 3.2 (recipes init): OK")

target_ing_init = 'const be=localStorage.getItem("bistro_ingredients");return be?JSON.parse(be):iw'
if target_ing_init in code:
    code = code.replace(target_ing_init, 'const be=localStorage.getItem("bistro_ingredients");if(be)try{const l=JSON.parse(be);if(Array.isArray(l))return l.filter(x=>!isMockId(x))}catch{}return[]', 1)
    print("Patch 3.3 (ingredients init): OK")

# =========================================================================
# PATCH 4: Remove Fake Shift injection in IpvVarianceTrendChart.tsx (gAe)
# =========================================================================
pos_fake = code.find('if(L.length<10){const q=[],xe=r.find(se=>se.id===f)')
assert pos_fake != -1, "pos_fake not found"
pos_fake_end = code.find('L=[...L,...q]}', pos_fake)
assert pos_fake_end != -1, "pos_fake_end not found"
pos_fake_end += len('L=[...L,...q]}')

code = code[:pos_fake] + '/* no fake shifts */' + code[pos_fake_end:]
print("Patch 4.1 (Remove fake shifts in gAe): OK")

# Top recurring items only if real shifts exist
target_top_recurring = 'topRecurringItems:Ee'
pos_tr = code.find(target_top_recurring, pos_fake - 100)
if pos_tr != -1:
    code = code[:pos_tr] + 'topRecurringItems:L.length>0?Ee:[]' + code[pos_tr + len(target_top_recurring):]
    print("Patch 4.2 (topRecurringItems conditioned): OK")

# Empty state in gAe when k.length === 0
target_gae_chart = '{className:"w-full h-72",children:n.jsxDEV($f,{width:"100%",height:"100%",children:n.jsxDEV(G8,{data:k,'
assert target_gae_chart in code, "target_gae_chart not found"
replacement_gae_chart = '{className:"w-full h-72",children:k.length===0?n.jsxDEV("div",{className:"w-full h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 dark:text-slate-500",children:[n.jsxDEV("div",{className:"text-3xl mb-2",children:"📊"}),n.jsxDEV("span",{className:"font-bold text-sm text-slate-700 dark:text-slate-300",children:"Sin datos de auditoría registrados"},void 0,!1),n.jsxDEV("span",{className:"text-xs text-slate-400 mt-1",children:"Inicie turnos y registre conteos físicos para auditar el inventario teórico vs real."},void 0,!1)]}):n.jsxDEV($f,{width:"100%",height:"100%",children:n.jsxDEV(G8,{data:k,'
code = code.replace(target_gae_chart, replacement_gae_chart, 1)
print("Patch 4.3 (gAe empty state): OK")

# =========================================================================
# PATCH 5: DynamicPurchaseModal Autocomplete Combobox
# =========================================================================
# Replace the select in DynamicPurchaseModal with a searchable combobox
target_purch_select = 'n.jsxDEV("select",{value:re.matchedInventoryId||"",onChange:fe=>ye(re.id,fe.target.value),className:"w-full text-[10px] px-2 py-1 bg-slate-100 dark:bg-slate-700/60 border border-slate-200 dark:border-slate-600 rounded text-slate-600 dark:text-slate-300",children:[n.jsxDEV("option",{value:"",children:"Vincular con inventario existente..."},void 0,!1,{fileName:"/app/applet/src/components/DynamicPurchaseModal.tsx",lineNumber:513,columnNumber:27},void 0),a.map(fe=>n.jsxDEV("option",{value:fe.id,children:[fe.name," (Stock: ",fe.currentStock," ",fe.unit," - Costo: ",Et(fe.costPerUnit,s),")"]},fe.id,!0,{fileName:"/app/applet/src/components/DynamicPurchaseModal.tsx",lineNumber:515,columnNumber:29},void 0))]},void 0,!0,{fileName:"/app/applet/src/components/DynamicPurchaseModal.tsx",lineNumber:508,columnNumber:25},void 0)'

assert target_purch_select in code, "target_purch_select not found"

replacement_purch_combobox = '''n.jsxDEV("div",{className:"relative mt-1",children:[(()=>{const norm=s=>(s||"").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase().trim();const q=norm(re.name);const matchedItem=a.find(fe=>fe.id===re.matchedInventoryId);const matches=q?a.filter(fe=>norm(fe.name).includes(q)||norm(fe.sku).includes(q)):[];return n.jsxDEV(n.Fragment,{children:[matchedItem?n.jsxDEV("div",{className:"flex items-center justify-between p-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-700 rounded-lg text-[10px] text-emerald-800 dark:text-emerald-300",children:[n.jsxDEV("span",{className:"truncate font-bold",children:[matchedItem.name," (Stock: ",matchedItem.currentStock," ",matchedItem.unit," • Costo: ",Et(matchedItem.costPerUnit||matchedItem.cost_per_unit||matchedItem.costCUP||0,s),")"]}),n.jsxDEV("button",{type:"button",onClick:()=>ye(re.id,""),className:"text-emerald-600 hover:text-emerald-900 font-bold ml-1 px-1",title:"Desvincular"},children:"✕"})]}):matches.length>0&&n.jsxDEV("div",{className:"max-h-40 overflow-y-auto space-y-1 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg p-1 shadow-lg z-20 text-[10px]",children:matches.slice(0,10).map(fe=>n.jsxDEV("button",{type:"button",onClick:()=>ye(re.id,fe.id),className:"w-full text-left px-2 py-1 rounded hover:bg-emerald-50 dark:hover:bg-emerald-900/40 flex items-center justify-between gap-1 transition-colors",children:[n.jsxDEV("span",{className:"font-bold truncate text-slate-800 dark:text-slate-100",children:[fe.name,fe.sku?` (${fe.sku})`:null]}),n.jsxDEV("span",{className:"text-slate-500 text-[9px] shrink-0",children:[fe.currentStock," ",fe.unit," • ",Et(fe.costPerUnit||fe.cost_per_unit||fe.costCUP||0,s)]})]},fe.id))})]})();})()]})'''

code = code.replace(target_purch_select, replacement_purch_combobox, 1)
print("Patch 5 (DynamicPurchaseModal Autocomplete Combobox): OK")

# =========================================================================
# PATCH 6: RecipeCostingView ingredient search onFocus select
# =========================================================================
target_rcv_search = 'placeholder:"Buscar producto o insumo por nombre, categoría o unidad...",value:kt,onChange:Ze=>at(Ze.target.value)'
if target_rcv_search in code:
    code = code.replace(target_rcv_search, 'placeholder:"Buscar producto o insumo por nombre, categoría o unidad...",value:kt,onFocus:Ze=>Ze.target.select(),onChange:Ze=>at(Ze.target.value)', 1)
    print("Patch 6 (RecipeCostingView ingredient search onFocus): OK")

# =========================================================================
# PATCH 7: InventoryView stock adjustment modal (Bt &&) interactive product combobox
# =========================================================================
target_inv_adjust_header = 'n.jsxDEV("div",{className:"p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700",children:[n.jsxDEV("div",{className:"font-bold text-slate-900 dark:text-white",children:Bt.name}'
if target_inv_adjust_header in code:
    replacement_inv_adjust_header = '''n.jsxDEV("div",{className:"p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 space-y-2",children:[n.jsxDEV("div",{className:"space-y-1",children:[n.jsxDEV("label",{className:"block text-[10px] font-bold text-slate-500 uppercase",children:"Producto Seleccionado / Cambiar Producto:"}),n.jsxDEV("input",{type:"text",defaultValue:Bt.name,key:Bt.id,onFocus:e=>e.target.select(),placeholder:"Buscar otro producto para ajustar...",onChange:e=>{const q=(e.target.value||"").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase().trim();if(q){const found=wt.find(it=>(it.name||"").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase().includes(q)||(it.sku||"").toLowerCase().includes(q));if(found&&found.id!==Bt.id){yt(found);}}},className:"w-full px-2.5 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg text-xs font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 focus:outline-none"}),n.jsxDEV("div",{className:"font-bold text-slate-900 dark:text-white text-sm",children:Bt.name})]})'''
    code = code.replace(target_inv_adjust_header, replacement_inv_adjust_header, 1)
    print("Patch 7 (InventoryView stock adjustment combobox): OK")

# =========================================================================
# PATCH 8: ProductPresentationsConfig onFocus select
# =========================================================================
target_pp_search = 'placeholder:"Buscar producto, cerveza, refresco, ingrediente, receta o SKU...",value:$,onChange:le=>ae(le.target.value)'
if target_pp_search in code:
    code = code.replace(target_pp_search, 'placeholder:"Buscar producto, cerveza, refresco, ingrediente, receta o SKU...",value:$,onFocus:le=>le.target.select(),onChange:le=>ae(le.target.value)', 1)
    print("Patch 8 (ProductPresentationsConfig search onFocus): OK")

# =========================================================================
# PATCH 9: DashboardView Live Food Cost, Expenses & Strict 2 Decimals
# =========================================================================
# 9.1 Insert liveStats calculation inside sDe
target_sde_v = 'const V=_p(e&&e.length>0?e[e.length-1]||e[0]:null),E=_p(e&&e.length>1?e[e.length-2]:V),'
assert target_sde_v in code, "target_sde_v not found"

replacement_sde_v = '''const V=_p(e&&e.length>0?e[e.length-1]||e[0]:null),E=_p(e&&e.length>1?e[e.length-2]:V);const liveStats=S.useMemo(()=>{let liveFoodCost=0,liveSalesRev=0;(i||[]).forEach(sale=>{if(sale.isCancelled||sale.status==="cancelled")return;liveSalesRev+=Number(sale.totalAmount||sale.amountCUP||0);if(sale.totalCostCUP&&Number(sale.totalCostCUP)>0){liveFoodCost+=Number(sale.totalCostCUP)}else if(Array.isArray(sale.itemsList)&&sale.itemsList.length>0){sale.itemsList.forEach(item=>{const itemQty=Number(item.quantity||1);const itemCost=Number(item.cost??item.unitCost??item.cost_per_portion??0);if(itemCost>0){liveFoodCost+=itemCost*itemQty}else{const rec=(t||[]).find(r=>r.id===item.recipeId||(r.name||"").toLowerCase().trim()===(item.name||"").toLowerCase().trim());if(rec&&Array.isArray(rec.ingredients)&&rec.ingredients.length>0){let rc=0;rec.ingredients.forEach(ing=>{const ingId=String(ing.ingredientId||ing.inventoryId||ing.id||"");const ingName=String(ing.ingredientName||ing.name||"").toLowerCase().trim();const inv=(d||[]).find(it=>it.id===ingId||(it.name||"").toLowerCase().trim()===ingName);const uCost=Number(inv?(inv.costPerUnit||inv.cost_per_unit||inv.costCUP||0):(ing.costPerUnit||ing.cost_per_unit||0));rc+=Number(ing.quantity||0)*uCost});const yP=Number(rec.portionYield||rec.portions||1)||1;liveFoodCost+=(rc/yP)*itemQty}else{const inv=(d||[]).find(it=>it.id===item.recipeId||(it.name||"").toLowerCase().trim()===(item.name||"").toLowerCase().trim());if(inv)liveFoodCost+=Number(inv.costPerUnit||inv.cost_per_unit||inv.costCUP||0)*itemQty}}})}});let expInsumos=0,opExpenses=0;(l||[]).forEach(exp=>{const amt=Number(exp.amount||exp.amountCUP||0);const cat=String(exp.category||"").toLowerCase();const cnp=String(exp.concept||"").toLowerCase();if(cat.includes("cogs")||cat.includes("bienes vendidos")||cnp.includes("insumo")||cnp.includes("materia prima")){expInsumos+=amt}else{opExpenses+=amt}});const rev=liveSalesRev>0?liveSalesRev:Number(V.totalRevenue||0);const cogs=liveFoodCost>0?liveFoodCost:(expInsumos>0?expInsumos:Number(V.totalCOGS||0));const opex=opExpenses>0?opExpenses:(Number(V.totalLaborCost||0)+Number(V.totalOpex||0));const grossProfit=rev-cogs;const netProfit=grossProfit-opex;const foodCostPct=rev>0?(cogs/rev)*100:0;const netMarginPct=rev>0?(netProfit/rev)*100:0;return{rev,cogs,opex,grossProfit,netProfit,foodCostPct,netMarginPct}},[i,l,t,d,V]);'''

code = code.replace(target_sde_v, replacement_sde_v, 1)
print("Patch 9.1 (liveStats calculation in DashboardView): OK")

# 9.2 Update KPI cards in DashboardView to use 2 decimals and liveStats
card_replacements = [
    ('children:Et(V.totalRevenue,s,0)', 'children:Et(liveStats.rev,s,2)'),
    ('children:Et(V.totalCOGS,s,0)', 'children:Et(liveStats.cogs,s,2)'),
    ('children:Et(V.totalLaborCost+V.totalOpex,s,0)', 'children:Et(liveStats.opex,s,2)'),
    ('children:Et(V.netProfit,s,0)', 'children:Et(liveStats.netProfit,s,2)'),
    ('children:ar(V.foodCostPct,1)', 'children:ar(liveStats.foodCostPct,1)'),
    ('children:ar(V.netMarginPct,1)', 'children:ar(liveStats.netMarginPct,1)'),
]

for old_s, new_s in card_replacements:
    assert old_s in code, f"Could not find {old_s}"
    code = code.replace(old_s, new_s, 1)
    print(f"Patch 9.2 ({old_s} -> {new_s}): OK")

# 9.3 Remove mock dates from F today's summary in DashboardView
target_f_date = 'Ke=i.filter(We=>We.date===ye||We.date==="2026-08-17"||We.date==="2026-08-26")'
if target_f_date in code:
    code = code.replace(target_f_date, 'Ke=i.filter(We=>We.date===ye&&!We.isCancelled&&We.status!=="cancelled")', 1)
    print("Patch 9.3 (Remove mock dates from today sales summary in DashboardView): OK")

# =========================================================================
# PATCH 10: DashboardRawMaterialShiftKPI mock dates removal
# =========================================================================
target_raw_dates = 'return Ee.date===I||Ee.date==="2026-08-17"||Ee.date==="2026-08-26"'
while target_raw_dates in code:
    code = code.replace(target_raw_dates, 'return Ee.date===I', 1)
    print("Patch 10 (Remove mock dates in DashboardRawMaterialShiftKPI): OK")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All BistroConta overhaul patches successfully applied to assets/index-DCC2oYkl.js!")
