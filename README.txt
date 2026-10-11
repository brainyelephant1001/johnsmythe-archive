John Smythe 2.0 — Clean Version 1.0

1. Keep your current johnsmythe-research folder as a backup.
2. Extract this ZIP as its own folder named John_Smythe_V1.
3. Open a terminal in that folder.
4. Run: python server.py
5. Open: http://127.0.0.1:5000

If dependencies are missing: python -m pip install -r requirements.txt

This release uses one external JavaScript file; the Python modules are necessary for research functionality.
Tests cover code compilation, import and local web routes; external source API search depends on network connectivity.


PUBLIC TESTER LOGGING (OPTIONAL; REQUIRED FOR PERSISTENT RECORDS)
----------------------------------------------------------------
No extra Python dependencies or additional application files are needed.
The engine runs normally without database credentials, but DOES NOT persist
search logs or accept feedback until the following storage is configured.

1. Create a Supabase project and open its SQL Editor. Run once:

create table public.tester_searches (
  id uuid primary key,
  created_at timestamptz not null default now(),
  question text not null,
  duration_seconds numeric,
  result_count integer,
  parliament_count integer,
  government_count integer,
  legislation_count integer,
  statistics_count integer,
  had_source_errors boolean
);
create table public.tester_feedback (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  search_id uuid not null references public.tester_searches(id),
  rating text not null check (rating in ('useful','partial','not_useful')),
  comment text
);
alter table public.tester_searches enable row level security;
alter table public.tester_feedback enable row level security;

2. In Render > Environment add SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
   Find them in Supabase project settings/API keys (use SECRET service-role,
   never anon/public). NEVER paste this key into GitHub, HTML, or JavaScript.
3. Redeploy Render so the backend receives those environment variables.
4. Test one search and submit feedback. Look under Supabase > Table Editor.

The database tables are private via RLS; server-side service-role key bypasses
RLS to write records. Do not give testers database/admin access.
The public frontend shows a notice; no account, IP address, or cookies are
recorded by this feature. Hosting providers may keep separate access logs.
The user may submit sensitive material in a question: set a retention period
and privacy policy before wider public rollout, and consider withholding query
text for non-consenting visitors. Feedback is optional.

Failure handling: A database-write failure is logged in the server logs and
search results still return normally; feedback returns an error rather than
claiming to be saved. This is not a complete security/rate-limiting solution;
add abuse protection and retention management before full public release.


PROFESSIONAL REPORT EXPORTS (October 2026)
-------------------------------------------
After research completes, choose Download Word (.docx), Download PDF (.pdf),
or Raw research data (.json). Formatted exports are generated server-side
from the search response and include linked sources, dates, evidence assessments,
and explicit verification limitations. They do not claim AI-generated conclusions.

Install updated requirements.txt and redeploy Render after uploading this whole folder.
Render start command remains: gunicorn server:server (ensure gunicorn is
provided by the Render environment; install it if needed).

No Google Drive login or automatic Drive upload is implemented; the .docx
opens with Microsoft Word or can be uploaded/opened in Google Docs.
