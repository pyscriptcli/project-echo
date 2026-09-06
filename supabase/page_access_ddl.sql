-- Project Echo — per-user page access policies
-- Safe to run repeatedly. Existing users keep full member-page access until
-- an administrator saves an explicit allowlist for that user.

create table if not exists public.user_page_access (
  user_id       uuid primary key references public.admin_users(id) on delete cascade,
  allowed_pages text[] not null default '{}',
  updated_by    uuid references public.admin_users(id),
  updated_at    timestamptz not null default now()
);

create index if not exists user_page_access_updated_at_idx
  on public.user_page_access (updated_at desc);
