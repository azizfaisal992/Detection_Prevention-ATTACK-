# MasqueradeGuard

MasqueradeGuard is a localhost-only university Network Security project. It
preserves an intentionally vulnerable Python TCP banking lab and builds a
separate protected TCP service with a React monitoring interface.

## Local services

- Original vulnerable lab: `127.0.0.1:5001`
- Protected TCP foundation: `127.0.0.1:5002`
- Restricted Python HTTP bridge: `127.0.0.1:8080`
- React/Vite dashboard: `127.0.0.1:5173`

## Windows setup

Install Python 3.11 or newer and Node.js 20 LTS or newer. Open three PowerShell
terminals in this project folder.

Terminal 1:

```powershell
python -m backend.server
```

Terminal 2:

```powershell
python -m backend.http_bridge
```

Terminal 3:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The Dashboard status card reports a real TCP
response relayed through the HTTP bridge.

Open **Banking Demo** to use the protected TCP-backed banking workflow. Synthetic
demonstration credentials are prefilled in the form:

- Username: `demo.rahim`
- Password: `Taka@2025`

The protected account file stores only PBKDF2 password hashes. Session tokens
expire after 30 minutes, are stored only as SHA-256 hashes, and are invalidated
by logout.

<!-- ## Original vulnerable lab

Run this only on localhost for the educational comparison:

```powershell
python original_simulation/server.py
python original_simulation/bank_client.py
python original_simulation/attacker.py
```

The lab intentionally permits an unauthenticated balance lookup. Never expose
port 5001 beyond localhost. -->



With the original server, protected server, and bridge running, execute:

```powershell
python -m unittest tests.test_sprint1 -v
```

Run all currently available integration tests with:

```powershell
python -m unittest discover -s tests -v
```

## Security boundary

React is an interface only. The bridge recognizes only approved HTTP paths and
uses a fixed local TCP destination. Banking authentication, session verification,
and account authorization are performed by the protected TCP server rather than
React or the HTTP bridge.

