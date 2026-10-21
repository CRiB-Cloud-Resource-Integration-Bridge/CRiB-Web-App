---
modified: 2026-10-20 17:32 PM
tags:
  - opit
linked_notes:
  - "[[OPIT]]"
  - "[[RECORDED-Web-development-1]]"
---
# CRiB Prototype Lifecycle and Architecture Options

## 1. Recommended working approach

Treat the existing ==🟣**Flask + SQLite + mock provider**== diagram(s) as a deliberately narrow prototype/build baseline, not as a promise of the final production stack. It is aligned with the most important uncertainty: can CRiB present a user-scoped, provider-shaped resource browser through a clean adapter boundary?


==🔴Decision==
Do not combine Flask, Spring Boot, and Node.js as three backend layers. For the later working demo, choose one backend runtime after a short technical spike. React/TypeScript is a frontend choice and can pair with either a Java/Spring Boot or Node.js backend; it can also be deferred while the team validates the provider flow with Flask-rendered pages.

## 2. What the supplied architecture accomplished so far

==Compare with the agreed  [[01-requirements-foundation]] and define a fixed option to map that==
The diagram shows these useful boundaries:

- A browser-facing web application with routes/views, authentication/session handling, core services, static assets, and database access.
- A **provider layer** that isolates the rest of the application from provider-specific APIs.
- A low-risk **mock provider** and seeded file data for the backbone stage.
- A later Google OAuth/Google Drive API path rather than asking for a user's provider password.
- A clear user path: login -> dashboard -> provider selection -> file browser -> folder navigation.

The requirements baseline extends the shown flow with explicit empty, loading, authorization-failure, expired-connection, search/filter, download/access, and disconnect states. These are essential prototype screens, not necessarily extra features.

## 3. Stack options compared

| Option                                                           | Strengths for CRiB                                                                                                                                            | Costs and risks                                                                                                                                                           | Best use                                                                                                                           |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Flask/Python + SQLite + server-rendered HTML + mock provider** | Smallest working surface; directly matches the supplied diagram; ideal for validating user flow, provider adapter, and seeded test data.                      | Less natural if the team wants a richer single-page UI; SQLite is not the preferred shared production database; moving later can create rework.                           | Early backbone and a credible fallback demo if time/skills are tight.                                                              |
| **React/TypeScript + Node.js API + PostgreSQL**                  | One language across client and server; strong component ecosystem; React supports a Figma-to-component workflow; PostgreSQL suits shared deployed data.       | Requires separate frontend/API delivery, auth/session design, provider OAuth integration, and environment management; do not underestimate JavaScript/TypeScript tooling. | Good candidate if the team is most comfortable with TypeScript and can establish a clean API boundary early.                       |
| **React/TypeScript + Java/Spring Boot + PostgreSQL**             | Clear enterprise-style API structure; mature security/data ecosystem; React remains a strong UI choice; PostgreSQL is suitable for a deployed multi-user app. | ==Highest initial setup/learning overhead for a beginner team; using Spring Security, OAuth, and React simultaneously can absorb the schedule.==                          | Good candidate if the team already has credible Java/Spring ownership and uses the prototype phase to prove the risky integration. |
| **Flask/Python + PostgreSQL, with React optional**               | Preserves the team's existing architecture and Python progress while replacing SQLite only when a shared hosted database is needed.                           | ==Still needs a deliberate frontend choice and deployment/security work; avoids the false comfort of a fully different "production" plan.==                               | Pragmatic transition if Flask is already moving and the team wants to reduce stack churn.                                          |

## 4. Recommendation without locking the stack

==🟢Can this be turned into a decision table to evaluate options?==
1. **Lock the architectural invariants now, not the framework:** 
   - browser client; 
   - one backend/API; 
   - one relational database; 
   - provider adapter; 
   - OAuth/provider-supported authorization; 
   - user-scoped authorization; 
   - no provider-password collection; 
   - ==no file synchronization or CRiB bulk storage.==
