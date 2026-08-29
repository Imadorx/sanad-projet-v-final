# SANAD Healthcare Platform

AI-powered healthcare management platform built on Odoo 19 Enterprise/Community,
with a React frontend and a configurable AI assistant layer. Built per the SANAD
Master PRD, Phases 1–9 complete.

## Project Structure

```
sanad/
├── custom-addons/          # 7 Odoo modules (backend + REST API)
│   ├── sanad_core/         # Identity, roles, orgs, AI audit log, auth API
│   ├── sanad_patient/      # Patient model, care-relationship RBAC backbone
│   ├── sanad_medical/      # Medical records, consultations, prescriptions
│   ├── sanad_laboratory/   # Lab requests/results workflow, KPI evolution
│   ├── sanad_pharmacy/     # Prescription reception workflow
│   ├── sanad_chat/         # Secure messaging on bus.bus
│   └── sanad_ai/           # AI assistant: search/explain/translate/TTS,
│                            #   PHI anonymization, safety filter, audit log
├── frontend/                # React (Vite) SPA - 5 role-based dashboards
├── docker/                  # docker-compose, Odoo config, Nginx, Dockerfiles
├── .env.example
└── README.md                 # this file
```

## Architecture Summary

- **Identity**: `res.partner`/`res.users` are the source of truth; custom
  models hold only healthcare-specific fields (see `sanad.doctor`, `sanad.patient`).
- **RBAC backbone**: `sanad.patient.doctor.rel` (active care relationship) is
  checked at both the `ir.rule` record-rule layer and as a Python
  `@api.constrains` on every clinical model - defense in depth against RPC bypass.
- **REST API**: 34 endpoints across 6 modules (`/api/auth/*`, `/api/patients/*`,
  `/api/consultations`, `/api/prescriptions`, `/api/lab-requests/*`,
  `/api/lab-results/*`, `/api/pharmacy/*`, `/api/chat/*`, `/api/ai/*`), all
  `auth='user'` - they inherit Odoo's record rules automatically and never
  re-implement authorization logic.
- **AI safety pipeline** (`sanad_ai`): authorization check → PHI anonymization
  → pluggable provider call → output safety filter → audit log, in that fixed
  order, for every request.
- **Real-time chat**: Odoo native `bus.bus`, with a polling fallback
  (`/api/chat/poll`) for the standalone React client.

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (only needed for local frontend development outside Docker)
- Python 3.11+ (only needed to run Odoo tests outside Docker)

## Installation & Startup (Docker - recommended)

```bash
cd sanad
cp .env.example .env
# edit .env: set a real POSTGRES_PASSWORD
# also edit docker/odoo.conf directly: set a real admin_passwd
#   (not controlled via .env - see comments in that file)

cd docker
docker compose up -d
```

This starts:
- PostgreSQL on `5432` (internal)
- Odoo (backend + REST API) on `http://localhost:8069`
- React frontend (production build, served by Nginx) on `http://localhost:3000`

## Database Initialization

The first Odoo start does not auto-create the SANAD database. Initialize it:

```bash
# Create the database and install all SANAD modules in dependency order
docker exec -it sanad_odoo odoo \
  -d sanad_db \
  -i sanad_core,sanad_patient,sanad_medical,sanad_laboratory,sanad_pharmacy,sanad_chat,sanad_ai \
  --without-demo=False \
  --stop-after-init

# Restart normally
docker compose restart odoo
```

Omit `--without-demo=False` for a production database with no demo data.

## Development Startup (without Docker)

**Backend:**
```bash
# Requires a local Odoo 19 + PostgreSQL install
odoo -c docker/odoo.conf --addons-path=custom-addons -d sanad_db \
  -i sanad_core,sanad_patient,sanad_medical,sanad_laboratory,sanad_pharmacy,sanad_chat,sanad_ai
```

**Frontend:**
```bash
cd frontend
cp .env.example .env.local   # set VITE_ODOO_URL if not using the Vite proxy
npm install
npm run dev
# → http://localhost:3000, proxies /api to http://localhost:8069
```

## Production Deployment

