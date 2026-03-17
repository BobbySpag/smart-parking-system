# API Documentation

Base URL: `http://localhost:8000`

All protected endpoints require the `Authorization: Bearer <token>` header.

---

## Authentication

### POST /api/auth/register
Register a new user account.

**Request body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "MyPass123",
  "full_name": "Jane Smith",
  "role": "driver"
}
```
`role` is optional (default: `"driver"`). Allowed values: `driver`, `staff`, `admin`.

**Response 201:**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

**Errors:** `409 Conflict` – email already registered.

---

### POST /api/auth/login
OAuth2 password flow.

**Request body (form-encoded):**
```
username=user@example.com&password=MyPass123
```

**Response 200:**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

**Errors:** `401 Unauthorized` – wrong credentials; `403 Forbidden` – account disabled.

---

### GET /api/auth/me
Get the current user's profile. **Requires auth.**

**Response 200:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Smith",
  "role": "driver",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

## Parking

### GET /api/parking/lots
List all active parking lots. **Requires auth.**

**Response 200:** Array of lot objects including `occupied_spaces` and `available_spaces`.

---

### GET /api/parking/lots/{lot_id}
Get a single parking lot with occupancy counts. **Requires auth.**

**Response 200:**
```json
{
  "id": "uuid",
  "name": "City Centre Car Park",
  "address": "1 Main St",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "total_spaces": 120,
  "is_active": true,
  "occupied_spaces": 45,
  "available_spaces": 75,
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors:** `404 Not Found`

---

### GET /api/parking/lots/{lot_id}/spaces
List all spaces in a lot. **Requires auth.**

**Response 200:** Array of space objects:
```json
[
  {
    "id": "uuid",
    "lot_id": "uuid",
    "space_number": "A1",
    "is_occupied": false,
    "coordinates_json": null,
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

---

### PUT /api/parking/spaces/{space_id}/status
Update occupancy status of a space. **Requires staff or admin role.**

**Request body:**
```json
{
  "is_occupied": true,
  "confidence_score": 0.95,
  "detection_method": "cnn"
}
```

`confidence_score` and `detection_method` are optional.

**Response 200:** Updated space object.

---

## Admin

### GET /api/admin/users
List all users. **Requires admin role.**

**Response 200:** Array of user objects.

---

### POST /api/admin/lots
Create a parking lot. **Requires admin role.**

**Request body:**
```json
{
  "name": "North Car Park",
  "address": "5 North Rd",
  "latitude": 51.51,
  "longitude": -0.13,
  "total_spaces": 50
}
```

**Response 201:** Created lot object.

---

### PUT /api/admin/lots/{lot_id}
Update a parking lot. **Requires admin role.** All fields optional.

**Request body:**
```json
{
  "name": "Renamed Lot",
  "is_active": false
}
```

**Response 200:** Updated lot object.

---

## Health

### GET /health
**Response 200:**
```json
{ "status": "ok", "version": "1.0.0" }
```
