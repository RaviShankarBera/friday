-- Run in the chosen Supabase project's SQL editor. Firebase UID is the owner.
create table if not exists public.tasks (
 id uuid primary key, user_id text not null, prompt text not null,
 status text not null check(status in ('queued','running','done','failed')),
 created_at timestamptz not null default now(), started_at timestamptz,
 finished_at timestamptz, result text, error text, mode text
);
create index if not exists tasks_owner on public.tasks(user_id,created_at desc);
create table if not exists public.messages (
 id bigint generated always as identity primary key, user_id text not null,
 role text not null check(role in ('user','assistant')), content text not null,
 created_at timestamptz not null default now()
);
create index if not exists messages_owner on public.messages(user_id,id desc);
create table if not exists public.workspace_files (
 id uuid primary key default gen_random_uuid(), user_id text not null,
 name text not null, content text not null check(length(content)<=64000),
 created_at timestamptz not null default now(), unique(user_id,name)
);
alter table public.tasks enable row level security;
alter table public.messages enable row level security;
alter table public.workspace_files enable row level security;
-- No anon/authenticated-client policies. Only the server's service role can access.
revoke all on public.tasks,public.messages,public.workspace_files from anon,authenticated;
-- Mark tasks stranded by a hard serverless timeout as failed. A durable worker/queue is
-- required before unattended jobs; this starter uses a bounded request lifecycle.
create or replace function public.fail_stale_tasks() returns void
language sql security definer set search_path = public as $$
 update public.tasks set status='failed',error='Execution timeout; outcome not confirmed',finished_at=now()
 where status in ('queued','running') and created_at < now()-interval '5 minutes';
$$;
revoke execute on function public.fail_stale_tasks() from public,anon,authenticated;
grant execute on function public.fail_stale_tasks() to service_role;
-- Enforce one active task per user even if concurrent requests pass the precheck.
create unique index if not exists one_active_task_per_user
on public.tasks(user_id) where status in ('queued','running');
-- Fixed-window usage control for voice. Key uses Firebase UID and UTC day.
create table if not exists public.voice_usage (
 user_id text not null, day date not null, characters integer not null default 0,
 primary key(user_id,day)
);
alter table public.voice_usage enable row level security;
revoke all on public.voice_usage from anon,authenticated;
create or replace function public.reserve_voice_characters(owner_id text,amount integer,daily_cap integer)
returns boolean language plpgsql security definer set search_path=public as $$
begin
 if amount<1 or amount>1000 or amount>daily_cap or daily_cap<1 or daily_cap>5000 then return false; end if;
 insert into public.voice_usage(user_id,day,characters) values(owner_id,current_date,amount)
 on conflict(user_id,day) do update set characters=voice_usage.characters+excluded.characters
 where voice_usage.characters+excluded.characters<=daily_cap;
 return found;
end;
$$;
revoke execute on function public.reserve_voice_characters(text,integer,integer) from public,anon,authenticated;
grant execute on function public.reserve_voice_characters(text,integer,integer) to service_role;
-- Explicit backend privileges. RLS bypass does not replace SQL table grants.
grant usage on schema public to service_role;
grant select,insert,update,delete on public.tasks,public.messages,public.workspace_files,public.voice_usage to service_role;
grant usage,select on sequence public.messages_id_seq to service_role;
