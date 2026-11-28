# CRiB — Codex engineering handover
28 November 2026 | COMP-2002 Web Development | Assessment 2 recovery

## 1. Mission and constraints

Deliver an end-to-end working educational cloud resource integration web app as soon as possible. Target demonstration 1 December 2026 (project requirements §3.2; confirm the actual Canvas submission time and rubric with the student). The student's explicit instruction is to evolve the live Assessment 1 frontend, not replace it with a new design. No additional spending. The student is available to perform manual steps, authorize accounts, run local checks and configure a mini PC; give exact short instructions when human action is required. Do not stop at an implementation plan: implement, run, test, fix and document the core journey.

## 2. Repository and recovery state

Repository: https://github.com/CRiB-Cloud-Resource-Integration-Bridge/CRiB-Web-App
Live prototype: https://crib-cloud-resource-integration-bridge.github.io/CRiB-Web-App/
Main at handover: a928590af1d25a46f294be99c544915d7320a13f (27 October).
Backup: backup-main-2026-11-28 points to the exact same main snapshot. Leave both unchanged.
Development: development created from recovered backend commit f2bf301c9b44e849a2e24055bff9cdd9920540bd. Previous assessment-2-mvp branch was deleted; PR #2 closed unmerged. Do not recreate or reopen it without permission. The recovered commit remains an ancestor of development.
Historical CI: https://github.com/CRiB-Cloud-Resource-Integration-Bridge/CRiB-Web-App/actions/runs/46077197066 reported six passing tests before handover. This is not a fresh run or proof of real provider operation. Re-run them.
The original prototype is still in prototype/. Its Pages workflow deploys only that directory. Do not dispatch that workflow from development. New backend UI must be separate from the archived prototype.

At start run git status, git branch --show-current, git log -5 --oneline, git remote -v, git diff backup-main-2026-11-28 -- prototype/ (fetch refs if necessary). If local task uses a temporary branch, verify it descends from development. Never override another person's changes. Keep working commits reviewable. If cloud Codex creates a feature branch, target a PR to development, not main; human reviews and merges. No code changes to protected reference branches.

## 3. Authoritative sources and conflicts

