-- Acadza live backend schema.
-- Run this in the Supabase SQL Editor or with your migration tool.
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'student' check (role in ('student','faculty','admin')),
  display_name text,
  external_student_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.questions (
  id text primary key,
  question_type text not null,
  subject text,
  chapter text,
  level text,
  content jsonb not null default '{}'::jsonb,
  version integer not null default 1 check (version >= 1),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  external_report_id text unique,
  question_id text not null references public.questions(id),
  student_user_id uuid references public.profiles(id),
  student_ref text,
  source text not null default 'web' check (source in ('web','android','ios','import')),
  comment text not null check (char_length(comment) between 3 and 3000),
  status text not null default 'faculty_review'
    check (status in ('pending_triage','faculty_review','approved','rejected','corrected','no_change')),
  idempotency_key text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (student_user_id is not null or student_ref is not null)
);
create unique index if not exists reports_student_idempotency_unique
  on public.reports(student_user_id, idempotency_key)
  where student_user_id is not null and idempotency_key is not null;
create index if not exists reports_queue_idx on public.reports(status, created_at desc);
create index if not exists reports_question_idx on public.reports(question_id, created_at desc);

create table if not exists public.triage_results (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null references public.reports(id) on delete cascade,
  verdict text not null,
  repair text,
  route text not null,
  confidence numeric(4,3) check (confidence between 0 and 1),
  evidence text,
  student_reply text,
  edit jsonb,
  engine_version text not null default 'rules-v1',
  created_at timestamptz not null default now()
);
create index if not exists triage_results_report_idx
  on public.triage_results(report_id, created_at desc);

create table if not exists public.repair_proposals (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null references public.reports(id) on delete cascade,
  question_id text not null references public.questions(id),
  repair text not null,
  edit jsonb,
  note text,
  status text not null default 'pending' check (status in ('pending','approved','rejected','superseded')),
  base_question_version integer not null,
  proposed_by uuid references public.profiles(id),
  reviewed_by uuid references public.profiles(id),
  reviewed_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists proposals_report_idx on public.repair_proposals(report_id, created_at desc);

create table if not exists public.question_versions (
  id bigserial primary key,
  question_id text not null references public.questions(id),
  version integer not null,
  snapshot jsonb not null,
  changed_by uuid references public.profiles(id),
  change_reason text not null,
  created_at timestamptz not null default now(),
  unique(question_id, version)
);

create table if not exists public.review_decisions (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null references public.reports(id),
  proposal_id uuid references public.repair_proposals(id),
  faculty_id uuid not null references public.profiles(id),
  action text not null check (action in ('approved','rejected')),
  reason text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
  id bigserial primary key,
  actor_id uuid references public.profiles(id),
  entity_type text not null,
  entity_id text not null,
  action text not null,
  before_state jsonb,
  after_state jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists audit_entity_idx
  on public.audit_logs(entity_type, entity_id, created_at desc);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at before update on public.profiles
for each row execute function public.set_updated_at();
drop trigger if exists questions_set_updated_at on public.questions;
create trigger questions_set_updated_at before update on public.questions
for each row execute function public.set_updated_at();
drop trigger if exists reports_set_updated_at on public.reports;
create trigger reports_set_updated_at before update on public.reports
for each row execute function public.set_updated_at();

-- New Supabase Auth users become students. Promote faculty/admin explicitly
-- from a trusted admin workflow; never accept a role from public sign-up input.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles(id, role, display_name)
  values (
    new.id,
    'student',
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();

create or replace function public.has_faculty_role()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.profiles
    where id = (select auth.uid()) and role in ('faculty','admin')
  );
$$;

alter table public.profiles enable row level security;
alter table public.questions enable row level security;
alter table public.reports enable row level security;
alter table public.triage_results enable row level security;
alter table public.repair_proposals enable row level security;
alter table public.question_versions enable row level security;
alter table public.review_decisions enable row level security;
alter table public.audit_logs enable row level security;

-- Profiles: users can see themselves; faculty may see profiles for review attribution.
drop policy if exists profiles_read_self_or_faculty on public.profiles;
create policy profiles_read_self_or_faculty on public.profiles for select to authenticated
using (id = (select auth.uid()) or public.has_faculty_role());

-- All signed-in users can read active questions. Writes are performed by trusted backend only.
drop policy if exists questions_read_authenticated on public.questions;
create policy questions_read_authenticated on public.questions for select to authenticated
using (is_active or public.has_faculty_role());

-- Students can see/insert only their own reports; faculty can review all.
drop policy if exists reports_read_owner_or_faculty on public.reports;
create policy reports_read_owner_or_faculty on public.reports for select to authenticated
using (student_user_id = (select auth.uid()) or public.has_faculty_role());
drop policy if exists reports_insert_owner on public.reports;
create policy reports_insert_owner on public.reports for insert to authenticated
with check (student_user_id = (select auth.uid()));
drop policy if exists reports_update_faculty on public.reports;
create policy reports_update_faculty on public.reports for update to authenticated
using (public.has_faculty_role()) with check (public.has_faculty_role());

drop policy if exists triage_read_owner_or_faculty on public.triage_results;
create policy triage_read_owner_or_faculty on public.triage_results for select to authenticated
using (exists (select 1 from public.reports r where r.id = report_id and
  (r.student_user_id = (select auth.uid()) or public.has_faculty_role())));

drop policy if exists proposals_read_owner_or_faculty on public.repair_proposals;
create policy proposals_read_owner_or_faculty on public.repair_proposals for select to authenticated
using (public.has_faculty_role() or exists (
  select 1 from public.reports r where r.id = report_id and r.student_user_id = (select auth.uid())
));

drop policy if exists versions_read_faculty on public.question_versions;
create policy versions_read_faculty on public.question_versions for select to authenticated
using (public.has_faculty_role());

drop policy if exists decisions_read_faculty on public.review_decisions;
create policy decisions_read_faculty on public.review_decisions for select to authenticated
using (public.has_faculty_role());

drop policy if exists audit_read_faculty on public.audit_logs;
create policy audit_read_faculty on public.audit_logs for select to authenticated
using (public.has_faculty_role());

-- Enable database change events for Supabase Realtime. This is safe to rerun.
do $$
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    begin alter publication supabase_realtime add table public.questions; exception when duplicate_object then null; end;
    begin alter publication supabase_realtime add table public.reports; exception when duplicate_object then null; end;
    begin alter publication supabase_realtime add table public.repair_proposals; exception when duplicate_object then null; end;
    begin alter publication supabase_realtime add table public.review_decisions; exception when duplicate_object then null; end;
    begin alter publication supabase_realtime add table public.audit_logs; exception when duplicate_object then null; end;
  end if;
end;
$$;
