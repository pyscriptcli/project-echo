-- Agent-mode RBAC DDL
-- Run this in the Supabase SQL Editor. Adds a per-user flag controlling whether
-- a user can enable "Agent mode" in Ask Echo.

alter table public.admin_users
  add column if not exists can_use_agent boolean not null default false;
