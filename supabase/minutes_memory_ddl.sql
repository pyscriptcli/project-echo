-- Minutes Memory per-user persistence DDL
-- Run this in the Supabase SQL Editor BEFORE using the meeting-processing flow.
--
-- Stores approved Minutes-of-Meeting output so Echo can learn how each user
-- wants their minutes formatted (few-shot style learning).
-- Enforced in app code (service-role key); user_id is a uuid matching admin_users.id.

create table if not exists public.minutes_memory (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null,
  meeting_id    text not null,
  client_name   text not null default '',
  approved_items jsonb not null default '[]'::jsonb,
  other_discussions text not null default '',
  created_at    timestamptz not null default now()
);
create index if not exists ndx_minutes_memory_user on public.minutes_memory (user_id, created_at desc);