Read these tracked files in full:
- docs/working-docs/01-requirements-foundation.md (scope, FR-01–15, NFR-01–13, decisions, acceptance criteria, risk and proposed data model).
- docs/working-docs/02-prototype-lifecycle-and-architecture.md (user journey, architecture, tradeoffs, traceability).
- README.md, docs/MVP-DECISION.md, app.py, database/schema.sql, services/providers/*.py, tests/*.py, templates/app.html, static/css/mvp.css.
- prototype/index.html, prototype/css/styles.css, prototype/css/prototype-v2.css, prototype/js/app.js — authoritative visual baseline, not a production security boundary.

External project materials (available to student in COMP-2002 project, not necessarily in clone): CRIB-Discord chat archive.pdf (pages 6–7 early Flask/SQLite and staged mock→Google roadmap; pages 23–26 November assignments, tech discussion and progress); 01-CRiB-requirements-foundation.pdf; 02-CRiB-Prototype -ifecycle-and-Architecture-Decisions.pdf; 03-CRiB-Screens–desktop.pdf (Penpot design reference); architecture and user journey diagrams; COMP-2002 Web Dev assignments.pdf; course modules. Do not upload raw Discord archive or private course materials into public GitHub. Request relevant rubric excerpts privately if needed.
The 4 November team discussion envisioned uploads and moves as well as downloads; the tracked formal requirements explicitly exclude transfers and prioritize read-only download. The user requested the live interactive prototype design, which takes precedence over alternate Penpot screenshots and the temporary simplified Flask UI. No claim that the entire team approved the recovered stack. Alin reported no progress on 17 November; Nikola reported security difficulties; the 23 November message mentions a mini PC and requests updates. This does not establish that no unpushed work exists. Preserve integration opportunities.

## 4. Existing implementation: do not restart

- Flask app factory create_app(config=None), Python 3.11+, SQLite schema, scrypt password hashes, database-backed session IDs, session expiry, login attempt throttling, CSRF, response security headers and user scoping.
- app.py routes: GET /, /health; GET/POST /signup, /signin; POST /logout; GET /dashboard, /providers; POST /providers/mock/connect, /providers/google/connect, /providers/disconnect; GET /oauth/google/callback, /files, /files/<file_id>, /files/<file_id>/download. Inspect code for exact field names and behavior. Forms currently use csrf. /files uses folder, q, kind.
- services/providers/mock.py: deterministic per-user sample resources, list/get/download; sample binary download is actual bytes, not simulation of clicking.
- services/providers/google_drive.py: optional read-only OAuth code, PKCE/state, encrypted tokens, refresh, revoke, bounded results/downloads. Live authorization not tested. Current schema permits one active provider (mock OR Google) per user. Do not imply simultaneous providers.
- Existing Flask frontend templates/app.html and static/css/mvp.css are functional but visually simplified: replace their appearance with prototype-derived markup/style while retaining server behavior.
- Current dependencies Flask, Waitress, requests, cryptography. Verify versions and vulnerability status without paid tools. Environment variables CRIB_SECRET_KEY, CRIB_DATABASE, CRIB_HTTPS, PORT, optional GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, CRIB_TOKEN_KEY. .env.example is not auto-loaded.
- Current limits: 500 Google resources per result set; 20 MB downloads; native Google Docs/Sheets/Slides exports unsupported; shared-drive coverage incomplete. No production guarantee.

## 5. Implementation milestones (in order)

### A. Reproduce baseline
Create isolated virtual environment, install requirements, run all tests, launch app with generated ephemeral secret and isolated database, verify /health. Record baseline and any errors. Inspect live prototype source and if browser available capture baseline screenshots (landing, auth, empty dashboard, provider selection, authorization, connected dashboard, files, folder, search, details, management, errors). Do not use real accounts yet.

### B. Integrate actual frontend
Keep prototype/ byte-for-byte unchanged. Reuse its HTML markup and both CSS files by copying/adapting into templates/ and static/ or creating a same-origin API if demonstrably simpler. Prefer Flask/Jinja templates and real server forms/links because existing routes and CSRF are already tested; preserve visual hierarchy, layout, branding, violet/lime palette, cards, tables, sidebar, dashboard and original design language. Vanilla JS for interactions where useful; no React rewrite or second design. Adapt fixed minimum widths to responsive layout without changing desktop appearance. Remove misleading fake credentials, fake counts, hardcoded files, unconditional success and placeholder actions. Dynamic content must be escaped (Jinja autoescape or textContent); never interpolate user/provider strings into unsafe innerHTML. Do not weaken CSP for inline scripts/styles; external assets and safe classes preferred.

Map each prototype view:
- renderLanding → /, genuine purpose, sign-in/sign-up buttons, clear demo vs real status.
- renderAuth → /signup and /signin, validated forms, visible errors, real logout.
- renderEmptyDashboard / renderDashboard → /dashboard based on authenticated connection; actual recent resources/count if available, otherwise honest unavailable/limited label.
- renderProviderSelection / renderAuthorize → /providers with explicit mock consent or real Google authorization redirect; cancel, deny, unavailable states; never ask for Google password.
- renderFiles / renderFolder → /files with dynamic resource rows, folder navigation, back/breadcrumb.
- renderSearchResults / renderNoResults → real q/kind filters and reset. Search semantics differ mock vs Google; explain.
- renderFileDetails → /files/<id>, provider metadata, permitted download only, back to correct folder.
- renderProviderManagement → connected status, confirmation, disconnect/reauthorize and updated dashboard.
- renderConnectionError / renderLoading → actionable error, waiting/loading when actual asynchronous request occurs; distinguish empty, permission-denied and expired connection. Disable planned functionality with truthful labels.

### C. Verify core mock journey end to end
Registration, duplicate/invalid inputs, bad login, session persistence, unauthenticated direct route denial, connect mock, dashboard, folder navigation, search/filter/reset, file metadata, actual download contents, restricted download rejection, disconnect and logout. Test User B cannot access User A's resources or connection. Test restart persistence; expired session; CSRF invalid/missing; keyboard navigation and 375px/desktop layout, accessible labels/focus and status. Browser tests with Playwright or equivalent if available; keep test DB disposable and no live secrets. Compare screenshots to prototype at desktop width, record differences and fix regressions. Add tests for route changes and escaping malicious filenames/user names. Avoid fabricated evidence.

### D. Google Drive live spike
Use read-only scope and dedicated test account; Google Cloud project, enable Drive API, External Testing consent screen, register test account, Web application OAuth client, exact local callback http://127.0.0.1:8000/oauth/google/callback. Student handles Google Console and secrets locally. Do not ask for raw secrets in chat or commit them. Generate Fernet key locally and store privately. Validate actual consent, state/callback, file/folder listing, search, allowed small file download, denied download, refresh/error and disconnect/reconnect. Review token handling, request limits/timeouts, replay prevention, logout/disconnect races and safe error messages. If blocked by configuration, document exactly what is missing and maintain runnable mock mode; no fabricated live success. The read-only scope is restricted; no unrestricted public release or sensitive accounts. Google-native exports and write permissions are not part of the baseline.

### E. Deployment after local green
Prepare reproducible no-cost local and mini-PC instructions (OS and network access not yet verified). Use Waitress behind HTTPS reverse proxy or other approved free solution; persistent SQLite data and environment secrets outside Git; permissions, backup/restore, health check, restart and safe logs. Do not expose Flask dev server or open ports blindly. For an assessor-accessible URL, choose a stable authorized HTTPS endpoint with the student; verify availability and OAuth redirect registration; GitHub Pages cannot host Flask. No purchase, no billing enablement without explicit approval. Avoid real personal data.

### F. Optional improvements only after core is verified
If time/rubric permits, discuss uploads and same-provider moves on dedicated test files and appropriate scoped authorization. Do not silently widen read-only scopes or enable destructive operations. OneDrive, Dropbox, simultaneous accounts, cross-provider moves, NAS, sync/backup, email verification, password reset and native previews remain later unless user changes scope. Prioritize a verified submission over feature sprawl.

## 6. Testing and delivery
Run python -m unittest discover -s tests -v after each milestone. Update .github/workflows/mvp-tests.yml push/PR filters to include development (currently assessment-2-mvp and main); keep original Pages workflow unchanged. Add browser test commands and CI where practical; do not claim tests ran unless logs prove it. Record manual checks as PASS/FAIL/NOT RUN and steps to reproduce. Ask two independent people to test core flow if possible (NFR-06); do not invent participants. Update README and docs/ARCHITECTURE.md with implemented stack, data model, provider contract, local run, configuration and limitations; add requirements traceability and evidence checklist. Maintain short progress log and list human blockers. Provide a roughly 150-word server-side technology note (Practice Assignment 7) for student review and verify actual Canvas requirements. Contribution Statement per assessment: report actual work and AI assistance, no invented percentages or consensus.

## 7. Definition of done and next response
A user can register, sign in, connect explicitly labeled demo storage (or verified Google Drive), browse/search/filter, view actual metadata, download permitted file bytes, disconnect, log out, and cannot access another user's data. UI unmistakably matches the live prototype; no fake data presented as live. Tests, browser evidence and reproducible setup supplied. Real Google and public deployment tracked separately if blocked. Final message should summarize files changed, tests run/results, known defects, exact next commands and any manual action. Work now through A–C autonomously in order; ask only for material blockers requiring user access. Stop before paid, external or irreversible actions.
