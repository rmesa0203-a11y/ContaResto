import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';
import { Lock, Mail, KeyRound, Loader2, AlertCircle, Building2, UserPlus, LogIn } from 'lucide-react';

interface LoginViewProps {
  onSuccess?: () => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onSuccess }) => {
  const { login } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [companyCode, setCompanyCode] = useState('biz-main');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);
    setLoading(true);

    const cleanEmail = email.trim().toLowerCase();

    try {
      if (isRegisterMode) {
        // 1. Verify company exists in Supabase
        const cleanCode = companyCode.trim();
        const { data: compList, error: compErr } = await supabase
          .from('companies')
          .select('id, name, company_code')
          .or(`company_code.ilike.${cleanCode},name.ilike.${cleanCode},id.eq.${cleanCode}`);

        let targetCompany = compList && compList.length > 0 ? compList[0] : null;
        if (!targetCompany && cleanCode.toLowerCase() === 'biz-main') {
          targetCompany = { id: 'biz-main', name: 'BistroConta Pro', company_code: 'biz-main' };
        }

        if (!targetCompany || compErr) {
          throw new Error('La empresa o código ingresado no existe en la base de datos.');
        }

        // 2. Sign up in Supabase Auth
        const { data: authData, error: authError } = await supabase.auth.signUp({
          email: cleanEmail,
          password,
          options: {
            data: {
              full_name: fullName.trim() || cleanEmail.split('@')[0],
              company_id: targetCompany.id,
              company_code: targetCompany.company_code || targetCompany.id,
            },
          },
        });

        if (authError) throw authError;

        const userId = authData.user?.id;
        if (userId) {
          // 3. Insert/Upsert into profiles
          await supabase.from('profiles').upsert({
            id: userId,
            full_name: fullName.trim() || cleanEmail.split('@')[0],
            company_id: targetCompany.id,
            role: 'cajero',
            status: 'pending_approval',
            business_name: targetCompany.name || 'BistroConta Pro',
            updated_at: new Date().toISOString(),
          });

          // Also insert into company_members
          try {
            await supabase.from('company_members').upsert({
              company_id: targetCompany.id,
              user_id: userId,
              email: cleanEmail,
              role: 'cajero',
              status: 'pending_approval',
            });
          } catch {
            // Non-blocking
          }
        }

        setSuccessMsg(
          `¡Cuenta registrada con éxito! Tu solicitud fue enviada a "${targetCompany.name}". Ya puedes iniciar sesión para comprobar tu estado.`
        );
        setIsRegisterMode(false);
      } else {
        // Standard Login
        await login(cleanEmail, password);
        onSuccess?.();
      }
    } catch (err: any) {
      console.error('[LoginView] Error:', err);
      setErrorMsg(err.message || 'Error al autenticar con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 select-none">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/20">
            <Lock className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">BistroConta Cloud</h1>
          <p className="text-xs text-slate-400">
            {isRegisterMode
              ? 'Solicita acceso a una empresa gastronómica activa'
              : 'Gestión contable, TPV e inventario para gastronomía'}
          </p>
        </div>

        {/* Notifications */}
        {errorMsg && (
          <div className="p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl flex items-start gap-2.5 text-rose-300 text-xs animate-shake">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span className="leading-relaxed">{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl flex items-start gap-2.5 text-emerald-300 text-xs">
            <span className="leading-relaxed">{successMsg}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegisterMode && (
            <>
              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Nombre Completo
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ej. Roberto Mesa"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                  Código o Nombre de Empresa
                </label>
                <div className="relative">
                  <Building2 className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={companyCode}
                    onChange={(e) => setCompanyCode(e.target.value)}
                    placeholder="Ej. biz-main o BistroConta Pro"
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 text-xs placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
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
                onChange={(e) => setEmail(e.target.value)}
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
                onChange={(e) => setPassword(e.target.value)}
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
            ) : isRegisterMode ? (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Enviar Solicitud de Registro</span>
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                <span>Iniciar Sesión</span>
              </>
            )}
          </button>
        </form>

        {/* Toggle between Login and Register */}
        <div className="text-center pt-2 border-t border-slate-800/80">
          <button
            type="button"
            onClick={() => {
              setIsRegisterMode(!isRegisterMode);
              setErrorMsg(null);
              setSuccessMsg(null);
            }}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold cursor-pointer transition"
          >
            {isRegisterMode
              ? '¿Ya tienes cuenta activa? Inicia sesión aquí'
              : '¿Nuevo colaborador? Regístrate y únete a una empresa'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginView;
