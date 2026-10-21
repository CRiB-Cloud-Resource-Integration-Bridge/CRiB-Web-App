---
modified: 2026-10-20 19:49 PM
tags:
  - opit
linked_notes:
  - "[[OPIT]]"
  - "[[RECORDED-Web-development-1]]"
---
# CRiB Prototype Lifecycle and Architecture Decisions

## 1. Accepted prototype baseline

For **Assessment 1**, CRiB adopts the existing **Flask/Python, SQLite, server-rendered UI, and mock-provider** design as its accepted prototype baseline. It is deliberately narrow and proves the most important early assumption: CRiB can present a user-scoped, provider-shaped resource browser through a clean adapter boundary.

This acceptance applies to the prototype/backbone. It does not by itself commit Assessment 2 to a final deployed stack. The team will use the feasibility spike in Section 5B to decide whether to continue and evolve this baseline, or use one alternative backend/API path.

**Architecture rule:** CRiB shall use one backend/API runtime. Flask, Spring Boot, and Node.js must not be combined as three backend layers. React/TypeScript is a frontend option that can pair with either Node.js or Spring Boot; it may also be deferred while the prototype baseline is validated.

## 2. What the supplied architecture accomplished so far

The diagram shows these useful boundaries:

- A browser-facing web application with routes/views, authentication/session handling, core services, static assets, and database access.
- A **provider layer** that isolates the rest of the application from provider-specific APIs.
- A low-risk **mock provider** and seeded file data for the backbone stage.
- A later Google OAuth/Google Drive API path rather than asking for a user's provider password.
- A clear user path: login -> dashboard -> provider selection -> file browser -> folder navigation.

The requirements baseline extends the shown flow with explicit empty, loading, authorization-failure, expired-connection, search/filter, download/access, and disconnect states. These are essential prototype screens, not necessarily extra features.

### Requirements-to-architecture traceability

The architecture must remain aligned with [[01-requirements-foundation]]. This table provides the fixed mapping for the accepted prototype baseline; it should be updated only when an approved requirement or architecture decision changes.

| Requirements | Architecture element | Prototype evidence | Status |
| --- | --- | --- | --- |
| FR-01, FR-04, FR-07 to FR-10, FR-14; NFR-06 to NFR-08 | Browser UI, routes/views, templates, static assets | Figma flow covering landing, dashboard, resource browser, responsive and error states | Planned |
| FR-02, FR-03; NFR-01, NFR-02, NFR-04 | Authentication/session layer and protected routes | Sign-in/sign-out screens; unauthorized-route and safe-error states | Planned |
| FR-05, FR-06, FR-12, FR-13; NFR-03, NFR-11 | Provider layer, provider connection data, OAuth/authorization boundary | Provider-selection, connection status, reauthorization, and disconnect states | Planned |
| FR-07 to FR-11; NFR-09, NFR-10 | Core services and provider adapter | Mock resource list, folder navigation, search/filter, access/download and provider-failure states | Planned |
| FR-06, FR-13; NFR-05 | SQLite database access and data model | User-scoped mock connections and documented retained metadata | Planned |
| NFR-12, NFR-13 | Repository, automated checks, hosting decision | README/setup record, decision record, and hosting-cost evidence | Planned |

## 3. Stack options compared

| Option                                                           | Strengths for CRiB                                                                                                                                            | Costs and risks                                                                                                                                                           | Best use                                                                                                                           |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Flask/Python + SQLite + server-rendered HTML + mock provider** | Smallest working surface; directly matches the supplied diagram; ideal for validating user flow, provider adapter, and seeded test data.                      | Less natural if the team wants a richer single-page UI; SQLite is not the preferred shared production database; moving later can create rework.                           | Early backbone and a credible fallback demo if time/skills are tight.                                                              |
| **React/TypeScript + Node.js API + PostgreSQL**                  | One language across client and server; strong component ecosystem; React supports a Figma-to-component workflow; PostgreSQL suits shared deployed data.       | Requires separate frontend/API delivery, auth/session design, provider OAuth integration, and environment management; do not underestimate JavaScript/TypeScript tooling. | Good candidate if the team is most comfortable with TypeScript and can establish a clean API boundary early.                       |
| **React/TypeScript + Java/Spring Boot + PostgreSQL**             | Clear enterprise-style API structure; mature security/data ecosystem; React remains a strong UI choice; PostgreSQL is suitable for a deployed multi-user app. | ==Highest initial setup/learning overhead for a beginner team; using Spring Security, OAuth, and React simultaneously can absorb the schedule.==                          | Good candidate if the team already has credible Java/Spring ownership and uses the prototype phase to prove the risky integration. |
| **Flask/Python + PostgreSQL, with React optional**               | Preserves the team's existing architecture and Python progress while replacing SQLite only when a shared hosted database is needed.                           | ==Still needs a deliberate frontend choice and deployment/security work; avoids the false comfort of a fully different "production" plan.==                               | Pragmatic transition if Flask is already moving and the team wants to reduce stack churn.                                          |

