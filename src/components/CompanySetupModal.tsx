import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';
import { Building2, Search, PlusCircle, CheckCircle2, AlertCircle, Loader2, LogOut } from 'lucide-react';

export const CompanySetupModal: React.FC = () => {
  const { currentUser, refreshProfile, logout } = useAuth();
  const [tab, setTab] = useState<'join' | 'create'>('join');
  const [companyCode, setCompanyCode] = useState('biz-main');
  const [selectedRole, setSelectedRole] = useState('cajero');
  const [newCompanyName, setNewCompanyName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) return;
    setErrorMsg(null);
    setLoading(true);

    const cleanCode = companyCode.trim();

    try {
      // 1. Buscar coincidencia flexible por id o por company_code
      let targetCompany: any = null;
      const { data: company, error: searchError } = await supabase
        .from('companies')
        .select('id, name, company_code')
        .or(`id.ilike.${cleanCode},company_code.ilike.${cleanCode}`)
        .maybeSingle();

      if (!searchError && company) {
        targetCompany = company;
      } else if (cleanCode.toLowerCase() === 'biz-main') {
        targetCompany = { id: 'biz-main', name: 'BistroConta Pro', company_code: 'BIZ-MAIN' };
      } else if (searchError) {
        setErrorMsg('Error al consultar empresa: ' + searchError.message);
        setLoading(false);
        return;
      }

      if (!targetCompany) {
        setErrorMsg(`Código de empresa no válido. Verifica el código "${cleanCode}" con tu administrador.`);
        setLoading(false);
        return;
      }

      // 2. Actualizar perfil en Supabase como pendiente de aprobación
      const { error: updateError } = await supabase
        .from('profiles')
        .update({
          company_id: targetCompany.id,
          role: selectedRole || 'cajero',
          status: 'pending_approval',
          business_name: targetCompany.name,
          updated_at: new Date().toISOString(),
        })
        .eq('id', currentUser.id);

      if (updateError) {
        setErrorMsg('Error al registrar solicitud: ' + updateError.message);
        setLoading(false);
        return;
      }

      // 3. También registrar en company_members
      try {
        await supabase.from('company_members').upsert({
          company_id: targetCompany.id,
          user_id: currentUser.id,
          email: currentUser.email,
          role: selectedRole || 'cajero',
          status: 'pending_approval',
        });
      } catch {
        // Non-blocking
      }

      // 4. Refrescar el perfil global para transicionar a la pantalla de espera
      if (refreshProfile) {
        await refreshProfile();
      }
    } catch (err: any) {
      console.error('[CompanySetupModal] Error al unirse:', err);
      setErrorMsg(err.message || 'Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) return;
    setErrorMsg(null);
    setLoading(true);

    const cleanName = newCompanyName.trim();
    if (!cleanName) {
      setErrorMsg('Por favor ingresa el nombre de la empresa.');
      setLoading(false);
      return;
    }

    try {
      const cleanLower = cleanName.toLowerCase();
      // Check if company already exists or is BistroConta Pro
      let targetCompany: any = null;
      let targetId = 'biz-main';

      if (cleanLower.includes('bistroconta') || cleanLower === 'bistroconta pro' || cleanLower === 'biz-main') {
        const { data: comp } = await supabase
          .from('companies')
          .select('*')
          .eq('id', 'biz-main')
          .maybeSingle();
        targetCompany = comp || { id: 'biz-main', name: 'BistroConta Pro', company_code: 'biz-main' };
        targetId = 'biz-main';
      } else {
        const { data: existingComp } = await supabase
          .from('companies')
          .select('*')
          .or(`company_code.ilike.${cleanName},name.ilike.${cleanName}`)
          .maybeSingle();

        if (existingComp) {
          targetCompany = existingComp;
          targetId = existingComp.id;
        } else {
          const slug = cleanName
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-|-$/g, '')
            .slice(0, 15) || 'empresa';
          targetId = `biz-${slug}`;

          const { data: newComp, error: compErr } = await supabase
            .from('companies')
            .insert({
              id: targetId,
              name: cleanName,
              company_code: targetId,
              owner_id: currentUser.id,
            })
            .select()
            .single();

          if (compErr) throw compErr;
          targetCompany = newComp;
        }
      }

      // 2. Crear sucursal matriz principal si no existe
      try {
        await supabase.from('branches').upsert({
          id: `branch-${targetId}-main`,
          tenant_id: targetId,
          name: 'Sede Principal',
          is_main: true,
          is_active: true,
          work_mode: 'pos_directo',
        });
      } catch {
        // Non-blocking
      }

      // 3. Actualizar perfil como administrador activo
      const { error: profileErr } = await supabase
        .from('profiles')
        .update({
          company_id: targetCompany.id,
          role: 'admin',
          status: 'active',
          business_name: targetCompany.name,
          branch_id: `branch-${targetId}-main`,
          updated_at: new Date().toISOString(),
        })
        .eq('id', currentUser.id);

      if (profileErr) throw profileErr;

      // 4. Registrar en company_members como admin activo
      try {
        await supabase.from('company_members').upsert({
          company_id: targetCompany.id,
          user_id: currentUser.id,
          email: currentUser.email,
          role: 'admin',
          status: 'active',
        });
      } catch {
        // Non-blocking
      }

      await refreshProfile();
    } catch (err: any) {
      console.error('[CompanySetupModal] Error creando empresa:', err);
      setErrorMsg(err.message || 'Error al registrar la empresa.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-md flex items-center justify-center p-4 select-none">
      <div className="max-w-lg w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Vinculación de Empresa Gastronómica</h2>
              <p className="text-xs text-slate-400">Usuario autenticado: {currentUser?.email}</p>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition"
            title="Cerrar sesión"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>

        {errorMsg && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-2 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Tab selection */}
        <div className="grid grid-cols-2 gap-2 p-1 bg-slate-950 rounded-xl border border-slate-800">
          <button
            type="button"
            onClick={() => setTab('join')}
            className={`py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
              tab === 'join' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            Unirse a Empresa
          </button>
          <button
            type="button"
            onClick={() => setTab('create')}
            className={`py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-2 ${
              tab === 'create' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <PlusCircle className="w-3.5 h-3.5" />
            Crear Nueva Empresa
          </button>
        </div>

        {tab === 'join' ? (
          <form onSubmit={handleJoin} className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                Código, Nombre o ID de la Empresa
              </label>
              <input
                type="text"
                required
                value={companyCode}
                onChange={(e) => setCompanyCode(e.target.value)}
                placeholder="Ej. biz-main o BistroConta Pro"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <span className="text-[10px] text-slate-500 mt-1 block">
                Introduce el código proporcionado por el administrador del establecimiento
              </span>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                Rol Solicitado
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="cajero">Cajero / Dependiente TPV</option>
                <option value="mesero">Mesero / Camarero</option>
                <option value="cocina">Cocinero / Personal KDS</option>
                <option value="gerente">Gerente de Sucursal</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              Enviar Solicitud de Acceso
            </button>
          </form>
        ) : (
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                Nombre de la Empresa o Restaurante
              </label>
              <input
                type="text"
                required
                value={newCompanyName}
                onChange={(e) => setNewCompanyName(e.target.value)}
                placeholder="Ej. Restaurante Habana Bistro"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4" />}
              Registrar Empresa y Activar como Administrador
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default CompanySetupModal;
