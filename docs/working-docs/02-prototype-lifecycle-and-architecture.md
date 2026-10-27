---
modified: 2026-10-26 20:59 PM
tags:
  - opit
linked_notes:
  - "[[OPIT]]"
  - "[[RECORDED-Web-development-1]]"
---
# CRiB Prototype Lifecycle and Architecture Decisions

## 1. Prototype baseline

The Assessment 1 prototype is a clickable **Penpot** prototype. Its purpose is to give the team and the reviewer a working, shareable visual representation of CRiB's features and form before application enters actual code development stages.

The prototype mirrors [[01-requirements-foundation]]:

- **Journey:** it follows the primary journey: landing page, register or sign in, connect Google Drive, browse, search and filter, view resource details, download, disconnect, and sign out.
- **Screens and states:** it covers the prototype screens listed in the requirements, including empty, loading, no-results, expired-connection, and error states.
- **Requirements:** every requirement whose phase includes "Prototype" is represented by at least one screen or interaction. Screens can carry requirement IDs as Penpot comments.
- **Scope:** it shows only what is inside the MVP boundary: download only, no in-app content preview, no transfers.

The prototype does not depend on any technology choice. It uses sample data and a simulated Google Drive connection.

![[CRiB-Assessment-1-user-journey-Excalidraw-export.png]]

**Deliverables:** a shareable Penpot link (view permissions checked in a private browser window) and a PDF export with documentation and architecture diagrams.

## 2. Architecture scope

The architecture describes CRiB's logical backbone: the parts the application needs and how they relate, independent of the languages and frameworks chosen later (Sections 3 and 4). The implementation is scaffolded from this backbone once the team selects a stack.

![[CRiB-Assessment-1-Excalidraw-export.png]]
### 2.1 Logical components

| Component                  | Responsibility                                                                                                                              |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Browser client             | Screens, navigation, forms, and states. Talks only to the backend API.                                                                      |
| Backend API                | Single entry point for all data and actions. Enforces authentication and user-scoped authorization.                                         |
| Authentication and sessions | Register, sign in and out, password hashing, sessions, and protected routes.                                                               |
| Core services              | Application rules: resource listing, search and filter, download eligibility, and connection management.                                    |
| Provider adapter           | One common contract for provider operations. A mock provider serves development and tests; a Google Drive adapter serves the demo.          |
| Database                   | One relational database for users, provider connections (with protected tokens), and an optional metadata cache.                          |
| External provider          | Google OAuth for authorization and the Google Drive API for resource data. CRiB never handles the provider password.                        |

```text
Browser client
      │  HTTPS
      ▼
Backend API ── Authentication and sessions
      │
      ▼
Core services ────────────── Database
      │
      ▼
Provider adapter
   ├── Mock provider (development, tests)
   └── Google Drive adapter ──► Google OAuth / Drive API
```

### 2.2 Expected outcomes

- One shared, editable architecture diagram showing these components, the mock provider, and Google Drive. The editable source lives in the repository, with a PNG or PDF export for the submission.
- Each component maps to requirements (Section 2.3), so the team can check that nothing is missing.
- The backbone stays the same whichever stack option is chosen; only the technologies that fill each component change.

### 2.3 Requirements-to-architecture traceability

This table maps the requirements in [[01-requirements-foundation]] to the logical components. Update it only when an approved requirement or architecture decision changes.

| Requirements                                                 | Architecture element                                  | Prototype evidence                                                                                  | Status  |
| ------------------------------------------------------------ | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ------- |
| FR-01, FR-04, FR-07 to FR-10, FR-14, FR-15; NFR-06 to NFR-08 | Browser client                                        | Penpot flow covering landing, dashboard, resource browser, search and filter, responsive and error states | Planned |
| FR-02, FR-03; NFR-01, NFR-02, NFR-04                         | Authentication and sessions, protected routes         | Register, sign-in, and sign-out screens; unauthorized-route and safe-error states                   | Planned |
| FR-05, FR-06, FR-12, FR-13; NFR-03, NFR-11                   | Provider adapter, Google OAuth boundary               | Provider selection, connection status, reauthorization, and disconnect states                       | Planned |
| FR-07 to FR-11; NFR-09, NFR-10                               | Core services and provider adapter                    | Sample resource list, folder navigation, search and filter, download, and provider-failure states   | Planned |
| FR-06, FR-13; NFR-02, NFR-05                                 | Database (data model proposal in requirements §8.1)   | User-scoped connections and documented stored fields                                                | Planned |
| NFR-12, NFR-13                                               | Repository, automated checks, hosting decision        | README and setup record, decision log, and hosting-cost evidence                                    | Planned |

