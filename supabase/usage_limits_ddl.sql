-- Usage limits + telemetry DDL
-- Run this in the Supabase SQL Editor.

-- Per-user configurable token budgets (daily/weekly) for Ask Echo + Agent mode.
-- A user with no row here uses the defaults in the app (daily 50k / weekly 250k).
create table if not exists public.usage_limits (
  user_id        uuid primary key,
  daily_limit    bigint not null default 50000,
  weekly_limit   bigint not null default 250000,
  updated_by     uuid,
  updated_at     timestamptz not null default now()
);

-- Telemetry rows: one per chat/AI call, carrying tokens used for that call.
-- (The table exists already; this is the guaranteed-shape reference.)
--   id           uuid primary key default gen_random_uuid()
--   user_id      uuid not null
--   tokens_used  bigint not null default 0
--   action       text
--   created_at   timestamptz not null default now()
