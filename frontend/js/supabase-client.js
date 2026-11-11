import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

let client;

export function getSupabase() {
  if (client) return client;
  const config = window.ACADZA_CONFIG;
  if (!config?.supabaseUrl || !config?.supabasePublishableKey) {
    throw new Error("Set supabaseUrl and supabasePublishableKey in frontend/config.js");
  }
  client = createClient(config.supabaseUrl, config.supabasePublishableKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });
  return client;
}

export async function signIn(email, password) {
  const { data, error } = await getSupabase().auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

export async function signOut() {
  const { error } = await getSupabase().auth.signOut();
  if (error) throw error;
}

export async function getAccessToken() {
  const { data, error } = await getSupabase().auth.getSession();
  if (error) throw error;
  const token = data.session?.access_token;
  if (!token) throw new Error("Please sign in before using the faculty console");
  return token;
}

export async function getCurrentUser() {
  const { data, error } = await getSupabase().auth.getUser();
  if (error) throw error;
  return data.user;
}
