import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🅿 Smart Parking</Link>
      </div>
      <ul className="navbar-links">
        {user && (
          <>
            <li><Link to="/dashboard">Dashboard</Link></li>
            <li><Link to="/map">Map</Link></li>
            {user.role === 'admin' && <li><Link to="/admin">Admin</Link></li>}
          </>
        )}
      </ul>
      <div className="navbar-auth">
        {user ? (
          <div className="navbar-user">
            <span className="navbar-username">{user.full_name}</span>
            <button className="btn btn-outline" onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <>
            <Link to="/login" className="btn btn-outline">Login</Link>
            <Link to="/register" className="btn btn-primary">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
