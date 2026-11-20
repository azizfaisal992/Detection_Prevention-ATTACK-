# Sprint progress

## Sprint 1 - Repository Setup and React Foundation

Status: Complete (2026-11-21)

- Preserved the original TCP clients, vulnerable server, and demonstration data
  in `original_simulation/`.
- Added a separate localhost-only protected TCP server foundation with a real
  `status` command, bounded newline-delimited JSON, timeouts, and safe errors.
- Added a localhost-only `http.server` bridge with an explicit `/api/status`
  allowlist and fixed TCP destination.
- Added a React, Vite, and Tailwind dashboard foundation with responsive sidebar,
  navigation, placeholder pages, and a live protected-TCP connectivity card.
- Added Windows run instructions, architecture documentation, and five live
  integration tests.

Validation performed:

- Python syntax and JSON validation: passed.
- Five live integration tests passed using real loopback sockets: direct TCP
  status, HTTP-to-TCP status, HTTP route allowlist, malformed TCP JSON, and the
  preserved unauthenticated balance disclosure.
- Frontend npm install/build was not run because Node.js/npm is unavailable in
  the current execution environment.

Next: Sprint 2 will add hashed demonstration credentials, server-side sessions,
login, own-account balance checks, logout, and the Banking Demo UI after approval.

## Sprint 2 - Banking System and User Login

Status: Complete (2026-11-21)

- Added two synthetic protected accounts with PBKDF2-SHA256 password hashes.
- Added secure random session tokens, hashed token storage, expiration, logout,
  and locked atomic JSON persistence.
- Added protected TCP actions for login, own-account balance access, and logout.
- Added server-side ownership enforcement so an authenticated customer cannot
  request another customer's balance.
- Added fixed HTTP bridge routes for approved banking actions.
- Added the React Banking Demo with login, balance retrieval, session state,
  errors, and logout. No sprint number or completion message is shown in the UI.

Validation performed:

- Python syntax and JSON validation: passed.
- Sprint 1 live integration tests: passed.
- Sprint 2 live integration tests: passed, covering valid and invalid login,
  own-account access, identity mismatch denial, logout invalidation, hashed
  storage, and the HTTP-to-TCP banking workflow.
- React production build: passed.

Next: the attack comparison remains isolated until Sprint 3 is explicitly approved.

