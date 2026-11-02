import React, { useState, useEffect } from 'react';
import { Users, UserCheck, UserX, Clock, Building, Shield, Check, Loader2 } from 'lucide-react';

export interface CompanyMember {
  id: string;
  company_id: string;
  user_id?: string;
  email: string;
  full_name?: string;
  role: string;
  status: 'pending' | 'pending_approval' | 'active' | 'rejected';
  branch_id?: string | null;
  created_at: string;
}

export interface Branch {
  id: string;
  name: string;
  is_main?: boolean;
}

interface AdminUsersViewProps {
  companyId: string;
  companyName: string;
  currentUser: any;
  branches: Branch[];
  supabaseClient?: any;
  onLogAudit?: (action: string, description: string, details?: string) => void;
}

export const AdminUsersView: React.FC<AdminUsersViewProps> = ({
  companyId,
  companyName,
  currentUser,
  branches = [],
  supabaseClient,
  onLogAudit
}) => {
  const [members, setMembers] = useState<CompanyMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<{ [id: string]: boolean }>({});
  const [selectedRoles, setSelectedRoles] = useState<{ [id: string]: string }>({});
  const [selectedBranches, setSelectedBranches] = useState<{ [id: string]: string }>({});
  const [notification, setNotification] = useState<string | null>(null);

  const getClient = () => {
    return supabaseClient || (window as any)?.__BISTRO_SUPABASE_CLIENT__;
  };

  const loadMembers = async () => {
    setLoading(true);
    const client = getClient();
    if (!client || !companyId) {
      setLoading(false);
      return;
    }

    try {
      const { data, error } = await client
        .from('company_members')
        .select('*')
        .eq('company_id', companyId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('[AdminUsersView] Error loading members:', error);
      } else {
        setMembers(data || []);
      }
    } catch (e) {
      console.error('[AdminUsersView] Exception loading members:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMembers();
  }, [companyId]);

  const handleApprove = async (member: CompanyMember) => {
    const roleToAssign = selectedRoles[member.id] || 'cajero';
    const branchToAssign = selectedBranches[member.id] || branches[0]?.id || 'branch-main';

    setActionLoading(prev => ({ ...prev, [member.id]: true }));
    const client = getClient();

    try {
      const { error } = await client
        .from('company_members')
        .update({
          status: 'active',
          role: roleToAssign,
          branch_id: branchToAssign
        })
        .eq('id', member.id);

      if (error) throw error;

      onLogAudit?.(
        'user_approved',
        `Usuario ${member.email} aprobado con rol ${roleToAssign.toUpperCase()} en sucursal ${branchToAssign}`,
        JSON.stringify({ memberId: member.id, role: roleToAssign, branchId: branchToAssign })
      );

      setNotification(`Usuario ${member.email} aprobado con éxito.`);
      setTimeout(() => setNotification(null), 4000);
      await loadMembers();
    } catch (e: any) {
      console.error('[AdminUsersView] Error approving user:', e);
      alert(e?.message || 'Error al aprobar solicitud de usuario.');
    } finally {
      setActionLoading(prev => ({ ...prev, [member.id]: false }));
    }
  };

  const handleReject = async (member: CompanyMember) => {
    if (!window.confirm(`¿Seguro que deseas rechazar la solicitud de acceso para ${member.email}?`)) {
      return;
    }

    setActionLoading(prev => ({ ...prev, [member.id]: true }));
    const client = getClient();

    try {
      const { error } = await client
        .from('company_members')
        .update({ status: 'rejected' })
        .eq('id', member.id);

      if (error) throw error;

      onLogAudit?.(
        'user_rejected',
        `Solicitud de acceso rechazada para ${member.email}`,
        JSON.stringify({ memberId: member.id })
      );

      setNotification(`Solicitud de ${member.email} rechazada.`);
      setTimeout(() => setNotification(null), 4000);
      await loadMembers();
    } catch (e: any) {
      console.error('[AdminUsersView] Error rejecting user:', e);
      alert(e?.message || 'Error al rechazar solicitud.');
    } finally {
      setActionLoading(prev => ({ ...prev, [member.id]: false }));
    }
  };

  const pendingRequests = members.filter(
    m => m.status === 'pending' || m.status === 'pending_approval'
  );
  const activeMembers = members.filter(m => m.status === 'active');

  return (
    <div className="space-y-6 animate-fadeIn pb-12 select-none">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Gestión de Usuarios y Personal</h1>
            <p className="text-xs text-slate-400">
              Control de acceso por roles (RBAC) y asignación estricta de sucursales para {companyName}
            </p>
          </div>
        </div>
      </div>

      {notification && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-2 text-emerald-300 text-xs">
          <Check className="w-4 h-4 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Seccion: Solicitudes Pendientes de Acceso */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-amber-400" />
            <h2 className="text-sm font-bold text-white">Solicitudes Pendientes de Acceso</h2>
          </div>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {pendingRequests.length} pendientes
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-emerald-500" />
            Cargando solicitudes...
          </div>
        ) : pendingRequests.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No hay solicitudes de acceso pendientes de aprobación en este momento.
          </div>
        ) : (
          <div className="space-y-3">
            {pendingRequests.map(req => (
              <div
                key={req.id}
                className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-xs">
                      {req.full_name || req.email.split('@')[0]}
                    </span>
                    <span className="text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20 font-semibold">
                      Pendiente de Aprobación
                    </span>
                  </div>
                  <span className="text-xs text-slate-400 block mt-0.5">{req.email}</span>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {/* Selector de Rol */}
                  <select
                    value={selectedRoles[req.id] || 'cajero'}
                    onChange={e =>
                      setSelectedRoles(prev => ({ ...prev, [req.id]: e.target.value }))
                    }
                    className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  >
                    <option value="cajero">Cajero / TPV</option>
                    <option value="dependiente">Dependiente</option>
                    <option value="mesero">Mesero / Sala</option>
                    <option value="cocina">Cocinero / KDS</option>
                    <option value="gerente">Gerente de Sucursal</option>
                    <option value="admin">Administrador</option>
                  </select>

                  {/* Selector de Sucursal */}
                  <select
                    value={selectedBranches[req.id] || branches[0]?.id || 'branch-main'}
                    onChange={e =>
                      setSelectedBranches(prev => ({ ...prev, [req.id]: e.target.value }))
                    }
                    className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  >
                    {branches.map(b => (
                      <option key={b.id} value={b.id}>
                        {b.name}
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={() => handleApprove(req)}
                    disabled={actionLoading[req.id]}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1 cursor-pointer disabled:opacity-50"
                  >
                    {actionLoading[req.id] ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <UserCheck className="w-3.5 h-3.5" />
                    )}
                    Aprobar
                  </button>

                  <button
                    onClick={() => handleReject(req)}
                    disabled={actionLoading[req.id]}
                    className="px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white rounded-lg text-xs font-bold transition flex items-center gap-1 cursor-pointer disabled:opacity-50"
                  >
                    <UserX className="w-3.5 h-3.5" />
                    Rechazar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Seccion: Miembros Activos */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-400" />
            <h2 className="text-sm font-bold text-white">Personal y Miembros Activos</h2>
          </div>
          <span className="text-xs text-slate-400">{activeMembers.length} activos</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {activeMembers.map(m => {
            const branchName =
              branches.find(b => b.id === m.branch_id)?.name || 'Sucursal Principal';
            return (
              <div
                key={m.id}
                className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-white text-xs block">
                    {m.full_name || m.email.split('@')[0]}
                  </span>
                  <span className="text-[11px] text-slate-400 block">{m.email}</span>
                  <span className="text-[10px] text-indigo-400 font-semibold flex items-center gap-1 mt-0.5">
                    <Building className="w-3 h-3" />
                    {branchName}
                  </span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                  {m.role}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AdminUsersView;
