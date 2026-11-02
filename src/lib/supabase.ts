import { createClient } from '@supabase/supabase-js';

export const SUPABASE_URL =
  (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_SUPABASE_URL) ||
  (typeof window !== 'undefined' && localStorage.getItem('bistro_supabase_url')) ||
  'https://yohpvligtqppphjrmxeq.supabase.co';

export const SUPABASE_ANON_KEY =
  (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_SUPABASE_ANON_KEY) ||
  (typeof window !== 'undefined' && localStorage.getItem('bistro_supabase_anon_key')) ||
  'sb_publishable_couMOQUQA8PDOqHvY1XvnA_jG_3_E8W';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: false,
  },
});

if (typeof window !== 'undefined') {
  (window as any).__BISTRO_SUPABASE_CLIENT__ = supabase;
}
