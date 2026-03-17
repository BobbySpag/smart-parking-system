import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

function UserTable({ users }) {
  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Joined</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.full_name}</td>
              <td>{u.email}</td>
              <td><span className={`badge badge--${u.role}`}>{u.role}</span></td>
              <td>{u.is_active ? '✅ Active' : '❌ Inactive'}</td>
              <td>{new Date(u.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CreateLotForm({ onCreated }) {
  const [form, setForm] = useState({ name: '', address: '', latitude: '', longitude: '', total_spaces: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSubmitting(true);
    try {
      await api.post('/api/admin/lots', {
        ...form,
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        total_spaces: parseInt(form.total_spaces, 10),
      });
      setSuccess('Parking lot created!');
      setForm({ name: '', address: '', latitude: '', longitude: '', total_spaces: '' });
      onCreated();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create lot.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="admin-card">
      <h3>Create New Lot</h3>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit} className="admin-form">
        <div className="form-row">
          <div className="form-group">
            <label>Name</label>
            <input name="name" value={form.name} onChange={handleChange} required className="form-input" />
          </div>
          <div className="form-group">
            <label>Total Spaces</label>
            <input name="total_spaces" type="number" min="1" value={form.total_spaces} onChange={handleChange} required className="form-input" />
          </div>
        </div>
        <div className="form-group">
          <label>Address</label>
          <input name="address" value={form.address} onChange={handleChange} required className="form-input" />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Latitude</label>
            <input name="latitude" type="number" step="any" value={form.latitude} onChange={handleChange} required className="form-input" />
          </div>
          <div className="form-group">
            <label>Longitude</label>
            <input name="longitude" type="number" step="any" value={form.longitude} onChange={handleChange} required className="form-input" />
          </div>
        </div>
        <button type="submit" disabled={submitting} className="btn btn-primary">
          {submitting ? 'Creating…' : 'Create Lot'}
        </button>
      </form>
    </div>
  );
}

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const [usersRes, lotsRes] = await Promise.all([
        api.get('/api/admin/users'),
        api.get('/api/parking/lots'),
      ]);
      setUsers(usersRes.data);
      setLots(lotsRes.data);
      setError('');
    } catch {
      setError('Failed to load admin data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const totalOccupied = lots.reduce((s, l) => s + l.occupied_spaces, 0);
  const totalSpaces = lots.reduce((s, l) => s + l.total_spaces, 0);

  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <p>Loading…</p>
      ) : (
        <>
          <div className="stats-bar">
            <div className="stat"><span className="stat-value">{users.length}</span><span className="stat-label">Users</span></div>
            <div className="stat"><span className="stat-value">{lots.length}</span><span className="stat-label">Lots</span></div>
            <div className="stat"><span className="stat-value">{totalOccupied}/{totalSpaces}</span><span className="stat-label">Occupied</span></div>
          </div>

          <section className="admin-section">
            <h2>Parking Lots</h2>
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr><th>Name</th><th>Address</th><th>Spaces</th><th>Occupied</th><th>Available</th><th>Active</th></tr>
                </thead>
                <tbody>
                  {lots.map((l) => (
                    <tr key={l.id}>
                      <td>{l.name}</td>
                      <td>{l.address}</td>
                      <td>{l.total_spaces}</td>
                      <td>{l.occupied_spaces}</td>
                      <td>{l.available_spaces}</td>
                      <td>{l.is_active ? '✅' : '❌'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="admin-section">
            <CreateLotForm onCreated={fetchData} />
          </section>

          <section className="admin-section">
            <h2>Users</h2>
            <UserTable users={users} />
          </section>
        </>
      )}
    </div>
  );
}
