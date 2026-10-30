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
`MONGO_URI` in `.env` and run:

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
| `extensions.py` | Holds the one shared database connection. |
| `models/` | One class per collection. The only code that queries MongoDB. |
| `routes/` | One Flask blueprint per group of endpoints. Validates input, calls models, returns JSON. |
| `tests/` | PyTest suite. |

## Data

| Collection | One document holds |
|---|---|
| `users` | `userid` and a hashed password (never the plain password) |
| `projects` | `projectId`, `name`, `description`, `ownerUserid`, `members` (userids who can use it, owner first), and `checkedOut`: kits out per set, like `{"HWSet1": 3}` |
| `hardware_sets` | `setId`, `name`, `capacity`, `available`, `contents` |
| `checkout_records` | History: `projectId`, `setId`, `quantity`, `action` (`checkout` or `checkin`), `at` |

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
| GET | `/api/health` | | `200 {status}` | |
| POST | `/api/auth/signup` | `{userid, password}` | `201 {userid}` | 400 missing field, 409 user ID taken |
| POST | `/api/auth/signin` | `{userid, password}` | `200 {userid}` | 400 missing field, 401 wrong user ID or password |
| GET | `/api/auth/me` | | `200 {userid}` (`null` if signed out) | |
| POST | `/api/auth/signout` | | `200 {userid: null}` | |
| GET | `/api/users?q=` 🔒 | | `200` up to 8 `{userid}` whose id starts with `q`. Blank `q` is `[]` | 401 signed out |
| GET | `/api/projects` 🔒 | | `200` list of `{projectId, name, ownerUserid, members}` for projects you own or were shared onto, sorted by name | |
| POST | `/api/projects` 🔒 | `{projectId, name, description}` | `201` project, owned by the signed-in user, `members` is just you | 400 missing field, 409 project ID taken |
| GET | `/api/projects/<projectId>` 🔒 | | `200` project, including `members` | 404 no such project, 403 not shared with you |
| POST | `/api/projects/<projectId>/members` 🔒 | `{userid}` | `200` updated project | 400 missing userid, 403 not on the project, 404 unknown project or user, 409 already a member |
| DELETE | `/api/projects/<projectId>/members/<userid>` 🔒 | | `200` updated project | 400 that userid is the owner, 403 not on the project, 404 not a member |
| GET | `/api/hardware` | | `200` list of hardware sets | |
| POST | `/api/hardware/checkout` 🔒 | `{projectId, setId, quantity}` | `200` updated hardware list | 400 bad input, 403 project isn't shared with you, 404 unknown project or set, 409 not enough on the shelf |
| POST | `/api/hardware/checkin` 🔒 | `{projectId, setId, quantity}` | `200` updated hardware list | 400 bad input, 403 project isn't shared with you, 404 unknown project or set, 409 more than the project has out |

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
- A project is visible only to its owner and the people on `members`.
  Documents created before sharing have no `members` field; those stay
  visible to the owner only until someone is added.
