# Setup Guide

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| Python | 3.11 |
| Node.js | 18 |
| PostgreSQL | 15 |
| Docker & Docker Compose | 24 (optional) |

---

## 1. Clone the repository

```bash
git clone https://github.com/your-org/smart-parking-system.git
cd smart-parking-system
```

---

## 2. Environment variables

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY and your DATABASE_URL
```

---

## 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at <http://localhost:8000/docs>

---

## 4. Frontend

```bash
cd frontend
cp .env.example .env              # adjust REACT_APP_API_URL if needed
npm install
npm start                         # http://localhost:3000
```

---

## 5. Detection module

```bash
# Install detection dependencies (in a separate venv recommended)
pip install -r detection/requirements.txt

# Annotate parking spaces
python -m detection.annotator --image path/to/lot.jpg --output annotations.json

# Run detection on an image
python - <<'PY'
from detection.detector import ParkingDetector
det = ParkingDetector(annotations_path="annotations.json")
print(det.detect_from_image("path/to/lot.jpg"))
PY

# Train the CNN
python -m detection.cnn.train \
    --data-dir datasets/pklot \
    --output-dir model_weights \
    --epochs 50
```

---

## 6. Running tests

```bash
pip install -r tests/requirements.txt
pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## 7. Docker (recommended for production)

```bash
docker compose up --build
```

This starts:
- `postgres` on port 5432
- `backend` on port 8000
- `frontend` on port 3000

---

## Key environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | asyncpg connection string | `postgresql+asyncpg://postgres:password@localhost:5432/smart_parking` |
| `SECRET_KEY` | JWT signing secret | `changeme-…` (**change in production**) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `DEBUG` | Enable debug mode | `False` |
| `REACT_APP_API_URL` | Frontend API base URL | `http://localhost:8000` |
