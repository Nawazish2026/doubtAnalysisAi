-- Public, no-login interactions are limited to these known demo fixture report IDs.
-- The browser cannot access these tables directly; only the server API uses them.
create table if not exists public.demo_report_allowlist (
    external_report_id text primary key
        references public.reports(external_report_id) on delete cascade
);

insert into public.demo_report_allowlist (external_report_id)
select 'R' || lpad(n::text, 3, '0')
from generate_series(1, 44) as series(n)
where exists (
    select 1 from public.reports r
    where r.external_report_id = 'R' || lpad(n::text, 3, '0')
)
on conflict (external_report_id) do nothing;

create table if not exists public.demo_review_actions (
    id bigserial primary key,
    report_id uuid not null references public.reports(id) on delete cascade,
    question_id text not null references public.questions(id),
    action text not null check (action in ('edited', 'approved', 'rejected')),
    actor_label text not null default 'Public demo visitor',
    reason text,
    details jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists demo_review_actions_created_idx
    on public.demo_review_actions(created_at desc);
create index if not exists demo_review_actions_report_idx
    on public.demo_review_actions(report_id, created_at desc);

create table if not exists public.demo_action_rate_limits (
    ip_hash text primary key,
    window_start timestamptz not null,
    request_count integer not null default 0
);

alter table public.demo_report_allowlist enable row level security;
alter table public.demo_review_actions enable row level security;
alter table public.demo_action_rate_limits enable row level security;

-- Deliberately no anon/authenticated policies or grants. The backend uses
-- its server-side database connection; browser clients cannot bypass the API.
