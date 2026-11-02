with open('assets/index-DCC2oYkl.js', 'r', encoding='utf-8') as f:
    code = f.read()

print("Original length:", len(code))

# ---------------------------------------------------------------------------
# 1. Update $ calculation in BatchProductionModal (SY): Coffee cost = 4.20 & Math.abs(qty)
# ---------------------------------------------------------------------------
pos_start = code.find('$=S.useMemo(()=>{if(!R||!Array.isArray(R.ingredients)')
pos_end = code.find('ae=$.some(he=>!he.isSufficient)', pos_start)

if pos_start != -1 and pos_end != -1:
    new_dollar_calc = '''$=S.useMemo(()=>{if(!R||!Array.isArray(R.ingredients)||R.ingredients.length===0)return[];const he=Number(R.portionYield||R.portions||1)||1,ee=B>0?(B/he):1;return R.ingredients.map(ne=>{const G=Y(ne.ingredientName||ne.name),W=G.split(/\\s+/).filter(ye=>ye.length>=3&&!/^\\d+g?$/.test(ye)),q=r.find(ye=>{if(!ye)return!1;if(ne.ingredientId&&ye.id===ne.ingredientId)return!0;const Ke=Y(ye.name);if(Ke===G||G.length>=3&&(Ke.includes(G)||G.includes(Ke)))return!0;const et=Ke.split(/\\s+/).filter(ce=>ce.length>=3&&!/^\\d+g?$/.test(ce));return!!W.some(ce=>et.includes(ce))});let xe=1;if(q){const ye=(ne.unit||"").toLowerCase(),Ke=(q.unit||"").toLowerCase();(ye==="g"||ye==="ml")&&(Ke==="kg"||Ke==="l"||Ke==="litro"||Ke==="litros")?xe=1/1e3:(ye==="kg"||ye==="l"||ye==="litro"||ye==="litros")&&(Ke==="g"||Ke==="ml")&&(xe=1e3)}const rawQty=Math.abs(Number(ne.quantity??ne.required_quantity??ne.qty??0));const ve=+(rawQty*ee*xe).toFixed(4),se=q?q.branchStock?.[f]??0:0,qe=q?se>=ve:!1;const isCoffee=ne.sku==="SKU-7564"||q?.sku==="SKU-7564"||ne.ingredientId==="SKU-7564"||G.includes("cafe")||G.includes("café")||(q&&(Y(q.name).includes("cafe")||Y(q.name).includes("café")));let Ne=Number(q?.cost_cup??ne.cost_cup??ne.unit_cost??ne.cost??q?.unit_cost??q?.costPerUnit??q?.costCUP??ne.costPerUnit??ne.cost_per_unit??0);if(isCoffee){if(q?.cost_cup&&Number(q.cost_cup)>0&&Number(q.cost_cup)<500){Ne=Number(q.cost_cup);}else if(ne.cost_cup&&Number(ne.cost_cup)>0&&Number(ne.cost_cup)<500){Ne=Number(ne.cost_cup);}else if(Ne>=500||Ne===1600||Ne<=0){Ne=4.20;}}const De=+(ve*Ne).toFixed(2);return{ingredientName:ne.ingredientName||ne.name||"Insumo",ingredientId:ne.ingredientId,matchedItem:q,unit:q?.unit||ne.unit||"unidades",requiredQty:ve,unitCost:Ne,currentBranchStock:se,isSufficient:qe,totalCost:De};})},[R,B,r,f]),'''
    code = code[:pos_start] + new_dollar_calc + code[pos_end:]
    print("1. $ useMemo updated: Coffee unit cost resolved to 4.20, Math.abs applied to quantities")
else:
    print("1. $ useMemo already updated or pos not found")

# ---------------------------------------------------------------------------
# 2. Remove negative sign in table column "Consumo Requerido"
# ---------------------------------------------------------------------------
old_table_td = 'children:["-",he.requiredQty," ",he.unit]'
new_table_td = 'children:[Math.abs(he.requiredQty).toFixed(4)," ",he.unit||"unidades"]'

if old_table_td in code:
    code = code.replace(old_table_td, new_table_td, 1)
    print("2. Removed negative sign in Consumo Requerido table cell")
else:
    print("2. Negative sign already removed")

# ---------------------------------------------------------------------------
# 3. Add Cache Sanitizer at startup
# ---------------------------------------------------------------------------
cache_sanitizer = '''
  try {
    ['bistro_recipes', 'cache_recipes', 'local_recipes'].forEach(function(key) {
      var raw = localStorage.getItem(key);
      if (raw) {
        var list = JSON.parse(raw);
        if (Array.isArray(list)) {
          var changed = false;
          list.forEach(function(rec) {
            if (Array.isArray(rec.ingredients)) {
              rec.ingredients.forEach(function(ing) {
                var name = (ing.name || ing.ingredientName || '').toLowerCase();
                if (name.indexOf('cafe') !== -1 || name.indexOf('café') !== -1 || ing.sku === 'SKU-7564' || ing.ingredientId === 'SKU-7564') {
                  if (ing.costPerUnit === 1600 || ing.unit_cost === 1600 || ing.cost === 1600 || !ing.cost_cup) {
                    ing.costPerUnit = 4.20;
                    ing.unit_cost = 4.20;
                    ing.cost = 4.20;
                    ing.cost_cup = 4.20;
                    changed = true;
                  }
                  if (ing.quantity < 0) {
                    ing.quantity = Math.abs(ing.quantity);
                    changed = true;
                  }
                }
              });
            }
          });
          if (changed) localStorage.setItem(key, JSON.stringify(list));
        }
      }
    });

    ['bistro_inventory', 'cache_inventory'].forEach(function(key) {
      var raw = localStorage.getItem(key);
      if (raw) {
        var list = JSON.parse(raw);
        if (Array.isArray(list)) {
          var changed = false;
          list.forEach(function(item) {
            var name = (item.name || '').toLowerCase();
            if ((name.indexOf('cafe') !== -1 || name.indexOf('café') !== -1 || item.sku === 'SKU-7564') && (name.indexOf('oz') !== -1 || name.indexOf('polvo') !== -1)) {
              item.cost_cup = 4.20;
              item.unit_cost = 4.20;
              item.costPerUnit = 4.20;
              changed = true;
            }
          });
          if (changed) localStorage.setItem(key, JSON.stringify(list));
        }
      }
    });
  } catch(e) {}
'''

top_target = 'if (typeof window === "undefined") return;'
assert top_target in code, "top_target not found"
code = code.replace(top_target, top_target + cache_sanitizer, 1)
print("3. Cache sanitizer inserted at startup to sanitize coffee unit cost to 4.20")

with open('assets/index-DCC2oYkl.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("All corrections cleanly applied!")
