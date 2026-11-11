import { api } from "./api.js";
import { getCurrentUser, signIn, signOut } from "./supabase-client.js";
import { subscribeFacultyChanges } from "./realtime.js";

let stopRealtime;

async function loadQueue() {
  return api.getQueue("open");
}

async function startRealtime(onRefresh) {
  if (stopRealtime) stopRealtime();
  stopRealtime = subscribeFacultyChanges(async (event) => {
    // Debounce at the UI layer if several table events arrive for one transaction.
    await onRefresh(event);
  });
}

window.ACADZA_LIVE = {
  signIn,
  signOut,
  getCurrentUser,
  loadQueue,
  submitProposal: api.createProposal,
  approve: api.approve,
  reject: api.reject,
  subscribe: startRealtime,
  getAuditLogs: api.getAuditLogs,
};

window.dispatchEvent(new CustomEvent("ac adza-live-ready"));
