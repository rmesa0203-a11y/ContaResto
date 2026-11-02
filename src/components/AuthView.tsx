import React, { useState } from 'react';
import { Lock, Mail, Building, User, KeyRound, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

interface AuthViewProps {
  supabaseClient?: any;
  onLoginSuccess: (userProfile: any, companyId: string, companyName: string) => void;
}

export const AuthView: React.FC<AuthViewProps> = ({ supabaseClient, onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [pendingApproval, setPendingApproval] = useState<boolean>(false);

  // Form fields
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyCode, setCompanyCode] = useState('biz-main');

  const getClient = () => {
    return supabaseClient || (window as any)?.__BISTRO_SUPABASE_CLIENT__;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    const client = getClient();
    if (!client) {
      setErrorMsg('Error: Cliente de base de datos no inicializado.');
      setLoading(false);
      return;
    }

    try {
      const cleanEmail = email.trim().toLowerCase();
      // Strict Supabase Auth with password
      const { data, error } = await client.auth.signInWithPassword({
        email: cleanEmail,
        password: password
      });

      if (error || !data?.user) {
        throw new Error(error?.message || 'Credenciales incorrectas. Verifique su correo y contraseña.');
      }

      const authUser = data.user;

      // 1. Carga directa de la tabla pública profiles
      const { data: profile, error: profileErr } = await client
        .from('profiles')
        .select('*')
        .eq('id', authUser.id)
        .maybeSingle();

      if (profileErr) {
        console.warn('[AuthView] Error consultando profiles:', profileErr);
      }

      // Check if user is pending approval
      if (profile?.status === 'pending_approval' || profile?.status === 'pending') {
        setPendingApproval(true);
        return;
      }

      if (profile?.status === 'rejected') {
        throw new Error('Tu solicitud de acceso fue rechazada por el administrador de la empresa.');
      }

      // Resolve company
      const companyId = profile?.company_id || 'biz-main';
      const { data: comp } = await client
        .from('companies')
        .select('*')
        .eq('id', companyId)
        .maybeSingle();

      const companyName = comp?.name || profile?.business_name || 'BistroConta Pro';

      const userProfile = {
        id: authUser.id,
        name: profile?.full_name || authUser.user_metadata?.full_name || cleanEmail.split('@')[0],
        email: cleanEmail,
        role: profile?.role || 'clerk',
        status: profile?.status || 'active',
        assignedBranchId: profile?.branch_id || 'branch-main',
        branch_id: profile?.branch_id || 'branch-main',
        tenantId: companyId,
        businessName: companyName
      };

      onLoginSuccess(userProfile, companyId, companyName);
    } catch (err: any) {
      console.error('[AuthView] Login error:', err);
      setErrorMsg(err?.message || 'Error al iniciar sesión.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterWithCompanyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    const client = getClient();
    if (!client) {
      setErrorMsg('Error: Cliente de base de datos no inicializado.');
      setLoading(false);
      return;
    }

    try {
      const cleanCode = companyCode.trim();
      if (!cleanCode) {
        alert('La empresa o código ingresado no existe en la base de datos.');
        throw new Error('Debes ingresar el nombre o código de la empresa.');
      }

      // 1. Búsqueda flexible de empresa por company_code, name o id (insensible a mayúsculas)
      const { data: companies, error: compErr } = await client
        .from('companies')
        .select('id, name, company_code')
        .or(`company_code.ilike.${cleanCode},name.ilike.${cleanCode},id.eq.${cleanCode}`);

      let company = companies && companies.length > 0 ? companies[0] : null;
      if (!company && cleanCode.toLowerCase() === 'biz-main') {
        company = { id: 'biz-main', name: 'BistroConta Pro', company_code: 'biz-main' };
      }

      if (!company || compErr) {
        alert('La empresa o código ingresado no existe en la base de datos.');
        throw new Error('La empresa o código ingresado no existe en la base de datos.');
      }

      const cleanEmail = email.trim().toLowerCase();

      // 2. Registro en Supabase Auth enviando metadatos
      const { data: authData, error: authError } = await client.auth.signUp({
        email: cleanEmail,
        password: password,
        options: {
          data: {
            full_name: fullName.trim(),
            company_id: company.id,
            company_code: company.company_code || company.id
          }
        }
      });

      if (authError) {
        alert('Error de registro: ' + authError.message);
        throw new Error('Error de registro: ' + authError.message);
      }

      const userId = authData.user?.id;
      if (userId) {
        // 3. Persistir inmediatamente en la tabla pública profiles
        const { error: profileError } = await client
          .from('profiles')
          .upsert({
            id: userId,
            full_name: fullName.trim(),
            company_id: company.id,
            role: 'pending',
            status: 'pending_approval',
            business_name: company.name || 'BistroConta Pro',
            updated_at: new Date().toISOString()
          });

        if (profileError) {
          console.error('Error al crear perfil en la nube:', profileError);
        }

        // También registrar en company_members
        try {
          await client.from('company_members').upsert({
            company_id: company.id,
            user_id: userId,
            email: cleanEmail,
            role: 'pending',
            status: 'pending_approval'
          });
        } catch (mErr) {
          console.warn('[AuthView] company_members notice:', mErr);
        }
      }

      // 4. Mostrar pantalla de espera de autorización
      setPendingApproval(true);
    } catch (err: any) {
      console.error('[AuthView] Registration error:', err);
      setErrorMsg(err?.message || 'Error al procesar registro.');
    } finally {
      setLoading(false);
    }
  };

  if (pendingApproval) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center space-y-4 shadow-2xl">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-white">Solicitud de Acceso Enviada</h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Solicitud de acceso enviada al administrador. Tu cuenta se activará cuando asignen tu rol y sucursal.
          </p>
          <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-slate-400">
            Puedes cerrar esta pestaña o volver a intentar iniciar sesión una vez que el administrador haya aprobado tu perfil en el panel.
          </div>
          <button
            onClick={() => {
              setPendingApproval(false);
              setIsRegister(false);
            }}
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition cursor-pointer"
          >
            Volver al Inicio de Sesión
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 select-none">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/20">
            <Lock className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">BistroConta POS</h1>
          <p className="text-xs text-slate-400">
            {isRegister
              ? 'Unirse a una empresa existente con Código de Empresa o Nombre'
              : 'Inicio de sesión seguro mediante Supabase Auth'}
          </p>
        </div>

        {errorMsg && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-2 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={isRegister ? handleRegisterWithCompanyCode : handleLogin} className="space-y-4">
          {isRegister && (
            <>
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Nombre Completo
                </label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={e => setFullName(e.target.value)}
                    placeholder="Ej. Roberto Mesa"
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Empresa (Código o Nombre)
                </label>
                <div className="relative">
                  <Building className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={companyCode}
                    onChange={e => setCompanyCode(e.target.value)}
                    placeholder="Ej. biz-main o BistroConta Pro"
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <span className="text-[10px] text-slate-500 mt-0.5 block">
                  Introduce el identificador (ej. biz-main) o nombre de la empresa
                </span>
              </div>
            </>
          )}

          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              Correo Electrónico
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="usuario@ejemplo.com"
                className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
              Contraseña
            </label>
            <div className="relative">
              <KeyRound className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isRegister ? (
              'Enviar Solicitud de Registro'
            ) : (
              'Iniciar Sesión con Contraseña'
            )}
          </button>
        </form>

        <div className="text-center pt-2 border-t border-slate-800/80">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setErrorMsg(null);
            }}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold cursor-pointer"
          >
            {isRegister
              ? '¿Ya tienes una cuenta activa? Inicia sesión aquí'
              : '¿Nuevo empleado o colaborador? Regístrate con Código de Empresa'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthView;
