# Sprint 1 architecture

```text
React/Vite dashboard (127.0.0.1:5173)
        | GET /api/status (HTTP/JSON)
        v
Python http.server bridge (127.0.0.1:8080)
        | {"action":"status"}\n (TCP/JSON)
        v
Protected TCP server (127.0.0.1:5002)
```

The HTTP bridge has one explicitly allowlisted route and always connects to the
fixed local protected server. Browser input cannot select a TCP host, port, or
payload. The TCP protocol uses newline-delimited JSON, a message-size limit,
and socket timeouts.

The original intentionally vulnerable comparison is isolated in
`original_simulation/` on `127.0.0.1:5001`. Its `check_balance` action trusts a
caller-supplied username without authentication. It is educational localhost-only
code and is not connected to protected banking operations.

## Protected banking flow

```text
React Banking Demo
        | POST /api/login, /api/balance, /api/logout
        v
Allowlisted Python HTTP bridge
        | login, check_balance, logout (newline-delimited JSON over TCP)
        v
Protected TCP banking server
        |-- PBKDF2 credential verification
        |-- server-side session verification
        |-- account ownership enforcement
        v
backend/data/accounts.json + backend/data/sessions.json
```

The bridge never accepts a TCP host, port, action, or arbitrary payload from the
browser. Session tokens are returned to the authenticated client but only their
SHA-256 hashes are stored. The React application holds its token in memory and
does not persist it in browser storage.

