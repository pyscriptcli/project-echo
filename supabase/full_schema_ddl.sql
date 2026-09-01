-- ============================================================
-- Project Echo — consolidated schema DDL (self-healing reference)
-- Run in the Supabase SQL Editor whenever a save fails with a
-- PGRST205 (table missing) / 42P10 (constraint missing) error.
-- Idempotent: safe to run repeatedly.
-- ============================================================

-- 1) usage_limits — per-user token budgets (Rate Limits tab + Ask Echo limits)
create table if not exists public.usage_limits (
  user_id      uuid primary key,
  daily_limit  bigint not null default 50000,
  weekly_limit bigint not null default 250000,
  updated_by   uuid,
  updated_at   timestamptz not null default now()
);

-- 2) daily_logs UNIQUE(user_id, log_date) — required by upsert_log(42P10 fix)
--    Keeps the newest row per (user, date), drops any older duplicates.
delete from public.daily_logs
where id not in (
  select distinct on (user_id, log_date) id
  from public.daily_logs
  order by user_id, log_date, created_at desc
);
alter table public.daily_logs
  add constraint daily_logs_user_date_unique unique (user_id, log_date);

-- 3) user_usage.event_type — column telemetry writes (PGRST204 fix)
alter table public.user_usage
  add column if not exists event_type text not null default 'chat';

-- 4) admin_users — role + agent RBAC columns (auth + agent mode)
alter table public.admin_users
  add column if not exists role text not null default 'member',
  add column if not exists can_use_agent boolean not null default false;

-- 5) minutes_memory — minutes style-learning table
create table if not exists public.minutes_memory (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null,
  meeting_id        text not null,
  client_name       text not null default '',
  approved_items    jsonb not null default '[]'::jsonb,
  other_discussions text not null default '',
  created_at        timestamptz not null default now()
);
create index if not exists ndx_minutes_memory_user on public.minutes_memory (user_id, created_at desc);

-- 6) echo_context unique (category, key) — for upsert_echo_context (usually already there)
create unique index if not exists echo_context_category_key_unique on public.echo_context (category, key);
