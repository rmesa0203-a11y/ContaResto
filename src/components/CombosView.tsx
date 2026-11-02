import React, { useState } from 'react';
import { Package, Plus, Search, Tag, DollarSign, Layers } from 'lucide-react';

export interface ComboItem {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  unitCost: number;
}

export interface Combo {
  id: string;
  name: string;
  sku: string;
  description?: string;
  sellingPrice: number;
  cost: number;
  items: ComboItem[];
  active: boolean;
  availableBranches?: string[];
  createdAt: string;
}

interface CombosViewProps {
  combos?: Combo[];
  currency?: string;
  currentUser?: any;
  onUpdateCombos?: (combos: Combo[]) => void;
  onOpenCreateModal?: () => void;
}

export const CombosView: React.FC<CombosViewProps> = ({
  combos = [],
  currency = 'CUP',
  currentUser,
  onUpdateCombos,
  onOpenCreateModal
}) => {
  const [search, setSearch] = useState('');
  const [filterActive, setFilterActive] = useState<'all' | 'active' | 'inactive'>('all');

  const filteredCombos = (combos || []).filter(combo => {
    const matchesSearch =
      (combo.name || '').toLowerCase().includes(search.toLowerCase()) ||
      (combo.sku || '').toLowerCase().includes(search.toLowerCase());
    const matchesActive =
      filterActive === 'all' ||
      (filterActive === 'active' && combo.active) ||
      (filterActive === 'inactive' && !combo.active);
    return matchesSearch && matchesActive;
  });

  return (
    <div className="space-y-6 animate-fadeIn pb-12 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Combos y Formatos Mayoristas</h1>
            <p className="text-xs text-slate-400">
              Gestión de paquetes promocionales, presentaciones y combos vinculados al inventario real
            </p>
          </div>
        </div>

        <button
          onClick={onOpenCreateModal}
          className="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-purple-600/20 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Nuevo Combo o Formato
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Buscar por nombre o SKU de combo..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'active', 'inactive'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilterActive(f)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition ${
                filterActive === f
                  ? 'bg-purple-600 text-white shadow-xs'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {f === 'all' ? 'Todos' : f === 'active' ? 'Activos' : 'Inactivos'}
            </button>
          ))}
        </div>
      </div>

      {/* Grid or Clean Empty State */}
      {filteredCombos.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center flex flex-col items-center justify-center">
          <div className="w-16 h-16 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mb-4">
            <Package className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-white mb-1">No hay combos activos registrados</h3>
          <p className="text-xs text-slate-400 max-w-sm mb-6">
            El catálogo de combos no contiene registros precargados. Crea paquetes promocionales o formatos mayoristas vinculados a tus insumos de almacén.
          </p>
          <button
            onClick={onOpenCreateModal}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Crear Primer Combo
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCombos.map(combo => (
            <div
              key={combo.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition space-y-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="text-[10px] font-mono font-bold text-purple-400 uppercase tracking-wider block mb-0.5">
                    {combo.sku || 'SIN SKU'}
                  </span>
                  <h3 className="font-bold text-white text-sm">{combo.name}</h3>
                </div>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    combo.active
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-slate-800 text-slate-500'
                  }`}
                >
                  {combo.active ? 'Activo' : 'Inactivo'}
                </span>
              </div>

              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1.5 text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Precio de Venta:</span>
                  <span className="font-bold text-white font-mono">
                    $ {combo.sellingPrice.toFixed(2)} {currency}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Costo Estimado:</span>
                  <span className="font-mono text-slate-300">
                    $ {combo.cost.toFixed(2)} {currency}
                  </span>
                </div>
                <div className="flex items-center justify-between text-slate-400 pt-1 border-t border-slate-800">
                  <span>Margen:</span>
                  <span className="font-bold text-emerald-400 font-mono">
                    {combo.sellingPrice > 0
                      ? (((combo.sellingPrice - combo.cost) / combo.sellingPrice) * 100).toFixed(1)
                      : 0}%
                  </span>
                </div>
              </div>

              <div className="text-[11px] text-slate-400">
                <span className="font-semibold block mb-1">Ítems incluidos ({combo.items?.length || 0}):</span>
                <ul className="space-y-0.5 max-h-24 overflow-y-auto">
                  {(combo.items || []).map((it, idx) => (
                    <li key={idx} className="flex justify-between text-slate-500">
                      <span>• {it.name}</span>
                      <span>{it.quantity} {it.unit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CombosView;
