-- Notebook per-user persistence DDL
-- Run this in the Supabase SQL Editor BEFORE using the Notebook screen.
--
-- Auth model: the app holds the service-role Supabase key and enforces
-- per-user separation in application code by always filtering/inserting
-- on user_id (a uuid matching admin_users.id). RLS is intentionally left
-- disabled (no auth.uid() policies), matching utils/db.py and utils/auth.py.

create table if not exists public.notepad_docs (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.admin_users(id) on delete cascade,
  title       text not null default 'Untitled',
  content     text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index if not exists ndx_notepad_user on public.notepad_docs (user_id);

create table if not exists public.daily_logs (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.admin_users(id) on delete cascade,
  log_date    date not null,
  client      text not null default '',
  admin       text not null default '',
  adhoc       text not null default '',
  meeting     text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  unique (user_id, log_date)
);
create index if not exists ndx_dailylog_user on public.daily_logs (user_id);
