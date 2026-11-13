# Backend (Flask + MongoDB)

API for Creator EaaS: user accounts, projects, and checkout/check-in of
HWSet1 (10 camera kits) and HWSet2 (8 audio and lighting kits).

The request and response shapes match the frontend stubs in
`creator-eaas/src/api/index.js`, field names included, so the frontend can
swap a stub for a real call without changing anything else.

## Setup

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Run

Without installing MongoDB (data is lost when the server stops):

```bash
USE_MOCK_DB=1 python app.py
```

Against a real MongoDB, local or a free MongoDB Atlas cluster, set
`MONGO_URI` in `.env` and run. Accounts are stored in `haas_users` and
projects in `haas_projects`. Set `USERS_MONGO_URI` and `PROJECTS_MONGO_URI`
to put those databases on different clusters:

```bash
python app.py
```

The API starts at `http://localhost:5001`. Try `GET /api/health`.
It uses 5001 because macOS reserves port 5000 for AirPlay Receiver. Set
`PORT` in `.env` to change it.

## Test

```bash
pytest
```

Tests use `mongomock`, an in-memory fake MongoDB, so they don't need a real
database.

## How it's organized

| Folder or file | Job |
|---|---|
| `app.py` | Builds the Flask app: config, database connection, seeding, routes. |
| `config.py` | Reads settings from environment variables and `.env`. |
| `extensions.py` | Holds the users database connection and the projects database connection. |
| `userid_crypto.py` | Encrypts user IDs before they are stored. Set `USERID_ENCRYPTION_KEY` once per deployment and never change it. |
| `models/` | One class per collection. The only code that queries MongoDB. |
| `routes/` | One Flask blueprint per group of endpoints. Validates input, calls models, returns JSON. |
| `tests/` | PyTest suite. |

## Data

Accounts and projects are separate databases. With one `MONGO_URI` they share a cluster and use different database names. With `USERS_MONGO_URI` and `PROJECTS_MONGO_URI` they are different clusters. The database name inside a URI is ignored.

| Database | Collection | One document holds |
|---|---|---|
| `haas_users` | `users` | `userid_hash` (keyed HMAC, for lookups), `userid_encrypted` (Fernet ciphertext) and `password_hash`. Neither the user ID nor the password is stored as typed; see `userid_crypto.py` |
| `haas_projects` | `projects` | `projectId`, `name`, `description`, `ownerUserid`, `members` (userids who can use it, owner first), and `checkedOut`: kits out per set, like `{"HWSet1": 3}` |
| `haas_projects` | `hardware_sets` | `setId`, `name`, `capacity`, `available`, `contents` |
| `haas_projects` | `checkout_records` | History: `projectId`, `setId`, `quantity`, `action` (`checkout` or `checkin`), `at` |

Documents already stored in the old `haas_db` database are not copied over.

Hardware sets are created on startup from `Hardware.DEFAULT_SETS` in
`models/hardware.py`. Restarting refreshes names and contents but never
resets `available`.

## Endpoints

Errors always come back as `{"error": "<message for the user>"}`.
🔒 = must be signed in (401 otherwise). Signing up or in stores the userid in
a signed session cookie that lasts 7 days, so a refresh keeps you signed in.
Sign-up needs a password of at least 8 characters.

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/api/health` | | `200 {status, usersDb, projectsDb}` | |
| POST | `/api/auth/signup` | `{userid, password}` | `201 {userid}` | 400 missing field, 409 user ID taken |
| POST | `/api/auth/signin` | `{userid, password}` | `200 {userid}` | 400 missing field, 401 wrong user ID or password |
| GET | `/api/auth/me` | | `200 {userid}` (`null` if signed out) | |
| POST | `/api/auth/signout` | | `200 {userid: null}` | |
| GET | `/api/projects` 🔒 | | `200` list of `{projectId, name, ownerUserid, members}` for projects you created or joined, sorted by name | |
| POST | `/api/projects` 🔒 | `{projectId, name, description}` | `201` project, owned by the signed-in user, `members` is just you | 400 missing field, 409 project ID taken |
| GET | `/api/projects/<projectId>` 🔒 | | `200` project, including `members` | 403 you haven't joined it, 404 no such project |
| POST | `/api/projects/<projectId>/join` 🔒 | | `200` project, with you added to `members`. Joining again is harmless | 404 no such project |
| GET | `/api/hardware` | | `200` list of hardware sets | |
| POST | `/api/hardware/checkout` 🔒 | `{projectId, setId, quantity}` | `200` updated hardware list | 400 bad input, 403 you haven't joined the project, 404 unknown project or set, 409 not enough on the shelf |
| POST | `/api/hardware/checkin` 🔒 | `{projectId, setId, quantity}` | `200` updated hardware list | 400 bad input, 403 you haven't joined the project, 404 unknown project or set, 409 more than the project has out |

## Rules the backend enforces

- A checkout can't take more kits than are on the shelf. The check and the
  update are one database operation, so two people can't both take the
  last kit.
- A check-in can't return more kits than that project has out, so
  availability never goes above capacity.
- Quantities must be whole numbers greater than 0.

## Known limitations

- Checkout and check-in each update two documents (the hardware set and
  the project) in separate steps. If the server crashed between them, the
  counts could drift. MongoDB transactions would fix this. They need a
  replica set, which MongoDB Atlas provides.
- Anyone who knows a project's ID can join it with
  `POST /api/projects/<projectId>/join`; there are no invites and no way to
  remove someone. Only the owner and the people on `members` can open the
  project or check kits in and out. Documents created before `members`
  existed have no `members` field; their owner is the whole crew until
  someone joins.
