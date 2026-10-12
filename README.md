# FRIDAY | Voice-first command center

FRIDAY is a modular starter app, not unrestricted autonomous AI. Account provisioning and production integration are separate from the working browser preview. No secrets are included.

## Chosen stack

- Frontend: responsive HTML/CSS/JavaScript, cinematic arc core, voice/text controls and task dashboard.
- API: FastAPI (`app.py`), targeted to Vercel's Python runtime.
- Database/backend storage: Supabase Postgres (`database/schema.sql`).
- Authentication: Firebase email/password REST flow and server verification of Firebase ID tokens.
- Memory: per-user conversations in Supabase; last 12 messages used by the configured model.
- AI: Gemini or OpenAI-compatible provider with a bounded tool loop. Local fallback is the default.
- Voice: optional female ElevenLabs voice configured by voice ID; browser TTS fallback.
- Email: Resend setup reserved; sending is not implemented/activated. Firebase account creation uses Firebase's verification email, not Resend.
- Deployment: Vercel same-origin frontend/API. GitHub Pages can be a frontend-only preview.

## Start

Python 3.12+: `pip install -r requirements.txt`, then `uvicorn app:app --reload --port 8080`. Configure server environment from `.env.example` securely; this file is only a template, not automatically loaded. Serve `public/` on the same origin when deploying. Local API docs are at `/docs`. Run tests with `python -m unittest discover -s tests -v`.

Vercel currently detects a FastAPI `app` instance in root `app.py`. Static files live in `public/`. See https://vercel.com/docs/frameworks/backend/fastapi . Import this repository, confirm the deployment domain, set `APP_ORIGIN` to its exact HTTPS origin, and add server environment variables privately. Run the schema in the intended Supabase project's SQL editor. Do not publish keys in Git, screenshots, frontend config or build logs.

## Authentication

Enable Firebase email/password authentication. Server validates token signature, audience, issuer, expiry and verified email. Restrict the owner with `ALLOWED_USER_EMAIL=rsbera707@gmail.com`. Add deployed domain to Firebase authorized domains. Firebase web API key is a public app identifier, not a service credential. Supabase service-role key stays server-side. Row level security is enabled with no client policies; all API queries are scoped to the verified Firebase UID. Email/password tokens stay in memory and expire; sign in again on expiry. Google popup login is included. No MFA, password-reset UI, session refresh, account deletion or abuse-resistant production auth is included yet.

## Agent and dashboard

One bounded request runs a task through queued/running/done/failed. Results include whether local fallback or a model was used. `done` means the response finished, not that an unavailable external action was performed. Supabase-backed dashboard refreshes every 10 seconds. This is not a durable unattended worker/queue; hard serverless timeouts can strand jobs. The schema's stale-task function marks them failed on dashboard reads. Before long autonomous workflows, add a durable job runner, retries and effect approvals.

Available tools are read-only list/read of user workspace text rows. Device control, arbitrary code execution, open internet fetch/search, automated account actions, file writes, messages, purchases and scheduling are disabled. No fake tool results are shown. External tool content is treated as untrusted data. A proper sandbox and permission UI are later work.

## Voice

Tap to listen for at most 12 seconds, then auto-sleep. Recognition may stop sooner depending on browser/service. Stop cancels listening and playback. Silence gives a gentle sleep response. Browser recognition needs HTTPS/localhost, mic permission and may send audio to the browser provider. Available languages/quality vary. Language choices are not a guarantee of recognition or speech support.

ElevenLabs requires a configured key, verified voice ID and model. Enable only within reviewed free quota with no billing upgrade. Text sent for TTS goes to ElevenLabs. If the service or playback fails, the UI reports fallback to browser voice. No movie-actor voice cloning. Waveform is a state animation, not an audio analyzer. English/Hindi are primary. Additional named language selection is limited to browser locale attempts and the model/voice engine's actual capabilities. There is no claim of 28-language coverage.

## Privacy and production limits

Local command log resets on reload. Authenticated task prompts, results and conversation memory go to the chosen Supabase project and, in AI mode, the model provider. TTS text goes to ElevenLabs when enabled. Do not enter secrets in prompts. Delete-memory control deletes conversation rows, not task history or workspace rows. Backups, retention and full account deletion need setup. Free-tier quotas, inactivity, data handling and plan terms must be verified for each configured service; no permanent-free guarantee.

Independent fan-inspired project, not affiliated with Marvel or connected to Instinct. Android/iOS and native permissions are later phases.

Temporary integration fixtures: ENABLE_TEST_USER=true permits only the explicitly configured TEST_USER_EMAIL in addition to the owner. This still requires verified Firebase tokens and separate UID ownership. Disable it and delete fixtures after tests. Never leave a broadly usable test login active.
