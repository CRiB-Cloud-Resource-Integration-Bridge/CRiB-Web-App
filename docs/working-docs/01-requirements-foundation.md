---
modified: 2026-10-20 15:55 PM
tags:
  - opit
linked_notes:
  - "[[OPIT]]"
  - "[[RECORDED-Web-development-1]]"
---
# CRiB Requirements Foundation

## 1. Purpose and status

**CRiB (Cloud Resource Integration Bridge)** is a proposed web application that gives an authenticated user one place to connect a supported cloud-storage account, browse its resources, and perform controlled access to an eligible file.

This is the requirements baseline. It is deliberately lightweight: it supports a credible Figma prototype, an architecture diagram, and a build-ready backlog without pretending that every later implementation choice has already been made.

**Status:** working baseline for team review. Requirements marked `Proposed` need confirmation before becoming a build commitment.

## 2. Assessment alignment

| Assessment need                        | Type      | Format                           | Evidence to prepare in the prototype phase                                                                                                |
| -------------------------------------- | --------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Detailed project prototype             | Mandatory | Any type                         | Descriptive flow for the primary user journey, with desktop and responsive states where practical. Suggested a clickable Figma prototype. |
| Documentation with images and comments | Preferred | Markdown                         | Exported prototype PDF that captions key screens and notes known limitations/decisions.                                                   |
| Interactive prototype URL              | Optional  | URL                              | Shareable Figma prototype link or GitHub Pages, with view permissions checked in an incognito/private browser.                            |
| Clear, simple documentation            | Mandatory | Markdown and/or diagrams, images | This requirements baseline, architecture diagram, decision log, and a short implementation plan in the repository.                        |

## 3. Product scope

### 3.1 Problem statement

People may keep files across separate cloud-storage services. Switching between provider interfaces makes it harder to locate, understand and use their resources. CRiB will demonstrate a secure aggregation layer: users authorize CRiB to access a supported provider and then browse a normalized view of the permitted resources.

### 3.2 Prototype and MVP boundary

The prototype must show the intended end-to-end experience. It does **not** need to be a production implementation or prove every integration.

The later MVP (target demo: **1 December**) should prove one real provider integration or, if that risk cannot be retired in time, explicitly demonstrate a mock-provider implementation with a documented provider adapter and test data. A real-provider OAuth spike should happen early enough to avoid making the fallback a late surprise.

### 3.3 In scope for the core MVP

- Account registration, login, logout, and user-scoped access.
- One supported cloud-storage provider.
- Provider connection status and an authorization/connection flow.
- File and folder listing, folder navigation, common metadata, search, and basic filtering.
- Clearly attributable provider source for each resource.
- Controlled access or download of a selected resource when permitted by the provider.
- Responsive, accessible core UI; useful errors and empty states.
- A public deployment, appropriate test coverage, and concise project documentation.

### 3.4 Explicitly out of scope for the core MVP

- Full or scheduled synchronization, backup, mirroring, or offline caching.
- Copying all provider files into CRiB-managed storage.
- A local-device/USB/NAS agent, remote local-filesystem control, or physical-device transfer.
- Multiple providers before the first provider works end to end.
- File sharing, ==duplicate detection==, ==analytics beyond a small summary==, and advanced previews.
- ==MFA, social login, email verification, and password recovery unless the team selects and validates them without displacing core delivery.==

## 4. Scope reconciliation and decisions to make

