# Component map

Frontend: public/index.html, style.css, app.js, icon.svg, manifest.webmanifest. Responsive UI, countdown listening, text fallback, account dialog and task dashboard. Uses safe text DOM rendering. Local mode cannot run general tasks.

API: root app.py. FastAPI health/config/tasks/memory/tts endpoints. Exact Origin and authenticated Firebase ID token required for writes. Same-origin deployment only. Config endpoint exposes only public Firebase identifiers and capability booleans.

Database: database/schema.sql. Supabase tables tasks/messages/workspace_files. RLS on with no anon policies. Service role server-only. Task queries and workspace tools bind Firebase UID. Stale-task recovery function marks unconfirmed executions failed.

Authentication: Firebase password REST flow. Password goes to Google's endpoint, not server. Create-account sends Firebase verification email; verification required before backend tasks. Token in memory, no refresh persistence. Owner allowlist env supported. Google login UI is future work.

Memory: last 12 messages sent to AI provider, per-user stored history. DELETE /api/memory deletes only conversation messages. Retention/account deletion not complete.

Tools: read/list server text workspace, read-only. No unrestricted web, shell, devices, automated account mutation or sending. Model loop capped at three iterations and a 45-second deadline. A serverless request is not an unattended background job.

Voice: browser recognition with max 12-second window. ElevenLabs server TTS optional. Voice/model IDs come from provider account setup, not guessing. Browser speech fallback is explicitly labeled. Language coverage varies, text remains fallback.

Email: Resend key may be provisioned but endpoint stays disabled. Sender verification plus recipient/content approval flow must be built before sending. Firebase handles account verification independently.

Deployment: Vercel detects root app.py and serves public/ assets from CDN. Set all environment vars privately. Supabase project/schema, Firebase project, model and voice credentials are prerequisites. No billing automatically enabled.
