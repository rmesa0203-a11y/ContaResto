import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';
import {
  Users,
  UserCheck,
  UserX,
  Clock,
  Building,
  Shield,
  Loader2,
  RefreshCw,
  AlertCircle,
  Edit2,
  Save,
  X,
  Lock,
} from 'lucide-react';

export interface UserProfileItem {
  id: string;
  email: string;
  full_name?: string | null;
  display_name?: string;
  role: string;
  status: string;
  company_id?: string | null;
  branch_id?: string | null;
  branch_name?: string;
  updated_at?: string;
}

export interface BranchOption {
  id: string;
  name: string;
}

export const UsersView: React.FC = () => {
  const { currentUser, refreshProfile } = useAuth();
  const currentCompanyId = currentUser?.company_id || 'biz-main';

  const [users, setUsers] = useState<UserProfileItem[]>([]);
  const [branches, setBranches] = useState<BranchOption[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<{ [id: string]: boolean }>({});

  // Pending request form selections
  const [selectedRoles, setSelectedRoles] = useState<{ [id: string]: string }>({});
  const [selectedBranches, setSelectedBranches] = useState<{ [id: string]: string }>({});

  // Active user edit mode
  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [editFullName, setEditFullName] = useState<string>('');
  const [editRole, setEditRole] = useState<string>('cajero');
  const [editBranchId, setEditBranchId] = useState<string>('');

  // 1. Cargar sucursales reales directamente desde Supabase sin mocks y sin duplicados
  const fetchBranches = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('branches')
        .select('id, name, is_active, company_id')
        .eq('company_id', currentCompanyId)
        .eq('is_active', true)
        .order('name', { ascending: true });

      if (!error && data && data.length > 0) {
        const uniqueBranches = Array.from(
          new Map(data.map((item) => [item.id, { id: item.id, name: item.name }])).values()
        );
        setBranches(uniqueBranches);
      } else {
        // Búsqueda flexible en caso de que company_id no esté asignado en la fila
        const { data: allData } = await supabase
          .from('branches')
          .select('id, name, is_active')
          .eq('is_active', true)
          .order('name', { ascending: true });

        if (allData && allData.length > 0) {
          const uniqueBranches = Array.from(
            new Map(allData.map((item) => [item.id, { id: item.id, name: item.name }])).values()
          );
          setBranches(uniqueBranches);
        } else {
          setBranches([]);
        }
      }
    } catch (err) {
      console.warn('[UsersView] Error consultando sucursales:', err);
      setBranches([]);
    }
  }, [currentCompanyId]);

  // 2. Consulta simplificada y blindada de perfiles sin joins frágiles ni filtros que descarten company_id null
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setErrorMsg(null);

      // 1. Obtener los perfiles directamente desde profiles
      const { data: profilesData, error: profError } = await supabase
        .from('profiles')
        .select('id, email, full_name, role, status, company_id, branch_id, updated_at')
        .order('updated_at', { ascending: false });

      if (profError) {
        console.error('Error al consultar profiles:', profError);
        setErrorMsg('Error al cargar perfiles: ' + profError.message);
        return;
      }

      // 2. Obtener las sucursales para mapear los nombres localmente sin fallar en joins
      const { data: branchesData } = await supabase
        .from('branches')
        .select('id, name');

      if (branchesData && branchesData.length > 0) {
        setBranches(branchesData);
      }

      const branchMap = new Map((branchesData || []).map((b) => [b.id, b.name]));

      // 3. Formatear usuarios
      const formattedUsers: UserProfileItem[] = (profilesData || []).map((u) => ({
        ...u,
        display_name: u.full_name || u.email || 'Usuario sin nombre',
        branch_name: branchMap.get(u.branch_id) || (u.branch_id ? u.branch_id : 'Sin sucursal asignada'),
      }));

      setUsers(formattedUsers);
    } catch (err: any) {
      console.error('Excepción al cargar usuarios:', err);
      setErrorMsg(err.message || 'Error desconocido al cargar usuarios');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBranches();
    fetchUsers();
  }, [fetchBranches, fetchUsers]);

  // 3. Guardar / Aprobar usuario persistiendo company_id ('biz-main'), sucursal y rol
  const handleApproveUser = async (userId: string, assignedRole: string, assignedBranchId: string) => {
    if (!assignedBranchId) {
      alert('Error: Debe asignar una sucursal obligatoriamente al empleado.');
      return;
    }

    try {
      setActionLoading((prev) => ({ ...prev, [userId]: true }));
      const { data, error } = await supabase
        .from('profiles')
        .update({
          company_id: currentCompanyId,
          role: assignedRole || 'cajero',
          branch_id: assignedBranchId,
          status: 'active',
          updated_at: new Date().toISOString(),
        })
        .eq('id', userId)
        .select();

      if (error) {
        alert('Error al guardar en base de datos: ' + error.message);
        return;
      }

      try {
        await supabase
          .from('company_members')
          .upsert({
            company_id: currentCompanyId,
            user_id: userId,
            role: assignedRole,
            status: 'active',
            branch_id: assignedBranchId,
          });
      } catch {
        // Non-blocking
      }

      await fetchUsers();
      alert('Usuario aprobado y activado correctamente.');
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  // 4. Edición de datos de usuario existente
  const handleUpdateUser = async (
    userId: string,
    newRole: string,
    newBranchId: string,
    newFullName: string
  ) => {
    try {
      setActionLoading((prev) => ({ ...prev, [userId]: true }));
      const { data, error } = await supabase
        .from('profiles')
        .update({
          full_name: newFullName.trim(),
          role: newRole,
          branch_id: newBranchId,
          company_id: currentCompanyId,
          updated_at: new Date().toISOString(),
        })
        .eq('id', userId)
        .select();

      if (error) {
        alert('Error al guardar en base de datos: ' + error.message);
        return;
      }

      setEditingUserId(null);
      if (currentUser?.id === userId) {
        await refreshProfile();
      }
      await fetchUsers();
      alert('Usuario actualizado correctamente.');
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  // 5. Rechazar solicitud
  const handleReject = async (userId: string, userEmail: string) => {
    if (!window.confirm(`¿Seguro que deseas rechazar la solicitud de acceso para ${userEmail}?`)) {
      return;
    }

    try {
      setActionLoading((prev) => ({ ...prev, [userId]: true }));
      const { error } = await supabase
        .from('profiles')
        .update({
          status: 'rejected',
          updated_at: new Date().toISOString(),
        })
        .eq('id', userId);

      if (error) {
        alert('Error al rechazar solicitud en Supabase: ' + error.message);
        return;
      }

      await fetchUsers();
      alert('Solicitud rechazada.');
    } catch (err: any) {
      alert('Error al rechazar usuario: ' + (err.message || String(err)));
    } finally {
      setActionLoading((prev) => ({ ...prev, [userId]: false }));
    }
  };

  const pendingRequests = users.filter((u) => u.status === 'pending_approval' || u.status === 'pending');
  const activeMembers = users.filter((u) => u.status === 'active');

  return (
    <div className="space-y-6 animate-fadeIn pb-12 select-none">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">Gestión de Personal & Control de Acceso</h1>
            <p className="text-xs text-slate-400">
              Perfiles sincronizados directamente con{' '}
              <span className="font-semibold text-emerald-400">Supabase PostgreSQL</span>
            </p>
          </div>
        </div>

        <button
          onClick={fetchUsers}
          disabled={loading}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-2 transition cursor-pointer self-start sm:self-auto border border-slate-700/60"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar Lista</span>
        </button>
      </div>

      {/* Renderizado de error visual */}
      {errorMsg && (
        <div className="p-4 bg-rose-500/15 border border-rose-500/40 rounded-xl flex items-start gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
          <div className="flex-1">
            <span className="font-bold block text-rose-200 mb-0.5">Error de conexión con Supabase:</span>
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={fetchUsers}
            className="px-3 py-1 bg-rose-600/30 hover:bg-rose-600 text-white rounded-lg text-xs font-semibold transition"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Indicador de carga principal */}
      {loading && users.length === 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-3 shadow-xl">
          <Loader2 className="w-6 h-6 animate-spin text-emerald-500" />
          <span>Cargando lista de usuarios desde la base de datos Supabase...</span>
        </div>
      )}

      {/* Mensaje descriptivo si no hay usuarios y no hay error */}
      {!loading && !errorMsg && users.length === 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-4 shadow-xl">
          <Users className="w-8 h-8 text-slate-600" />
          <div>
            <p className="font-bold text-slate-200 text-sm">No se encontraron usuarios registrados en la base de datos.</p>
            <p className="text-slate-500 mt-1">Verifica que las políticas RLS permitan lectura o haz clic en reintentar.</p>
          </div>
          <button
            onClick={fetchUsers}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer shadow-md shadow-emerald-600/20"
          >
            <RefreshCw className="w-4 h-4" />
            Reintentar Carga
          </button>
        </div>
      )}

      {/* SECCIÓN 1: Solicitudes Pendientes de Aprobación */}
      {(!loading || users.length > 0) && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-400" />
              <h2 className="text-sm font-bold text-white">Solicitudes Pendientes de Aprobación</h2>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {pendingRequests.length} pendientes
            </span>
          </div>

          {pendingRequests.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs">
              No hay solicitudes de acceso pendientes en este momento.
            </div>
          ) : (
            <div className="space-y-3">
              {pendingRequests.map((req) => {
                const displayName = req.display_name || req.full_name || req.email;
                const currentRole = selectedRoles[req.id] || req.role || 'cajero';
                const currentBranch = selectedBranches[req.id] || branches[0]?.id || '';

                return (
                  <div
                    key={req.id}
                    className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl flex flex-col lg:flex-row lg:items-center justify-between gap-4 hover:border-slate-700 transition"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-xs">{displayName}</span>
                        <span className="text-[10px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20 font-semibold">
                          Pendiente de Aprobación
                        </span>
                      </div>
                      <span className="text-xs text-slate-400 block mt-0.5 font-mono">{req.email}</span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      {/* Selector de Rol Válido */}
                      <div className="flex flex-col">
                        <label className="text-[9px] text-slate-500 uppercase font-bold mb-0.5">Rol Requerido</label>
                        <select
                          value={currentRole}
                          onChange={(e) => setSelectedRoles((prev) => ({ ...prev, [req.id]: e.target.value }))}
                          className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                        >
                          <option value="cajero">Cajero / TPV</option>
                          <option value="dependiente">Dependiente</option>
                          <option value="mesero">Mesero / Sala</option>
                          <option value="cocina">Cocinero / KDS</option>
                          <option value="gerente">Gerente de Sucursal</option>
                          <option value="admin">Administrador Global</option>
                        </select>
                      </div>

                      {/* Selector obligatorio de sucursal cargada desde public.branches */}
                      <div className="flex flex-col">
                        <label className="text-[9px] text-slate-500 uppercase font-bold mb-0.5">
                          Sucursal Obligatoria *
                        </label>
                        <select
                          value={currentBranch}
                          onChange={(e) => setSelectedBranches((prev) => ({ ...prev, [req.id]: e.target.value }))}
                          className="px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500 max-w-[200px]"
                        >
                          {branches.map((b) => (
                            <option key={b.id} value={b.id}>
                              {b.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="flex items-center gap-1.5 mt-auto pt-3">
                        <button
                          onClick={() => handleApproveUser(req.id, currentRole, currentBranch)}
                          disabled={actionLoading[req.id]}
                          className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shadow-md shadow-emerald-600/20"
                        >
                          {actionLoading[req.id] ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <UserCheck className="w-3.5 h-3.5" />
                          )}
                          Aprobar Acceso
                        </button>

                        <button
                          onClick={() => handleReject(req.id, req.email)}
                          disabled={actionLoading[req.id]}
                          className="px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white rounded-lg text-xs font-bold transition flex items-center gap-1 cursor-pointer disabled:opacity-50"
                        >
                          <UserX className="w-3.5 h-3.5" />
                          Rechazar
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* SECCIÓN 2: Personal Activo */}
      {(!loading || users.length > 0) && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-emerald-400" />
              <h2 className="text-sm font-bold text-white">Personal Activo</h2>
            </div>
            <span className="text-xs text-slate-400">{activeMembers.length} activos</span>
          </div>

          {activeMembers.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs">
              No hay usuarios activos registrados aún.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {activeMembers.map((m) => {
                const displayName = m.display_name || m.full_name || m.email;
                const isEditing = editingUserId === m.id;
                const isSelf = currentUser?.id === m.id;

                return (
                  <div
                    key={m.id}
                    className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex flex-col justify-between gap-3 hover:border-slate-700 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-xs block">{displayName}</span>
                          {isSelf && (
                            <span className="text-[9px] bg-slate-800 text-slate-300 px-1.5 py-0.2 rounded font-semibold">
                              Tú
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-400 block font-mono">{m.email}</span>
                        <span className="text-[10px] text-indigo-400 font-semibold flex items-center gap-1 mt-1">
                          <Building className="w-3 h-3" />
                          {m.branch_name}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                          {m.role}
                        </span>

                        {currentUser?.role === 'admin' && !isEditing && (
                          <button
                            onClick={() => {
                              setEditingUserId(m.id);
                              setEditFullName(m.full_name || '');
                              setEditRole(m.role || 'cajero');
                              setEditBranchId(m.branch_id || branches[0]?.id || 'sucursal-central');
                            }}
                            className="p-1 text-slate-400 hover:text-emerald-400 rounded-lg hover:bg-slate-800 transition cursor-pointer"
                            title="Editar rol y sucursal"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Modo edición con guardado directo en public.profiles */}
                    {isEditing && (
                      <div className="pt-2 border-t border-slate-800/80 flex flex-col gap-2.5 bg-slate-900/80 p-3 rounded-lg">
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wide flex items-center gap-1">
                          <Lock className="w-3 h-3" /> Editar Perfil & Asignación
                        </span>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                          <div>
                            <label className="text-[9px] text-slate-400 block mb-0.5">Nombre Completo</label>
                            <input
                              type="text"
                              value={editFullName}
                              onChange={(e) => setEditFullName(e.target.value)}
                              placeholder="Nombre y Apellidos"
                              className="w-full px-2 py-1.5 bg-slate-950 border border-slate-700 rounded text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                            />
                          </div>

                          <div>
                            <label className="text-[9px] text-slate-400 block mb-0.5">Rol en el Sistema</label>
                            <select
                              value={editRole || 'cajero'}
                              onChange={(e) => setEditRole(e.target.value)}
                              className="w-full px-2 py-1.5 bg-slate-950 border border-slate-700 rounded text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                            >
                              <option value="cajero">Cajero / TPV</option>
                              <option value="dependiente">Dependiente</option>
                              <option value="mesero">Mesero</option>
                              <option value="cocina">Cocina / KDS</option>
                              <option value="gerente">Gerente</option>
                              <option value="admin">Administrador</option>
                            </select>
                          </div>

                          <div>
                            <label className="text-[9px] text-slate-400 block mb-0.5">Sucursal Asignada *</label>
                            <select
                              value={editBranchId || (branches[0]?.id || '')}
                              onChange={(e) => setEditBranchId(e.target.value)}
                              className="w-full px-2 py-1.5 bg-slate-950 border border-slate-700 rounded text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                            >
                              {branches.map((b) => (
                                <option key={b.id} value={b.id}>
                                  {b.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>

                        <div className="flex items-center justify-end gap-2 pt-1">
                          <button
                            onClick={() => handleUpdateUser(m.id, editRole, editBranchId, editFullName)}
                            disabled={actionLoading[m.id]}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-bold transition flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shadow-md shadow-emerald-600/20"
                          >
                            {actionLoading[m.id] ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <Save className="w-3 h-3" />
                            )}
                            Guardar Cambios
                          </button>

                          <button
                            onClick={() => setEditingUserId(null)}
                            className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-semibold cursor-pointer flex items-center gap-1"
                          >
                            <X className="w-3 h-3" />
                            Cancelar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UsersView;
