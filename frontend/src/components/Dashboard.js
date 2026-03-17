import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const POLL_INTERVAL_MS = 30_000;

function AvailabilityBar({ available, total }) {
  const pct = total > 0 ? Math.round((available / total) * 100) : 0;
  const colour = pct > 50 ? 'green' : pct > 20 ? 'amber' : 'red';
  return (
    <div className="availability-bar-wrap">
      <div className={`availability-bar availability-bar--${colour}`} style={{ width: `${pct}%` }} />
      <span className="availability-bar-label">{pct}% free</span>
    </div>
  );
}

function LotCard({ lot }) {
  const { id, name, address, available_spaces, total_spaces } = lot;
  const statusClass =
    available_spaces === 0 ? 'lot-card--full' : available_spaces <= 5 ? 'lot-card--low' : 'lot-card--available';

  return (
    <div className={`lot-card ${statusClass}`}>
      <h3 className="lot-card__name">{name}</h3>
      <p className="lot-card__address">{address}</p>
      <AvailabilityBar available={available_spaces} total={total_spaces} />
      <p className="lot-card__count">
        <strong>{available_spaces}</strong> / {total_spaces} spaces free
      </p>
      <Link to={`/parking/${id}`} className="btn btn-primary btn-sm">
        View Map
      </Link>
    </div>
  );
}

export default function Dashboard() {
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchLots = useCallback(async () => {
    try {
      const res = await api.get('/api/parking/lots');
      setLots(res.data);
      setLastUpdated(new Date());
      setError('');
    } catch (err) {
      setError('Failed to load parking data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLots();
    const interval = setInterval(fetchLots, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchLots]);

  const totalAvailable = lots.reduce((s, l) => s + l.available_spaces, 0);
  const totalSpaces = lots.reduce((s, l) => s + l.total_spaces, 0);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Parking Dashboard</h1>
        <div className="dashboard-actions">
          {lastUpdated && (
            <span className="last-updated">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button className="btn btn-outline btn-sm" onClick={fetchLots} disabled={loading}>
            {loading ? 'Refreshing…' : '⟳ Refresh'}
          </button>
        </div>
      </div>

      <div className="stats-bar">
        <div className="stat">
          <span className="stat-value">{lots.length}</span>
          <span className="stat-label">Lots</span>
        </div>
        <div className="stat">
          <span className="stat-value">{totalAvailable}</span>
          <span className="stat-label">Available</span>
        </div>
        <div className="stat">
          <span className="stat-value">{totalSpaces - totalAvailable}</span>
          <span className="stat-label">Occupied</span>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading && lots.length === 0 ? (
        <p className="loading-text">Loading parking lots…</p>
      ) : (
        <div className="lot-grid">
          {lots.map((lot) => (
            <LotCard key={lot.id} lot={lot} />
          ))}
          {lots.length === 0 && <p>No parking lots found.</p>}
        </div>
      )}
    </div>
  );
}