| Topic                              | Reconciled position                                                                                                                                                                         | Decision status / question                                           | Owner |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ----- |
| Aggregation versus synchronization | ==Aggregate metadata and enable controlled provider-backed access==. Synchronization is a future extension.                                                                                 | Confirmed direction.                                                 |       |
| Provider count                     | Design a provider adapter boundary; implement **one** provider first.                                                                                                                       | Select Google Drive, OneDrive, or Dropbox after a feasibility spike. |       |
| Real API versus mock provider      | A mock provider is valid for early UX and integration work. The target demo should use a real provider if the spike succeeds; otherwise state the limitation and show the adapter contract. | Proposed fallback decision gate.                                     |       |
| Download versus transfer           | ==A user may access/download an eligible resource through the provider. Transfer to local devices is excluded.==                                                                            | Confirmed MVP boundary?                                              |       |
| Prototype versus demo              | Assessment 1 validates the designed experience; Assessment 2 validates the working MVP.                                                                                                     | Confirmed timeline boundary.                                         |       |
| Authentication breadth             | ==Use one conventional account-authentication path. ==Do not combine password, social login, MFA, email verification, and recovery in the first build.                                      | Team chooses the minimum viable method.                              |       |
| Deployment                         | The target demo should be Internet-accessible, using free/low-cost services and test data.                                                                                                  | Hosting selection pending.                                           |       |

## 5. Actors and primary journeys

### Primary actor

**Registered user:** a person with a CRiB account who may authorize one cloud-storage account from the selected supported providers. Future versions may support additional providers and additional accounts.

### Primary journey

1. The user learns what CRiB does on the landing page.
2. The user registers or signs in.
3. The user opens an initially empty dashboard and chooses a provider to connect.
4. The user authorizes the selected provider and returns to CRiB dashboard.
5. The user sees connection status and browses folders/resources.
6. The user searches or filters the resource list.
7. The user opens an eligible resource or initiates an allowed download.
8. The user can disconnect the provider and sign out. ==Question: Account deletion process fits where?==

### Prototype screens

- Landing page
- Sign up / sign in / sign out state
- Empty dashboard with provider connection call to action
- Provider-selection and OAuth hand-off/return states
- Connected dashboard with resource list and provider badge
- Folder navigation and resource detail/action state
- Search, filter, no-results, loading, expired-connection, and error states
- Account and connected-provider management

## 6. Functional requirements

Priority uses MoSCoW: **Must**, **Should**, **Could**, **Won't (this release)**. “Prototype” means the interaction must be represented in Figma; “Demo” means it must be working for the 1 December MVP unless noted.

| ID    | Requirement                                                                                                                           | Module            | Priority | Phase                                               | Acceptance criteria                                                                                                                                 |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | -------- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-01 | The system shall present a public landing page explaining CRiB's purpose and the supported-provider concept.                          | Core              | Must     | Prototype, Demo                                     | A first-time visitor can identify the product purpose, main action, and privacy/security expectation without authentication.                        |
| FR-02 | The system shall let a new user register and an existing user sign in and sign out using the selected authentication method.          | Auth              | Must     | Prototype, Demo                                     | Valid credentials create an authenticated session; invalid credentials show a safe, understandable error; sign-out ends access to protected routes. |
| FR-03 | The system shall prevent an unauthenticated user from viewing dashboard, provider, or resource data.                                  | Auth              | Must     | Prototype, Demo                                     | Direct navigation to a protected route redirects to sign-in or returns an authorized error response.                                                |
| FR-04 | The system shall show an authenticated user a dashboard with connected-provider status and a clear way to connect the first provider. | Core/Auth         | Must     | Prototype, Demo                                     | A user with no connection sees an empty state and connect action; a connected user sees provider name and status.                                   |
| FR-05 | The system shall let a user start authorization for one selected cloud-storage provider using the provider-supported mechanism.       | Provider          | Must     | Prototype, Demo / mock permitted during early build | The user can initiate a connection; ==CRiB does not request or store the provider password.==                                                       |
| FR-06 | The system shall record a provider connection only for the authenticated user who authorized it.                                      | Provider          | Must     | Demo                                                | ==A user can see and use only their own provider connections==; a second user cannot retrieve or alter them.                                        |
| FR-07 | The system shall show connected resources as a list with at least name, resource type, provider, and modified date when available.    | Core              | Must     | Prototype, Demo                                     | The list distinguishes provider/source and handles unavailable metadata without breaking the screen.                                                |
| FR-08 | The system shall allow navigation into and out of folders where the provider supports folders.                                        | Core              | Must     | Prototype, Demo                                     | Selecting a folder updates the displayed contents and exposes a clear route/breadcrumb back.                                                        |
| FR-09 | The system shall let a user search the currently available resource set by name.                                                      | Search and Filter | Must     | Prototype, Demo                                     | A search term visibly narrows matching results; empty results have a clear state and reset action.                                                  |
| FR-10 | The system shall let a user apply at least one simple resource filter, such as type.                                                  | Search and Filter | Should   | Prototype, Demo                                     | Applying/removing a filter changes the shown resources and makes the active filter visible.                                                         |
| FR-11 | The system shall let a user access or download an eligible selected resource using a provider-permitted route.                        | Provider          | Must     | Prototype, Demo where provider permits              | The action is only available for eligible resources; failures show a useful error and do not expose another user's resource.                        |
| FR-12 | The system shall warn a user when a connection has expired or failed and provide a reauthorization/retry action.                      | Provider          | Should   | Prototype, Demo if real provider                    | An expired/failed connection has a clear status, does not silently show stale authority, and offers the next step.                                  |
| FR-13 | The system shall let a user view and disconnect their own provider connection.                                                        | Core/Provider     | Should   | Prototype, Demo                                     | Disconnect requires confirmation, removes/revokes local usable connection state as applicable, and updates the dashboard.                           |
| FR-14 | The system shall provide loading, empty, permission-denied, and service-error states for the main connection and browsing flow.       | Core              | Must     | Prototype, Demo                                     | Each specified state is designed and can be reached or demonstrated; messages do not reveal secrets or implementation internals.                    |
| FR-15 | The system may remember a user's last list/display preference after a deliberate selection.                                           | Core              | Could    | Prototype, Demo only if time permits                | A changed preference persists for the same authenticated user and can be changed again.                                                             |