## 4. Architecture decisions and option evaluation

### 4.1 Architecture invariants

These choices should be approved as a team before implementation proceeds. “Approved” means the decision is accepted for the Assessment 1 prototype and will not change without a recorded team decision.

| Decision | Proposed position | Status | Owner | Evidence / decision record |
| --- | --- | --- | --- | --- |
| Client boundary | Browser-based web client | Pending team approval |  |  |
| Backend boundary | One backend/API runtime only | Pending team approval |  |  |
| Data boundary | One relational database; SQLite for the accepted prototype baseline | Pending team approval |  |  |
| Provider abstraction | Provider adapter isolates provider-specific behaviour | Pending team approval |  |  |
| Provider authorization | OAuth or provider-supported authorization; never collect provider passwords | Pending team approval |  |  |
| User authorization | Every protected operation is user-scoped | Pending team approval |  |  |
| Storage boundary | No file synchronization, CRiB bulk storage, or local-device transfer in the MVP | Pending team approval |  |  |
| Repository strategy | One monorepo containing application code, tests, documentation, automation, and deployment assets | Accepted |  |  |
| Prototype baseline | Flask/Python, SQLite, server-rendered UI, mock provider | Accepted for Assessment 1 |  |  |

### 4.2 Assessment 2 stack decision gate

The team shall run one time-boxed feasibility spike before committing the working-demo stack. Each candidate must demonstrate the same minimum test: a provider authorization callback, secure association with the user, one resource-list request, and an expired-connection or provider-error state.

After the spike, the team must select exactly one demo path:

- Continue the Flask baseline, moving from SQLite to PostgreSQL only if deployment or shared-data needs justify it; or
- Use React/TypeScript with **one** API backend: Node.js **or** Spring Boot, plus PostgreSQL.

Prefer the option the team can explain, test, and deploy by 1 December. A coherent, small integration is preferable to a partially assembled multi-framework solution.

### 4.3 Candidate evaluation record

Score each candidate 1-5 after the spike, with evidence rather than preference. A score without linked evidence is incomplete.

| Candidate                                   | Provider integration | Ownership | Security fit | Deployment fit | Evidence / decision link | Decision |
| ------------------------------------------- | -------------------- | --------- | ------------ | -------------- | ------------------------ | -------- |
| Flask/Python + PostgreSQL                   |                      |           |              |                |                          |          |
| React/TypeScript + Node.js + PostgreSQL     |                      |           |              |                |                          |          |
| React/TypeScript + Spring Boot + PostgreSQL |                      |           |              |                |                          |          |

## 5. Prototype-to-demo lifecycle

```text
Requirements baseline
        ↓
Figma user-flow prototype + Excalidraw architecture
        ↓
Provider/stack feasibility spike
        ↓
Commit one demo architecture and backlog
        ↓
Incremental implementation and automated checks
        ↓
Usability, security, and acceptance tests
        ↓
Public deployment and demo rehearsal
```

### A. Requirements and design - prototype milestone (27 October)

**Outcome:** a traceable, reviewable design package, not an unfinished build.

- [ ] Confirm the MVP boundary in `01-requirements-foundation.md`.
- [ ] Complete the primary Figma flow and all key exceptional states listed in the requirements.
- [ ] Decide and record one shared, editable architecture-diagram tool. Excalidraw is recommended, but the team may select any free, low-friction alternative.
- [ ] Produce the shared architecture diagram. It must label: browser, backend/API, provider adapter, database, mock provider, and future real provider.
- [ ] Store the editable diagram source and export a stable PNG or PDF snapshot for the submission package.
- [ ] Update the Markdown documentation and/or export a PDF with screen annotations and publish the Figma URL with tested permissions.
- [ ] Recommended if the team is ready to use GitHub Issues: create issues using requirement IDs and give each team member a visible ownership area.

### B. Risk retirement and architecture decision - immediately after the prototype milestone

