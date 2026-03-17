import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import api from '../services/api';

// Fix default Leaflet icon paths broken by webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const availableIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const fullIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

export default function ParkingMap() {
  const { id } = useParams();
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [center, setCenter] = useState([51.505, -0.09]);

  const fetchLots = useCallback(async () => {
    try {
      if (id) {
        const res = await api.get(`/api/parking/lots/${id}`);
        setLots([res.data]);
        setCenter([res.data.latitude, res.data.longitude]);
      } else {
        const res = await api.get('/api/parking/lots');
        setLots(res.data);
        if (res.data.length > 0) {
          setCenter([res.data[0].latitude, res.data[0].longitude]);
        }
      }
      setError('');
    } catch {
      setError('Failed to load parking data.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchLots(); }, [fetchLots]);

  const openNavigation = (lat, lng) => {
    window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`, '_blank');
  };

  if (loading) return <p className="loading-text">Loading map…</p>;
  if (error) return <div className="alert alert-error">{error}</div>;

  return (
    <div className="map-page">
      <h1>{id ? 'Parking Lot' : 'All Parking Lots'}</h1>
      <MapContainer center={center} zoom={id ? 16 : 12} className="map-container">
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {lots.map((lot) => (
          <Marker
            key={lot.id}
            position={[lot.latitude, lot.longitude]}
            icon={lot.available_spaces > 0 ? availableIcon : fullIcon}
          >
            <Popup>
              <div className="map-popup">
                <h4>{lot.name}</h4>
                <p>{lot.address}</p>
                <p>
                  <strong>{lot.available_spaces}</strong> / {lot.total_spaces} spaces free
                </p>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => openNavigation(lot.latitude, lot.longitude)}
                >
                  Navigate
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
