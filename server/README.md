# Backend (Flask + MongoDB)

API for the Creator Equipment-as-a-Service app: user accounts, projects,
and hardware checkout/check-in for HWSet1 (camera kits) and HWSet2
(audio and lighting kits).

## Setup

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edit MONGO_URI if not using local default
```

Requires a running MongoDB instance (e.g. `brew services start mongodb-community`,
or a free MongoDB Atlas cluster -- point MONGO_URI at it).

## Run

```bash
python app.py
```

Starts the API at `http://localhost:5000`. Try `GET /api/health`.

## Test

```bash
pytest
```

Tests use `mongomock` (an in-memory fake Mongo), so they don't need a
real database running.

## Endpoints

| Method | Path                     | Purpose                              |
|--------|--------------------------|---------------------------------------|
| GET    | /api/health              | Liveness check                        |
| POST   | /api/auth/signup         | Create a user `{userid, password}`    |
| POST   | /api/auth/signin         | Verify credentials                    |
| POST   | /api/projects            | Create a project                      |
| GET    | /api/projects/\<id>      | Fetch a project                       |
| GET    | /api/hardware            | List HWSet1/HWSet2 capacity+available |
| POST   | /api/hardware/checkout   | `{project_id, set_id, quantity}`      |
| POST   | /api/hardware/checkin    | `{project_id, set_id, quantity}`      |