## 3. Tech stack options

Two options are shortlisted for the working demo. Both use a **React + TypeScript** browser client and a **PostgreSQL** database; they differ in the backend runtime.

### 3.1 Option A: React/TypeScript + Node.js API + PostgreSQL

**Strengths:** one language (TypeScript) across the browser client and the backend, so API request and response types can be shared. Lightweight setup, a large ecosystem, and an official Google API client library for Node.js. React fits a component workflow that follows the Penpot prototype, and PostgreSQL suits a deployed multi-user application.

**Costs and risks:** the frontend and API are delivered separately, so authentication, sessions, provider OAuth, and environment settings all need deliberate design. JavaScript/TypeScript tooling (build configuration, asynchronous code) can be confusing for beginners. Node.js has fewer built-in conventions, so the team must agree on structure and choose security libraries carefully.

**Best fit:** the team is most comfortable with JavaScript/TypeScript and wants the shortest path to a working demo.

### 3.2 Option B: React/TypeScript + Java/Spring Boot + PostgreSQL

**Strengths:** a clear, conventional backend structure (controllers, services, repositories); mature security and OAuth support (Spring Security) and database access (Spring Data); strong typing; and an official Google API client library for Java. React remains a strong UI choice and PostgreSQL suits a deployed multi-user application.

**Costs and risks:** the highest initial setup and learning overhead for a beginner team. Learning Spring Security, OAuth, and React at the same time can absorb the schedule. The team works in two languages (Java and TypeScript).

**Best fit:** at least one team member has credible Java/Spring experience and can own the backend.

## 4. Architecture decisions and stack evaluation

### 4.1 Architecture baseline

These choices should be approved as a team before implementation starts. "Approved" means the decision is part of the baseline and changes only through a recorded team decision.

| Decision               | Proposed position                                                                                                  | Status                    | Owner                | Evidence / decision record |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------- | -------------------- | -------------------------- |
| Client boundary        | Browser-based web client                                                                                           | Approved                  | Team                 | Team communication channel |
| Frontend framework     | React + TypeScript (common to both stack options)                                                                  | Pending team approval     | Frontend             |                            |
| Backend boundary       | One backend/API runtime only: Node.js or Spring Boot, never both                                                   | Pending team approval     | Nikola               |                            |
| Data boundary          | One relational database: PostgreSQL                                                                                | Pending team approval     | Nikola, Daniil, Alin |                            |
| Provider abstraction   | Provider adapter isolates provider-specific behaviour                                                              | Pending team approval     | Nikola               |                            |
| Provider authorization | OAuth or provider-supported authorization; never collect provider passwords                                        | Pending team approval     | Nikola               |                            |
| User authorization     | Every protected operation is user-scoped                                                                           | Pending team approval     | Nikola, Alin         |                            |
| Storage boundary       | Download only: no file synchronization, CRiB bulk storage, in-app content preview, or local-device transfer in the MVP | Pending team approval  | Nikola               |                            |
| Repository strategy    | One monorepo containing application code, tests, documentation, automation, and deployment assets                  | Pending team approval     | Nikola, Alin, Daniil |                            |
| Prototype              | Clickable Penpot prototype                                                                                         | Accepted for Assessment 1 | Daniil, Anika        | Team communication channel |

### 4.2 Stack evaluation

The two options in Section 3 are evaluated against the team's skills, the deadline, and the MVP scope (Google Drive authorization, resource listing, and download). The evaluation is deliberately informal:

1. **Skills check and Spike:** a skillset team discussion and a short, time-boxed test (2–3 days) in the leading option, or in both if at least two people are available. It should prove a Google sign-in callback, storing the connection for the signed-in user, one resource-list request, and an expired-connection or error state.
2. **Decision:** the team discusses the results, chooses one option.

Prefer the option the team can explain, test, and deploy as soon as possible. A small, coherent integration beats a partially assembled multi-framework solution.

**Rough lifecycle estimate** (for planning, not a commitment), about five weeks from 28 October to 1 December:

| Week | Dates                       | Focus                                                                  |
| ---- | --------------------------- | ---------------------------------------------------------------------- |
| 1    | Post Assessment 1           | Skills check, spike, stack decision, repository skeleton               |
| 2    | Post Assessment 1 + 1 weeks | Authentication, user-scoped access, database                           |
| 3    | Post Assessment 1 + 2 weeks | Provider adapter (mock, then Google Drive), dashboard, resource list   |
| 4    | Post Assessment 1 + 2 weeks | Folder navigation, search and filter, download, error states           |
| 5    | Post Assessment 1 + 3 weeks | Testing, accessibility and responsive pass, deployment, demo rehearsal |

