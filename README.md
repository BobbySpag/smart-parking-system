# Smart Parking System 🅿

A full-stack smart parking system that uses computer vision to detect real-time parking space occupancy and displays availability to users via an interactive web dashboard and map.

## Features

- 🔍 **Real-time occupancy detection** using OpenCV and a custom CNN (TensorFlow/Keras)
- 🗺️ **Interactive Leaflet map** showing lot locations and availability
- 📊 **Live dashboard** with colour-coded availability cards and auto-refresh
- 🔐 **JWT-based authentication** with role-based access (driver / staff / admin)
- ⚙️ **Admin panel** for managing parking lots and users
- 🐳 **Docker Compose** for one-command deployment

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router v6, React-Leaflet, Axios |
| Backend | FastAPI 0.104, SQLAlchemy 2.0 (async), Alembic |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Database | PostgreSQL 15 |
| Detection | OpenCV 4.8, TensorFlow 2.14 (CNN) |
| Containers | Docker, Docker Compose |
| Tests | pytest, pytest-asyncio, httpx |

## Quick Start

### Using Docker Compose (recommended)

```bash
git clone https://github.com/your-org/smart-parking-system.git
cd smart-parking-system
cp .env.example .env          # Set SECRET_KEY and DATABASE_URL
docker compose up --build
```

- Frontend: <http://localhost:3000>
- API docs: <http://localhost:8000/docs>

### Local Development

See [docs/setup.md](docs/setup.md) for a full step-by-step guide.

```bash
# Backend
cd backend && pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm start
```

## Project Structure

```
smart-parking-system/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── main.py           # App factory & CORS
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # Async SQLAlchemy engine
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routes/           # auth, parking, admin routers
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic
│   │   └── middleware/       # Auth middleware
│   ├── alembic/              # Database migrations
│   └── requirements.txt
├── detection/                # Computer vision module
│   ├── detector.py           # Main ParkingDetector class
│   ├── preprocessor.py       # Image preprocessing utilities
│   ├── annotator.py          # GUI annotation tool
│   ├── utils.py              # Drawing & I/O helpers
│   └── cnn/                  # CNN training & inference
│       ├── model.py
│       ├── train.py
│       ├── predict.py
│       └── data_loader.py
├── frontend/                 # React application
│   ├── src/
│   │   ├── App.js
│   │   ├── components/       # Dashboard, Map, Auth forms, Navbar
│   │   ├── context/          # AuthContext
│   │   └── services/         # Axios instance, JWT helpers
│   └── public/
├── tests/
│   ├── test_backend/         # pytest tests for API
│   └── test_detection/       # pytest tests for CV module
├── docs/                     # Architecture, API, setup, user guide
├── docker-compose.yml
└── .env.example
```

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Register user, get token |
| POST | `/api/auth/login` | — | Login (OAuth2 form) |
| GET | `/api/auth/me` | ✅ | Current user profile |
| GET | `/api/parking/lots` | ✅ | List all lots with availability |
| GET | `/api/parking/lots/{id}` | ✅ | Lot details |
| GET | `/api/parking/lots/{id}/spaces` | ✅ | All spaces in a lot |
| PUT | `/api/parking/spaces/{id}/status` | Staff+ | Update space occupancy |
| GET | `/api/admin/users` | Admin | List all users |
| POST | `/api/admin/lots` | Admin | Create parking lot |
| PUT | `/api/admin/lots/{id}` | Admin | Update parking lot |

Full documentation: [docs/api.md](docs/api.md)

## Running Tests

```bash
pip install -r tests/requirements.txt
pytest tests/ -v --cov=backend/app --cov-report=term-missing
```

## Deployment

### Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/BobbySpag/smart-parking-system)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/BobbySpag/smart-parking-system)

---

### Railway (Docker Compose – one click)

1. Click the **Deploy on Railway** button above (or go to [railway.app](https://railway.app) → New Project → Deploy from GitHub Repo).
2. Select `BobbySpag/smart-parking-system`. Railway will detect `railway.toml` and spin up all three services automatically.
3. In the Railway dashboard, set the following **environment variables** on the **backend** service:
   - `SECRET_KEY` – a strong random value (see [Environment Variables](#environment-variables) below)
   - `POSTGRES_PASSWORD` – the password for the managed PostgreSQL service
4. Railway automatically provisions public URLs for the backend and frontend. Copy the backend URL and set it as `REACT_APP_API_URL` on the **frontend** service.

---

### Render (Blueprint)

1. Click the **Deploy to Render** button above (or go to [render.com](https://render.com) → New → Blueprint).
2. Connect `BobbySpag/smart-parking-system`. Render will read `render.yaml` and create:
   - A **PostgreSQL** database (`smart-parking-db`, free tier)
   - A **Web Service** for the FastAPI backend
   - A **Static Site** for the React frontend
3. After the first deploy, copy the backend service URL (e.g. `https://smart-parking-backend.onrender.com`) and set it as `REACT_APP_API_URL` in the frontend service's environment variables, then trigger a redeploy of the frontend.
4. **Important:** Render's free PostgreSQL databases expire after 90 days – upgrade to a paid plan for production use.

---

### Fly.io (Backend only)

```bash
# Install the Fly CLI
curl -L https://fly.io/install.sh | sh

# Authenticate
fly auth login

# Create and deploy the backend app (uses fly.toml at the repo root)
fly launch --copy-config --name smart-parking-api
fly secrets set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
fly secrets set DATABASE_URL="postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>"
fly deploy
```

The `fly.toml` file is pre-configured with:
- Internal port `8000`
- Health check on `/health`
- `shared-cpu-1x` VM with 256 MB RAM
- Auto-stop / auto-start machines for cost efficiency

---

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | ✅ | Async PostgreSQL connection string | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | ✅ | JWT signing secret – **use a strong random value in production** | `openssl rand -hex 32` |
| `ALGORITHM` | ✅ | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token TTL in minutes | `30` |
| `DEBUG` | — | Enable debug mode (default `false`) | `false` |
| `REACT_APP_API_URL` | ✅ (frontend) | Backend base URL used by the React app | `https://api.example.com` |
| `REACT_APP_MAPBOX_TOKEN` | — | Mapbox public token for map tiles | `pk.ey...` |

> ⚠️ **Security reminder:** Never commit a real `SECRET_KEY` to version control. Generate one with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```
> A production-ready template is available in [`.env.production.example`](.env.production.example).

---

### CI/CD (GitHub Actions)

The repository includes a GitHub Actions workflow at `.github/workflows/ci-cd.yml` that:

- **CI** (every push and PR to `main`): runs `pytest` against the backend and verifies the React app builds successfully.
- **CD** (push to `main` only, after CI passes): triggers a Render deploy hook.

To enable automatic deployment, add your Render deploy hook URL as a repository secret named `RENDER_DEPLOY_HOOK_URL` (Settings → Secrets and variables → Actions → New repository secret).

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please ensure all tests pass and add tests for new functionality.

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.
