-- Run this in Supabase Dashboard -> SQL Editor -> New query.
-- Each authenticated user can access only their own row and task list.
create table if not exists public.student_data (
  user_id uuid primary key references auth.users(id) on delete cascade,
  tasks jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.student_data enable row level security;

drop policy if exists "Students can read their own data" on public.student_data;
create policy "Students can read their own data"
  on public.student_data for select
  to authenticated
  using (auth.uid() = user_id);

drop policy if exists "Students can create their own data" on public.student_data;
create policy "Students can create their own data"
  on public.student_data for insert
  to authenticated
  with check (auth.uid() = user_id);

drop policy if exists "Students can update their own data" on public.student_data;
create policy "Students can update their own data"
  on public.student_data for update
  to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