## 5. Prototype-to-demo lifecycle

```text
Requirements baseline
        ↓
Penpot user-flow prototype + Excalidraw architecture
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

- [x] Confirm the MVP boundary in `01-requirements-foundation.md`.
- [ ] Complete the primary Penpot flow and all key exceptional states listed in the requirements.
- [x] Decide and record one shared, editable architecture-diagram tool. Excalidraw is recommended, but the team may select any free, low-friction alternative.
- [ ] Produce the shared architecture diagram. It must label: browser client, backend API, authentication, provider adapter, database, mock provider, and Google Drive.
- [ ] Store the editable diagram source and export a stable PNG or PDF snapshot for the submission package.
- [ ] Update the Markdown documentation and/or export a PDF with screen annotations and publish the Penpot URL with tested permissions.
- [ ] Recommended if the team is ready to use GitHub Issues: create issues using requirement IDs and give each team member a visible ownership area.

### B. Risk retirement and architecture decision - immediately after the prototype milestone

**Outcome:** one evidence-backed implementation choice.

- [ ] Create Google Drive test/developer credentials and test accounts without using personal content (provider chosen: Google Drive).
- [ ] Run the time-boxed OAuth/resource-list spike.
- [ ] Evaluate the two stack options as described in Section 4.2.
- [ ] Update the architecture diagram to reflect the selected stack.
- [ ] Define the shared resource contract and provider adapter interface before building screen-specific code.

### C. Core demo build - toward 1 December

**Build order:**

1. Repository foundations: README, local setup steps, environment-variable template, branch/PR workflow, and test-data policy.
2. Authentication and user-scoped authorization.
3. Provider adapter plus mock data; then Google Drive.
4. Dashboard, resource list, folders, search/filter, and provider states.
5. Controlled download where the provider permits it.
6. Error, security, responsive, accessibility, and usability passes.
7. Public deployment, demonstration data, final test evidence, and team rehearsal.

**Definition of demo-ready:** a fresh user can sign in, connect Google Drive or use the documented test provider, browse resources, search/filter, download an eligible resource, encounter an understandable error state, and complete the journey in the publicly available deployment. The team can map each behaviour to a requirement ID and explain limitations honestly.

## 6. Proposed monorepo structure

This is a proposed, stack-neutral starting structure that works for either option in Section 3. Create folders only when they are needed.

```dirtree
- /CRiB-Web-App
	- /frontend                      # React + TypeScript browser client
		- /src
			- /pages                 # Landing, auth, dashboard, resource browser
			- /components            # Reusable UI parts based on the Penpot prototype
			- /services              # Calls to the backend API
		- /tests
	- /backend                       # Node.js or Spring Boot API (one only)
		- /src
			- /routes                # HTTP endpoints (controllers in Spring Boot)
			- /auth                  # Sign-in, sessions, protected-route checks
			- /services              # Application rules and use cases
			- /providers             # Provider-adapter boundary
				- base.*             # Common ProviderAdapter contract
				- mock_provider.*    # Sample data for development and tests
				- google_drive.*     # Google Drive adapter
			- /repositories          # Database access only
			- /models                # User, connection, and resource models
			- config.*               # Environment-based settings; no secrets
		- /tests
			- /unit                  # Services and adapter transformations
			- /integration           # API, database, and user-ownership tests
	- /tests
		- /acceptance                # Primary user-journey evidence
	- /docs
		- /working-docs
			- 01-requirements-foundation.md
			- 02-prototype-lifecycle-and-architecture.md
		- /decisions
		- /prototype
			- penpot-link.md
			- prototype-export.pdf
			- architecture.excalidraw
		- /testing
			- acceptance-scenarios.md
	- /ci-cd                         # Deployment/config templates; no credentials
	- .env.example                   # Variable names only; no real values
	- README.md
```

## 7. Near future team agenda

1. Confirm the Penpot prototype and architecture diagram exports for the 27 October milestone.
2. Approve or amend the architecture baseline (Section 4.1) and confirm owners.
3. Run the skills check, nominate the spike owner, and set the spike deadline. Register Google Drive test accounts at the same time.
4. Choose the stack option (Section 4.2).
5. Create the monorepo skeleton (Section 6) for the chosen stack, with only the folders needed to start.
