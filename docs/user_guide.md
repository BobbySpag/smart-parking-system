# User Guide

## Drivers

### Finding available parking

1. Open the app and **register** or **log in**.
2. The **Dashboard** shows all parking lots with colour-coded availability:
   - 🟢 **Green** – plenty of spaces available
   - 🟡 **Amber** – fewer than 20% of spaces remain
   - 🔴 **Red** – lot is full
3. The dashboard **auto-refreshes every 30 seconds**. Click **⟳ Refresh** for an instant update.

### Navigating to a lot

1. Click **View Map** on any lot card, or navigate to **Map** in the top menu.
2. Green markers indicate available lots; red markers indicate full lots.
3. Click a marker to see the lot name, address, and current availability.
4. Click **Navigate** to open Google Maps with turn-by-turn directions.

---

## Staff

Staff can view the same dashboard as drivers. In addition, staff can update space statuses via the API (typically done automatically by the detection module).

**Update a space status (API):**
```http
PUT /api/parking/spaces/{space_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{ "is_occupied": true, "detection_method": "manual" }
```

---

## Admins

### Managing parking lots

1. Log in with an admin account.
2. Navigate to **Admin** in the top menu.
3. The **Parking Lots** table shows all lots with occupancy statistics.
4. Use the **Create New Lot** form to add a lot:
   - Enter name, address, GPS coordinates, and total number of spaces.
   - Click **Create Lot**.

### Managing users

The **Users** section of the admin dashboard lists all registered accounts with their role and active status.

To promote a user or deactivate an account, use the admin API:
```http
PUT /api/admin/users/{user_id}   # not yet in UI – use API directly
```

### Viewing occupancy statistics

The stats bar at the top of the admin dashboard shows:
- Total number of users
- Total number of lots
- Aggregate occupied/total spaces

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "Failed to load parking data" | Backend unreachable | Check `REACT_APP_API_URL` and that the backend is running |
| Login returns 401 | Wrong credentials | Reset password or check the email used |
| Map shows no markers | No lots in database | Create lots via Admin → Create New Lot |
| Token expired | Session older than 30 min | Log out and log back in |
