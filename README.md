# Virtual Sports AI

Premium-style **virtual football analytics dashboard** with DEMO sample data, FastAPI backend, SQLite, JWT auth, and a transparent statistical prediction baseline.

> **All leagues, teams, odds, and default predictions are labeled DEMO.** This is not live BetPawa data and not real-money betting.

## Requirements

| Software | Status on your machine |
|----------|-------------------------|
| **Python 3.11+** | Detected: Python 3.12 |
| **Node.js LTS + npm** | **Install required** — not found on PATH during setup |
| **Git** (optional) | Recommended |

Install Node.js: [https://nodejs.org/](https://nodejs.org/) (LTS). Restart Cursor after install.

## First-time setup

```powershell
cd "C:\Users\Dj Mayson\Desktop\ai\virtual-sports-ai"

python -m venv backend\.venv
backend\.venv\Scripts\pip install -r backend\requirements.txt

cd frontend
npm install
cd ..
```

On first backend start, SQLite creates `backend/virtual_sports_ai.db` and seeds DEMO leagues, matches, odds, and an admin user.

## Run (Windows)

**Easy way:** double-click `start.bat` or:

```powershell
cd "C:\Users\Dj Mayson\Desktop\ai\virtual-sports-ai"
.\start.bat
```

**Manual way:**

```powershell
# Terminal 1 — backend
cd "C:\Users\Dj Mayson\Desktop\ai\virtual-sports-ai\backend"
..\\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — frontend
cd "C:\Users\Dj Mayson\Desktop\ai\virtual-sports-ai\frontend"
npm run dev
```

- **App:** [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Stop: run `stop.bat` or close the server windows.

## Admin dashboard

1. Log in at `/login`
2. **Email:** `admin@virtualsports.ai`
3. **Password:** `Admin123!`
4. Open **Admin** in the sidebar

Admins can manage users, premium access, free prediction limits, and trigger DEMO data refresh.

## Tests

```powershell
cd backend
..\\backend\.venv\Scripts\python.exe -m pytest -q
```

## Project layout

```
virtual-sports-ai/
  frontend/          React + Vite + Tailwind
  backend/app/       FastAPI, models, AI engine, providers
  start.bat / stop.bat
```

## Data providers

- `DemoDataProvider` — active by default
- `BetPawaProvider` — verified BetPawa Uganda JSON fixture and odds provider

Background refresh runs every **5 minutes** by default. For BetPawa, the scheduler also registers a one-time refresh at the next verified round start, so a new round is fetched immediately even though all matches start together. Refreshes are non-overlapping and retain the last successful dataset if the selected provider fails.

### Configuration

Create `backend/.env` or set environment variables before starting the backend:

```text
DATA_PROVIDER=demo
REFRESH_INTERVAL_MINUTES=5
BETPAWA_BASE_URL=https://www.betpawa.ug
BETPAWA_TIMEOUT_SECONDS=10
```

Use `DATA_PROVIDER=betpawa` after reviewing [the source investigation](docs/BETPAWA_DATA_SOURCE.md). The provider fetches verified live fixtures, results, and 1X2, O/U, BTTS, DC, and HT/FT odds. To switch back, set `DATA_PROVIDER=demo` and restart the backend.

Manual refresh is available from the dashboard or `POST /api/data/refresh`. The current provider, last successful update, last attempted fetch, status, and safe error message are available at `GET /api/data/status`. Admin refresh logs are available at `/api/admin/scraper-logs`.

If a source fails, check the status response and the scraper logs. A failed request never replaces a valid dataset with an empty response.

## Phases completed

1. Responsive dashboard UI (dark theme, markets, leagues, selections)
2. Backend + SQLite + idempotent DEMO seed
3. JWT auth + role-based limits
4. Analytics, match detail, prediction history
5. Baseline prediction engine + outcome evaluation hook
6. Admin panel + APScheduler
7. Windows scripts, tests, this README

See `TODO.md` for checklist details.
