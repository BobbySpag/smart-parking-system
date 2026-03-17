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

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please ensure all tests pass and add tests for new functionality.

## License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.