**Outcome:** one evidence-backed implementation choice.

- [ ] Choose one provider and create test/developer credentials without using personal production content.
- [ ] Run the time-boxed OAuth/resource-list spike.
- [ ] Evaluate the backend/database candidates with the decision criteria above.
- [ ] Record the selected path, rejected alternatives, evidence, owner, date, and consequences in `ADR-002-demo-stack.md`.
- [ ] Update the architecture diagram to reflect the selected demo path.
- [ ] Define the shared resource contract and provider adapter interface before building screen-specific code.

### C. Core demo build - toward 1 December

**Build order:**

1. Repository foundations: README, local setup steps, environment-variable template, branch/PR workflow, and test-data policy.
2. Authentication and user-scoped authorization.
3. Provider adapter plus mock data; then the selected real provider.
4. Dashboard, resource list, folders, search/filter, and provider states.
5. Controlled download/access where permitted.
6. Error, security, responsive, accessibility, and usability passes.
7. Public deployment, demonstration data, final test evidence, and team rehearsal.

**Definition of demo-ready:** a fresh user can sign in, connect or use the documented test provider, browse resources, search/filter, access an eligible resource, encounter an understandable error state, and complete the journey in the publicly available deployment. The team can map each behaviour to a requirement ID and explain limitations honestly.

## 6. Proposed monorepo structure

This is a proposed starting structure for the accepted Flask prototype baseline. It makes the browser/API boundary, application services, provider adapter, database access, tests, and project evidence visible without forcing the team to create empty folders before they are needed.

```dirtree
- /CRiB-Web-App
	- /app                           # Browser routes, templates, and static assets
		- /routes
			- auth.*
			- dashboard.*
			- /tests
			- /ui
		- /services                  # Application use cases and business rules
			- resource_service.*
			- connection_service.*
	- /api                           # JSON endpoints when a browser/client needs them
		- resources.*
		- provider_connections.*
	- /providers                     # Provider-adapter boundary
		-  base.*                    # Common ProviderAdapter contract
		-  mock_provider.*           # Assessment 1 seeded/test-data adapter
		-  google_drive.*            # Add only if Google Drive is selected
	- /repositories                  # Database access only
		- users.*
		- provider_connections.*
	- /models                        # User, connection, and normalized resource models
	- config.*                       # Environment-based configuration; no secrets
	- /tests
	- /unit                          # Services and provider-adapter transformations
	- /integration                   # API/database/user-ownership tests
	- /acceptance                    # Primary user-journey evidence
	- /docs
		- /working-docs
			- 01-requirements-foundation.md
			- 02-prototype-lifecycle-and-architecture.md
		- /decisions
			- ADR-001-first-provider.md
			- ADR-002-demo-stack.md
			- ADR-003-hosting-and-cost.md
		- /prototype
			- figma-link.md
			- prototype-export.pdf
			- architecture.excalidraw
		- /testing
			- acceptance-scenarios.md
	- /ci-cd                         # Deployment/config templates; no credentials
	- README.md
```

### Boundary rules

- **Web** renders browser pages and receives browser actions. **API** exposes data/actions to an interactive client. A Flask prototype may use only `web/` initially; retain `api/` only when JSON endpoints are needed.
- **Services** contain application rules. Route/API files should delegate to them rather than access the database or provider directly.
- **Providers** define one common adapter contract and concrete implementations. Core browsing logic calls the contract, never a provider-specific SDK directly.
- **Repositories** own database queries and persistence. They do not contain HTTP, provider, or UI logic.
- **Models** represent concepts shared within the application, such as user, provider connection, and normalized resource metadata.
- **Tests** mirror the risk areas: unit tests for transformations/rules, integration tests for user ownership and persistence, and acceptance tests for the assessed journey.

If the team later selects React, add a `frontend/` directory at the repository root and keep the backend implementation in `app/` or rename it to `backend/`. Do not create that directory until the Assessment 2 stack decision is made.

## 7. Near future team agenda

1. Review the scope-reconciliation table and explicitly approve the out-of-scope items.
2. Nominate the first-provider owner and set a short technical-spike deadline.
3. Create prototype screens by requirement IDs, including failure and empty states.
4. Approve or amend the architecture-invariants table and assign owners.
5. Decide on the shared diagram tool and create the editable first diagram.
6. Review the proposed "monorepo" structure and create only the folders needed for the prototype baseline.
7. Create the three decision records above before any irreversible stack investment.