## 7. Non-functional requirements

| ID     | Requirement                                                                                                                                                                      | Module              | Priority    | Acceptance criteria / measure                                                                                                                            |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-01 | **Security - authentication.** Passwords, if used, shall never be stored in plaintext; authenticated session material shall be protected.                                        | Auth                | Must        | Implementation review verifies a proven password-hashing library or similar and no plaintext passwords/secrets in source, logs, or database fixtures.    |
| NFR-02 | **Security - authorization.** Every protected API/resource action shall verify the authenticated user and ownership of the provider connection/resource.                         | Auth                | Must/Should | A negative integration test proves that User B cannot access a connection or resource requested with User A's identifier.                                |
| NFR-03 | **Security - provider credentials.** CRiB shall use the provider-supported authorization flow and shall not collect provider passwords.                                          | Auth                | Must        | Connection UI redirects/uses the provider authorization flow; review confirms minimum required scopes and protected token handling.                      |
| NFR-04 | **Security - common web risks.** Inputs shall be validated, database access shall be parameterized/ORM-backed, and errors shall not expose stack traces or secrets to end users. | Auth                | Must        | Tests or review cover invalid input and unsafe access attempts; deployed error response is safe and understandable.                                      |
| NFR-05 | **Privacy.** The app shall minimize retained provider data and avoid storing file content unless explicitly required for a demonstrated feature.                                 | Core                | Must        | Data model documents the purpose of each stored field; no bulk file-copy feature is implemented in the MVP.                                              |
| NFR-06 | **Usability.** The primary journey shall be understandable without team assistance.                                                                                              | Core                | Must        | At least two independent test users can complete sign-in, connection (or mock connection), browsing, search, and resource action; findings are recorded. |
| NFR-07 | **Accessibility.** The core UI shall support keyboard navigation, visible focus, semantic labels, sufficient colour contrast, and non-colour-only status cues.                   | Core                | Should      | Manual keyboard pass and automated/lint audit find no critical issues in the primary flow; design includes labels/error text.                            |
| NFR-08 | **Responsive behaviour.** Core screens shall work from a narrow mobile viewport through desktop.                                                                                 | Core                | Should      | Prototype shows mobile and desktop variants for dashboard and resource browser; implementation has no horizontal overflow in the primary flow.           |
| NFR-09 | **Performance.** The resource list shall avoid loading an unbounded remote collection in one request.                                                                            | Core/Provider       | Should      | The design/API documents paging or a bounded result size; a normal test-data list becomes usable within an agreed demo target.                           |
| NFR-10 | **Reliability.** Provider/API failures and missing metadata shall degrade gracefully.                                                                                            | Core/Provider       | Must        | A simulated provider error and an empty/partial response result in a recoverable UI state rather than a broken page.                                     |
| NFR-11 | **Maintainability.** Provider-specific code shall be isolated behind an adapter/service boundary with documented common resource fields.                                         | Provider            | Should      | A mock provider and selected real-provider adapter can both satisfy the same documented interface without changing core browsing logic.                  |
| NFR-12 | **Testability and delivery.** The project shall have repeatable build/test instructions and a lightweight automated check on pull requests.                                      | Core                | Should      | Repository README documents local start/test steps; pull request workflow runs at least lint/build and selected tests.                                   |
| NFR-13 | **Cost control.** The deployed solution shall use free/low-cost tiers where practicable and avoid storing user files by default.                                                 | Architecture/DevOps | Must        | ==Hosting decision records expected free-tier limits and an owner checks any billing safeguards/usage limits.==                                          |