1. Set a strong `POSTGRES_PASSWORD` in `.env`, and a strong `admin_passwd`
   directly in `docker/odoo.conf` (not controlled via `.env` - see that
   file's comments for why).
2. Edit `docker/odoo.conf`: set `list_db = False` (don't expose the database
   list publicly) and `admin_passwd` to a strong value.
3. Put the whole stack behind a TLS-terminating reverse proxy (or extend
   `docker/nginx.conf` with a `listen 443 ssl` block) - PRD 19 requires HTTPS
   in production.
4. Configure the AI provider: Settings → General Settings → SANAD AI, or set
   `sanad_ai.provider` / `sanad_ai.api_key` / `sanad_ai.model` via
   `ir.config_parameter`. Defaults to the safe offline mock provider until
   configured - no external AI calls happen until you explicitly enable one.
5. Set up regular PostgreSQL backups (`pg_dump` on a cron, or your platform's
   managed backup mechanism) - not automated in this delivery.
6. Build the frontend for production: `docker compose build frontend` (already
   done by `docker compose up`, but rebuild after any frontend change).

## Testing

**Odoo backend tests** (18 test files, 6 modules, ~50 test methods):
```bash
docker exec -it sanad_odoo odoo \
  -d sanad_db --test-enable --stop-after-init \
  -i sanad_core,sanad_patient,sanad_medical,sanad_laboratory,sanad_pharmacy,sanad_chat,sanad_ai \
  --log-level=test
```

Run a specific module's tests only:
```bash
docker exec -it sanad_odoo odoo -d sanad_db --test-enable --test-tags sanad_rbac --stop-after-init
```
Available tags: `sanad_rbac`, `sanad_core`, `sanad_medical`, `sanad_laboratory`,
`sanad_pharmacy`, `sanad_chat`, `sanad_ai`, `sanad_e2e`.

**Frontend build validation:**
```bash
cd frontend
npm install
npm run build   # must complete with 0 errors
```

**IMPORTANT - test execution disclosure**: the 18 Odoo test files were written
following Odoo 19's `TransactionCase` testing framework and validated for
Python syntax correctness (`ast.parse`, 0 errors). The pure-Python AI safety
functions (`anonymizer.py`, `safety_filter.py`) were additionally executed
directly and verified against real inputs during development (this caught and
fixed a real date/phone-regex ordering bug). However, the Odoo-ORM-dependent
tests (everything using `TransactionCase`, i.e. all 18 files) have **not**
been executed against a live Odoo+PostgreSQL instance, because no such runtime
is available in the environment used to build this deliverable. Run the
command above on your machine to get actual pass/fail results before treating
this test suite as verified.

## Default/Demo Credentials

Demo data (loaded with `--without-demo=False`) creates:

| Role | Login | Notes |
|---|---|---|
| Doctor | `doctor.demo@sanad-health.example.com` | Dr. Amina El Fassi, Cardiology |
| Patient | `patient.demo@sanad-health.example.com` | Youssef Bennani |

No password is set on demo users by default - set one via Odoo's
"Invite user" / password-reset flow, or `odoo shell` for local testing:
```python
env['res.users'].search([('login','=','doctor.demo@sanad-health.example.com')]).write({'password': 'demo1234'})
```

Admin access: use the Odoo master database admin created at `docker compose up`
first-run, or promote a user via `Settings > Users > [user] > Access Rights`.

## Complete List of Implemented Features

**Backend (7 Odoo modules, 77 Python files, 34 XML files, 34 REST endpoints):**
- Identity foundation, multi-role RBAC, doctor/patient/org models
- Care-relationship-based access control (record rules + ORM constraints)
- Medical records, consultations, prescriptions
- Laboratory request workflow (Draft→Sent→Accepted→Processing→Completed/Cancelled),
  results, KPI evolution tracking
- Pharmacy workflow (Pending→Received→Prepared→Completed)
- Secure chat with server-side pairing enforcement, bus.bus real-time delivery
- AI assistant: authorized search, document/result explanation, translation
  (AR/FR/EN), text-to-speech (browser Web Speech API), PHI anonymization,
  pluggable provider (mock/Anthropic/OpenAI), output safety filtering,
  full audit logging

**Frontend (React SPA, 42 JS/JSX files):**
- Session-based auth, protected routes, role-based navigation
- 5 dashboards: Patient, Doctor, Laboratory, Pharmacy, Admin
- Medical record viewer, consultation/prescription create forms
- Lab request workflow UI, result upload, KPI charts (Recharts)
- Pharmacy queue with status transitions
- Secure chat widget (polling-based real-time)
- Patient AI Assistant page (search/explain/translate/read-aloud)
- Notification bell, loading/error/empty states throughout, responsive layout

**Testing:**
- 18 Odoo test files covering RBAC, doctor model integrity, care-relationship
  enforcement, consultation/prescription constraints, lab workflow, KPI
  evolution, pharmacy workflow + org-scoped visibility, chat pairing
  enforcement, AI anonymization, AI safety filtering, AI authorization/audit
  logging, and one full end-to-end journey test

**Deployment:**
- Docker Compose (PostgreSQL, Odoo, Nginx-served frontend)
- Production Nginx reverse-proxy config (same-origin API, no CORS needed)
- Environment variable template

## Known Limitations

1. **Odoo tests not executed against a live runtime** in this delivery
   environment (see Testing section above) - syntax-validated only, must be
   run on your machine for real pass/fail results.
2. **Chat real-time delivery uses short-polling** (4-8s intervals) for the
   standalone React client rather than native WebSocket subscription to
   Odoo's bus protocol - a deliberate, documented tradeoff (see
   `sanad_chat/controllers/chat_controller.py` docstring), not a hidden gap.
   `mail.thread.message_post()` still dispatches real `bus.bus` events
   server-side; only the React-side *consumption* of that channel is
   polling-based rather than a native websocket subscription.
3. **Text-to-speech uses the browser's Web Speech API**, not a server-side
   TTS provider - chosen deliberately over faking server audio generation;
   swapping in a real server-side TTS provider later is a contained change
   (see `sanad_ai/models/ai_assistant.py::request_tts` docstring).
4. **Admin user/role/org management** is not reimplemented as a parallel
   React CRUD - the Admin → Users page links directly to Odoo's native
   Settings → Users screen, which already does this safely.
5. **AI provider defaults to an offline mock** - no external AI provider is
   called until an administrator explicitly configures one with valid
   credentials in Settings → General Settings → SANAD AI.
6. **No automated CI pipeline** is included - test/build commands are
   documented above for manual or CI-integrated execution.
7. **No automated backup job** is configured - production deployments should
   add a scheduled `pg_dump` or equivalent.
#   s a n a d - p r o j e t - v - f i n a l  
 