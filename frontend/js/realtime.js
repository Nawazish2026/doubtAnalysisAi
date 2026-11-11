import { getSupabase } from "./supabase-client.js";

export function subscribeFacultyChanges(onChange) {
  const client = getSupabase();
  const channel = client
    .channel("ac adza-faculty-live")
    .on("postgres_changes", { event: "*", schema: "public", table: "reports" }, onChange)
    .on("postgres_changes", { event: "*", schema: "public", table: "questions" }, onChange)
    .on("postgres_changes", { event: "*", schema: "public", table: "repair_proposals" }, onChange)
    .on("postgres_changes", { event: "*", schema: "public", table: "review_decisions" }, onChange)
    .subscribe();

  return () => client.removeChannel(channel);
}