## 8. Data and integration baseline

The initial normalized resource view should use only fields that the chosen provider can reasonably supply:

```dirtree
- Resource
	- id                  # CRiB identifier where needed
	- provider
	- providerResourceId
	- name
	- kind                # file or folder
	- mimeType            # optional
	- size                # optional
	- createdAt           # optional
	- modifiedAt          # optional
	- parentId            # optional
	- accessAction        # allowed / unavailable, not a stored secret
```

Minimum persisted concepts: `user`, `provider_connection`, and (only if needed) sanitized/cached `resource metadata`. Access and refresh tokens are sensitive data; their storage approach must be decided before real-provider deployment.

## 9. Assumptions, dependencies, and open questions

### Assumptions

- ==The team has access to the tooling suite recommended== (i.e. Figma, Excalidraw, GitHub, and/or a free/low-cost hosting option).
- ==Test cloud accounts/data can be used without exposing personal files.==
- The selected provider supplies a lawful developer/OAuth path compatible with the team's deployment model.
- *Assessment 1 accepts a shareable interactive prototype plus a PDF/documented design rather than a production-complete application.*

### Open questions to close

| ID    | Question                                                                                        | Why it matters                                                                      | Target decision point                                                                                                 | Module       | Owner |
| ----- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------ | ----- |
| OQ-01 | Which one provider is first: Google Drive, OneDrive, or Dropbox?                                | Determines OAuth, API model, test accounts, Figma wording, and the technical spike. | Before implementation planning.                                                                                       | Provider     |       |
| OQ-02 | Is user email verification required for assessment, or only desirable?                          | Changes identity flow and delivery risk.                                            | Before auth build.                                                                                                    | Core/Auth    |       |
| OQ-03 | Which deployment option can host the chosen backend/database inside the cost constraint?        | Affects stack feasibility and public-demo reliability.                              | After the stack/provider spike.                                                                                       | Architecture |       |
| OQ-04 | Does the assessment require named team contribution evidence or a specific presentation format? | Affects GitHub workflow and final artefact structure.                               | As soon as teaching guidance is available. ==Or can be assumed and expanded by the team in a clear transparent way,== | Core         |       |
| OQ-05 | Is download enough for the demo, or must CRiB preview file content?                             | Prevents an unbounded preview/streaming feature from entering scope.                | Before finalising demo acceptance tests.                                                                              | Core         |       |

## 10. Traceability and change control

- Use these IDs (data, functional and non-functional requirements, open questions) in Figma annotations, GitHub issues, pull requests, tests, and the final demo script.
- Record a requirement change as: ID, reason, decision date, owner, affected screens/components, and assessment impact.
- Do not promote a `Should` or `Could` item into the demo commitment without full team commitment and naming what it displaces.
- ==Suggestion: Keep a one-page decision log next to this document for provider, stack, hosting, and security-storage decisions.==

