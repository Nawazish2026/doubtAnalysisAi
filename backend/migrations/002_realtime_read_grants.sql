-- Apply after 001_initial_schema.sql if that migration was already run.
-- Allows authenticated browser sessions to receive Realtime change events.
-- Row Level Security policies from 001 continue to restrict visible records.
-- Browser mutations remain disabled; writes go through the FastAPI service.

grant select on public.profiles to authenticated;
grant select on public.questions to authenticated;
grant select on public.reports to authenticated;
grant select on public.triage_results to authenticated;
grant select on public.repair_proposals to authenticated;
grant select on public.question_versions to authenticated;
grant select on public.review_decisions to authenticated;
grant select on public.audit_logs to authenticated;
