with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

start_marker = 'n.jsxDEV("div",{className:"relative mt-1",children:[(()=>{const norm=s=>'
end_marker = 'fe.id))})]})();})()]})'

pos_start = code.find(start_marker)
assert pos_start != -1, 'start_marker not found'
pos_end = code.find(end_marker, pos_start)
assert pos_end != -1, 'end_marker not found'
pos_end += len(end_marker)

replacement = '''n.jsxDEV("div",{className:"relative mt-1",children:(()=>{const norm=s=>(s||"").normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").toLowerCase().trim(),q=norm(re.name),matchedItem=a.find(fe=>fe.id===re.matchedInventoryId),matches=q?a.filter(fe=>norm(fe.name).includes(q)||norm(fe.sku).includes(q)):[];if(matchedItem)return n.jsxDEV("div",{className:"flex items-center justify-between p-1.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-700 rounded-lg text-[10px] text-emerald-800 dark:text-emerald-300",children:[n.jsxDEV("span",{className:"truncate font-bold",children:[matchedItem.name," (Stock: ",matchedItem.currentStock," ",matchedItem.unit," • Costo: ",Et(matchedItem.costPerUnit||matchedItem.cost_per_unit||matchedItem.costCUP||0,s),")"]},void 0,!0),n.jsxDEV("button",{type:"button",onClick:()=>ye(re.id,""),className:"text-emerald-600 hover:text-emerald-900 font-bold ml-1 px-1",title:"Desvincular"},children:"✕"},void 0,!1)]},void 0,!0);if(matches.length>0)return n.jsxDEV("div",{className:"max-h-40 overflow-y-auto space-y-1 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg p-1 shadow-lg z-20 text-[10px]",children:matches.slice(0,10).map(fe=>n.jsxDEV("button",{type:"button",onClick:()=>ye(re.id,fe.id),className:"w-full text-left px-2 py-1 rounded hover:bg-emerald-50 dark:hover:bg-emerald-900/40 flex items-center justify-between gap-1 transition-colors",children:[n.jsxDEV("span",{className:"font-bold truncate text-slate-800 dark:text-slate-100",children:[fe.name,fe.sku?" ("+fe.sku+")":""]},void 0,!0),n.jsxDEV("span",{className:"text-slate-500 text-[9px] shrink-0",children:[fe.currentStock," ",fe.unit," • ",Et(fe.costPerUnit||fe.cost_per_unit||fe.costCUP||0,s)]},void 0,!0)]},fe.id,!0))},void 0,!1);return null})()},void 0,!1,{fileName:"/app/applet/src/components/DynamicPurchaseModal.tsx",lineNumber:508,columnNumber:25},void 0)'''

code = code[:pos_start] + replacement + code[pos_end:]

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print('Updated bundle successfully!')
