# System Architecture

## Overview

The Smart Parking System is a full-stack application that detects parking space occupancy in real time using computer vision and serves the data via a REST API to a web frontend.

```
┌──────────────────────────────────────────────────────────┐
│                        Frontend                          │
│          React 18 + React-Leaflet + Axios                │
│   (Dashboard · Map · Admin · Auth)                       │
└──────────────────────┬───────────────────────────────────┘
                       │  HTTP / REST (JWT)
┌──────────────────────▼───────────────────────────────────┐
│                      Backend API                         │
│              FastAPI + SQLAlchemy 2.0 (async)            │
│   /api/auth  /api/parking  /api/admin                    │
└──────────┬───────────────────────┬───────────────────────┘
           │ asyncpg               │
┌──────────▼──────┐    ┌───────────▼──────────────────────┐
│   PostgreSQL 15 │    │         Detection Module          │
│  (parking lots, │    │  OpenCV + TensorFlow CNN          │
│   users, logs)  │    │  (space annotation + inference)   │
└─────────────────┘    └───────────────────────────────────┘
```

## Components

### Frontend (`frontend/`)
- **React 18** SPA with React Router v6
- **Leaflet / react-leaflet** for the interactive parking map
- **Axios** for API communication with JWT interceptors
- **AuthContext** for global authentication state

### Backend (`backend/`)
- **FastAPI** application with async request handling
- **SQLAlchemy 2.0** async ORM with **asyncpg** driver
- **Alembic** for database schema migrations
- **python-jose** for JWT token signing and verification
- **passlib + bcrypt** for secure password hashing
- Three route groups: `auth`, `parking`, `admin`

### Detection Module (`detection/`)
- **OpenCV** for image preprocessing and annotation
- **TensorFlow / Keras CNN** for binary occupancy classification
- `ParkingDetector` supports images, video files, and live cameras
- GUI `annotator.py` tool for labelling training data
- Training pipeline in `detection/cnn/train.py`

### Database
- **PostgreSQL 15** (production) / **SQLite** (tests)
- Tables: `users`, `parking_lots`, `parking_spaces`, `occupancy_logs`

## Data Flow

1. Detection module analyses a camera frame and calls `process_detection_result()`.
2. The service layer updates `parking_spaces.is_occupied` and appends an `occupancy_logs` record.
3. The frontend polls `GET /api/parking/lots` every 30 s and re-renders availability.
4. Admin users can create/edit lots via `POST /api/admin/lots`.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, React Router v6, Leaflet |
| API | FastAPI 0.104, Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Database | PostgreSQL 15 |
| CV | OpenCV 4.8, TensorFlow 2.14 |
| Migrations | Alembic 1.13 |
| Tests | pytest, pytest-asyncio, httpx |
| Container | Docker Compose |

## Deployment Architecture

```
Internet → Nginx (TLS termination)
              ├── /           → React static build
              └── /api/*      → Uvicorn (FastAPI)
                                    └── PostgreSQL
```
