import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { supabase } from '../lib/supabase';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: 'active' | 'pending_approval' | 'rejected' | string;
  company_id: string | null;
  branch_id: string | null;
  company_name: string;
  branch_name: string;
  avatar_url?: string | null;
  created_at?: string;
  updated_at?: string;
}

interface AuthContextType {
  currentUser: UserProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<UserProfile>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<UserProfile | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => {
    if (typeof localStorage === 'undefined') return null;
    try {
      const cached = localStorage.getItem('bistro_user');
      return cached ? JSON.parse(cached) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState<boolean>(true);

  // Helper to fetch full profile enriched with company and branch names
  const fetchFullProfile = useCallback(async (userId: string, userEmail?: string): Promise<UserProfile | null> => {
    try {
      // 1. Fetch live profile
      const { data: profile, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .maybeSingle();

      if (error) {
        console.warn('[AuthContext] Error consultando perfil:', error.message);
      }

      if (!profile) {
        // Fallback: If user in Auth but has no row in profiles yet
        return {
          id: userId,
          email: userEmail || '',
          full_name: userEmail?.split('@')[0] || 'Usuario',
          role: 'pending',
          status: 'pending_approval',
          company_id: null,
          branch_id: null,
          company_name: '',
          branch_name: '',
        };
      }

      let companyName = profile.business_name || '';
      if (profile.company_id) {
        const { data: comp } = await supabase
          .from('companies')
          .select('id, name')
          .eq('id', profile.company_id)
          .maybeSingle();
        if (comp?.name) companyName = comp.name;
      }

      let branchName = '';
      if (profile.branch_id) {
        const { data: br } = await supabase
          .from('branches')
          .select('id, name')
          .eq('id', profile.branch_id)
          .maybeSingle();
        if (br?.name) branchName = br.name;
      }

      const full: UserProfile = {
        id: profile.id,
        email: userEmail || profile.email || '',
        full_name: profile.full_name || userEmail?.split('@')[0] || 'Usuario',
        role: profile.role || 'cajero',
        status: profile.status || 'pending_approval',
        company_id: profile.company_id || null,
        branch_id: profile.branch_id || null,
        company_name: companyName,
        branch_name: branchName,
        avatar_url: profile.avatar_url,
        created_at: profile.created_at,
        updated_at: profile.updated_at,
      };

      return full;
    } catch (err) {
      console.error('[AuthContext] Excepción en fetchFullProfile:', err);
      return null;
    }
  }, []);

  const refreshProfile = useCallback(async (): Promise<UserProfile | null> => {
    try {
      const { data: sessionData } = await supabase.auth.getSession();
      const user = sessionData?.session?.user;
      if (!user) {
        setCurrentUser(null);
        if (typeof localStorage !== 'undefined') localStorage.removeItem('bistro_user');
        return null;
      }

      const full = await fetchFullProfile(user.id, user.email);
      if (full) {
        setCurrentUser(full);
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('bistro_user', JSON.stringify(full));
          if (full.company_id) {
            localStorage.setItem('bistro_tenant_id', full.company_id);
          }
          if (full.role !== 'admin' && full.branch_id) {
            localStorage.setItem('active_branch_id', full.branch_id);
            localStorage.setItem('selected_branch_id', full.branch_id);
            localStorage.setItem('bistro_active_branch', full.branch_id);
          } else if (full.branch_id) {
            localStorage.setItem('active_branch_id', full.branch_id);
            localStorage.setItem('selected_branch_id', full.branch_id);
            localStorage.setItem('bistro_active_branch', full.branch_id);
          }
        }
      }
      return full;
    } catch (err) {
      console.error('[AuthContext] Error en refreshProfile:', err);
      return null;
    }
  }, [fetchFullProfile]);

  const login = async (email: string, password: string): Promise<UserProfile> => {
    const cleanEmail = email.trim().toLowerCase();
    const { data, error } = await supabase.auth.signInWithPassword({
      email: cleanEmail,
      password,
    });

    if (error || !data.user) {
      throw new Error(error?.message || 'Credenciales incorrectas. Verifique su correo y contraseña.');
    }

    const full = await fetchFullProfile(data.user.id, data.user.email);
    const finalProfile = full || {
      id: data.user.id,
      email: cleanEmail,
      full_name: cleanEmail.split('@')[0],
      role: 'cajero',
      status: 'pending_approval',
      company_id: null,
      branch_id: null,
      company_name: '',
      branch_name: '',
    };

    setCurrentUser(finalProfile);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('bistro_user', JSON.stringify(finalProfile));
      if (finalProfile.company_id) {
        localStorage.setItem('bistro_tenant_id', finalProfile.company_id);
      }
    }

    return finalProfile;
  };

  const logout = async (): Promise<void> => {
    try {
      await supabase.auth.signOut();
    } catch (err) {
      console.warn('[AuthContext] Error signing out:', err);
    } finally {
      setCurrentUser(null);
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('bistro_user');
      }
    }
  };

  // Initial session recovery & onAuthStateChange subscription
  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        const { data: sessionData } = await supabase.auth.getSession();
        const user = sessionData?.session?.user;
        if (user && isMounted) {
          const profile = await fetchFullProfile(user.id, user.email);
          if (profile && isMounted) {
            setCurrentUser(profile);
            if (typeof localStorage !== 'undefined') {
              localStorage.setItem('bistro_user', JSON.stringify(profile));
              if (profile.company_id) {
                localStorage.setItem('bistro_tenant_id', profile.company_id);
              }
            }
          }
        }
      } catch (err) {
        console.warn('[AuthContext] Error recuperando sesión inicial:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    initAuth();

    const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user && isMounted) {
        const profile = await fetchFullProfile(session.user.id, session.user.email);
        if (profile && isMounted) {
          setCurrentUser(profile);
          if (typeof localStorage !== 'undefined') {
            localStorage.setItem('bistro_user', JSON.stringify(profile));
            if (profile.company_id) {
              localStorage.setItem('bistro_tenant_id', profile.company_id);
            }
          }
        }
      } else if (event === 'SIGNED_OUT' && isMounted) {
        setCurrentUser(null);
        if (typeof localStorage !== 'undefined') {
          localStorage.removeItem('bistro_user');
        }
      }
    });

    return () => {
      isMounted = false;
      authListener?.subscription?.unsubscribe();
    };
  }, [fetchFullProfile]);

  return (
    <AuthContext.Provider value={{ currentUser, loading, login, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser utilizado dentro de un AuthProvider');
  }
  return context;
};