1. ==🔴Decision==
   ==Define this as tech stack w/o putting a finger on the solution==
   ==**Use the supplied Flask/SQLite/mock-provider structure for the prototype/backbone** if it already represents team work. It is not an inferior option for Assessment 1; it makes the user journey demonstrable early.==
2. **Run one time-boxed spike before committing the Assessment 2 stack.** The same test must be attempted in the team-preferred candidate: provider authorization callback, secure user association, one resource-list request, and an error/expired-connection state. Record effort, blockers, deployment fit, and ownership.
3. **Choose exactly one of these demo paths after the spike:**
   - Continue Flask and move SQLite to PostgreSQL only if deployment/shared-data needs justify it; or
   - Build React/TypeScript with one API backend: **either** Node.js **or** Spring Boot, plus PostgreSQL.
5. Prefer the option the team can explain, test, and deploy by 1 December. A coherent small working integration will assess better than a partially assembled multi-framework architecture.

### Decision criteria

Score each candidate 1-5 after the spike, with evidence rather than preference:

| Item                 | Question                                                                                    | Spike owner | Score |
| -------------------- | ------------------------------------------------------------------------------------------- | ----------- | ----- |
| Provider integration | Did the OAuth callback and one resource listing work safely with test data?                 |             |       |
| Team ownership       | Does every key layer have a named contributor who can explain and maintain it?              |             |       |
| Delivery speed       | Can authentication, browsing, testing, and deployment be completed by 1 December?           |             |       |
| Security fit         | Is user scoping, secrets management, and safe token handling clear and testable?            |             |       |
| Deployment fit       | Can it be publicly hosted at acceptable cost with a suitable database?                      |             |       |
| Maintainability      | Are provider code and UI/API contracts separated enough to support a second provider later? |             |       |

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
- [ ] ==🔴Decision: Choose Excalidraw or another tool or abandon== Update Excalidraw so its labels match the agreed terms: browser, backend/API, provider adapter, database, mock provider, and future real provider.
- [ ] Update the Markdown documentation and/or export a PDF with screen annotations and publish the Figma URL with tested permissions.
- ==🟡Suggestion!==
	- Open GitHub issues using requirement IDs and give each team member a visible ownership area.

### B. Risk retirement and architecture decision - immediately after the prototype milestone

**Outcome:** one evidence-backed implementation choice.

- [ ] Choose one provider and create test/developer credentials without using personal production content.
- [ ] Run the time-boxed OAuth/resource-list spike.
- [ ] Evaluate the backend/database candidates with the decision criteria above.
- [ ] Record the decision, rejected alternatives, and the smallest next architecture diagram.
- [ ] Define the shared resource contract and provider adapter interface before building screen-specific code.

### C. Core demo build - toward 1 December

**Build order:**

1. Repository foundations: README, local setup, etc.
2. Authentication and user-scoped authorization.
3. Provider adapter plus mock data; then the selected real provider.
4. Dashboard, resource list, folders, search/filter, and provider states.
5. Controlled download/access where permitted.
6. Error, security, responsive, accessibility, and usability passes.
7. Public deployment, demonstration data, final test evidence, and team rehearsal.

**Definition of demo-ready:** a fresh user can sign in, connect or use the documented test provider, browse resources, search/filter, access an eligible resource, encounter an understandable error state, and complete the journey in the publicly available deployment. The team can map each behaviour to a requirement ID and explain limitations honestly.

## 6. Suggested repository documentation layout

```dirtree
- /docs/
  - working-docs/
    - 01-requirements-foundation.md
    - 02-prototype-lifecycle-and-architecture.md
  - decisions/
    - ADR-001-first-provider.md
    - ADR-002-demo-stack.md
    - ADR-003-hosting-and-cost.md
  - prototype/
    - figma-link.md
    - prototype-export.pdf
    - architecture.excalidraw
  - testing/
    - acceptance-scenarios.md
- README.md
```

## 7. Near future team agenda

1. Review the scope-reconciliation table and explicitly approve the out-of-scope items.
2. Nominate the first-provider owner and set a short technical-spike deadline.
3. Create prototype screens by requirement IDs, including failure and empty states.
4. Decide on the UI option.
5. Create the three decision records above before any irreversible stack investment.

