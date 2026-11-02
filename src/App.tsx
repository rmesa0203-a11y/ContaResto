import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginView } from './components/LoginView';
import { CompanySetupModal } from './components/CompanySetupModal';
import { UsersView } from './components/UsersView';
import { CombosView } from './components/CombosView';
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Layers,
  Users,
  LogOut,
  RefreshCw,
  Building,
  Store,
  ShieldAlert,
} from 'lucide-react';

const AppContent: React.FC = () => {
  const { currentUser, loading, logout, refreshProfile } = useAuth();
  const [activeTab, setActiveTab] = useState<'pos' | 'inventory' | 'combos' | 'users'>('pos');
  const [checkingStatus, setCheckingStatus] = useState(false);

  // 1. Estado de carga inicial
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center select-none">
        <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-4" />
        <h2 className="text-base font-bold text-white mb-1">Sincronizando con BistroConta Cloud...</h2>
        <p className="text-xs text-slate-400">Verificando credenciales, empresa y sucursal asignada</p>
      </div>
    );
  }

  // 2. Sin sesión activa
  if (!currentUser) {
    return <LoginView />;
  }

  // 3. Usuario sin empresa asignada
  if (!currentUser.company_id) {
    return <CompanySetupModal />;
  }

  // 4. Usuario pendiente de aprobación por el administrador
  if (currentUser.status === 'pending_approval' || currentUser.status === 'pending') {
    const handleCheckStatus = async () => {
      setCheckingStatus(true);
      try {
        await refreshProfile();
      } finally {
        setCheckingStatus(false);
      }
    };

    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 select-none">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center space-y-6 shadow-2xl backdrop-blur-xl">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto text-3xl">
            ⏳
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-black text-white tracking-tight">Acceso Pendiente de Aprobación</h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              Tu cuenta está registrada en{' '}
              <span className="font-bold text-emerald-400">{currentUser.company_name || 'tu empresa'}</span>, pero requiere
              que el administrador apruebe tu acceso y asigne tu sucursal operativa.
            </p>
          </div>

          <div className="p-4 bg-slate-950/80 rounded-2xl border border-slate-800/80 text-left space-y-2 text-xs">
            <div className="flex justify-between text-slate-400">
              <span>Colaborador:</span>
              <span className="font-semibold text-white">{currentUser.full_name || currentUser.email}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Correo:</span>
              <span className="font-mono text-slate-300">{currentUser.email}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Rol Solicitado:</span>
              <span className="font-bold uppercase text-amber-400">{currentUser.role}</span>
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <button
              onClick={handleCheckStatus}
              disabled={checkingStatus}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${checkingStatus ? 'animate-spin' : ''}`} />
              <span>Comprobar Estado</span>
            </button>

            <button
              onClick={() => logout()}
              className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-semibold transition flex items-center justify-center gap-2 cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Si fue rechazado
  if (currentUser.status === 'rejected') {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 select-none">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center space-y-6 shadow-2xl">
          <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-white">Solicitud Rechazada</h2>
            <p className="text-xs text-slate-300">
              Tu solicitud de ingreso a {currentUser.company_name} no fue aprobada por el administrador.
            </p>
          </div>
          <button
            onClick={() => logout()}
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition cursor-pointer"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    );
  }

  // 5. Usuario Activo -> Interfaz Principal
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col select-none">
      {/* Top Navbar */}
      <header className="bg-slate-900 border-b border-slate-800 px-4 sm:px-6 py-3 flex items-center justify-between sticky top-0 z-30 shadow-md">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center font-black text-white text-sm shadow-md shadow-emerald-500/20">
              BC
            </div>
            <div>
              <span className="font-extrabold text-sm text-white tracking-tight block">BistroConta Pro</span>
              <div className="flex items-center gap-2 text-[11px] text-slate-400">
                <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                  <Building className="w-3 h-3" />
                  {currentUser.company_name}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1 text-indigo-400">
                  <Store className="w-3 h-3" />
                  {currentUser.branch_name || 'Sede Principal'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('pos')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === 'pos' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShoppingCart className="w-3.5 h-3.5" />
            TPV / Ventas
          </button>

          <button
            onClick={() => setActiveTab('inventory')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === 'inventory' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Package className="w-3.5 h-3.5" />
            Inventario
          </button>

          <button
            onClick={() => setActiveTab('combos')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
              activeTab === 'combos' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Combos
          </button>

          {currentUser.role === 'admin' && (
            <button
              onClick={() => setActiveTab('users')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                activeTab === 'users' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              Personal & RBAC
            </button>
          )}
        </nav>

        {/* User Badge & Logout */}
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <span className="text-xs font-bold text-white block">{currentUser.full_name}</span>
            <span className="text-[10px] text-emerald-400 uppercase font-mono font-semibold tracking-wider">
              {currentUser.role}
            </span>
          </div>

          <button
            onClick={() => logout()}
            className="p-2 bg-slate-800 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 rounded-xl transition border border-slate-700/60 cursor-pointer"
            title="Cerrar sesión"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main View Area */}
      <main className="flex-1 p-4 sm:p-6 max-w-7xl w-full mx-auto">
        {activeTab === 'pos' && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center space-y-3">
            <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-xl flex items-center justify-center mx-auto">
              <ShoppingCart className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-white">Terminal Punto de Venta (TPV)</h2>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Operando en <span className="font-semibold text-emerald-400">{currentUser.branch_name || 'Sede Principal'}</span> bajo
              la empresa <span className="font-semibold text-emerald-400">{currentUser.company_name}</span> con inventario segmentado.
            </p>
          </div>
        )}

        {activeTab === 'inventory' && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center space-y-3">
            <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-xl flex items-center justify-center mx-auto">
              <Package className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-white">Control de Existencias & Almacén</h2>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Existencias vinculadas a la sucursal activa. Los usuarios con rol {currentUser.role} tienen acceso con políticas RBAC aplicadas.
            </p>
          </div>
        )}

        {activeTab === 'combos' && <CombosView />}

        {activeTab === 'users' && currentUser.role === 'admin' && <UsersView />}
      </main>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
