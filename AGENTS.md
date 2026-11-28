# CRiB agent instructions

Read docs/CODEX-HANDOVER.md and both docs/working-docs/ documents before implementation.

- Work on development or a feature branch based on development. Never modify main, backup-main-2026-11-28, prototype-requirements-foundation, or deploy GitHub Pages from development. Do not force-push, delete branches, merge PRs, or change repo settings.
- The existing live prototype is the authoritative visual baseline: prototype/index.html, prototype/css/styles.css, prototype/css/prototype-v2.css, prototype/js/app.js. Keep prototype/ unchanged. Reuse its actual markup, CSS, components and visual language in the working app; do not redesign it or introduce React.
- Reuse and review the recovered Flask/SQLite backend and provider adapters. Do not discard working code just to change frameworks.
- Zero additional spending. Do not purchase services, credits, API keys, domains or hosting. Ask before any external configuration, deployment or irreversible action.
- Keep secrets out of Git, logs, screenshots and browser JS. Use only synthetic credentials and dedicated Google test accounts. No public unrestricted OAuth launch.
- Implement and test in small coherent milestones. Run python -m unittest discover -s tests -v, add browser-level checks, fix regressions, report actual evidence and limitations. Preserve existing tests unless a justified change is necessary.
- Do not claim real OAuth, deployment, independent usability testing or assessment completion unless verified. Explain decisions and changes in plain language. Record AI assistance honestly.
