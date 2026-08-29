import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import NotificationBell from './NotificationBell';

const NAV_ITEMS = [
  { to: '/patient', label: 'Dashboard', roles: ['patient'] },
  { to: '/patient/records', label: 'Medical Record', roles: ['patient'] },
  { to: '/patient/prescriptions', label: 'Prescriptions', roles: ['patient'] },
  { to: '/patient/lab-results', label: 'Lab Results', roles: ['patient'] },
  { to: '/patient/ai-assistant', label: 'AI Assistant', roles: ['patient'] },
  { to: '/patient/chat', label: 'Chat', roles: ['patient'] },

  { to: '/doctor', label: 'Dashboard', roles: ['doctor'] },
  { to: '/doctor/patients', label: 'Patients', roles: ['doctor'] },
  { to: '/doctor/consultations', label: 'Consultations', roles: ['doctor'] },
  { to: '/doctor/prescriptions', label: 'Prescriptions', roles: ['doctor'] },
  { to: '/doctor/lab-requests', label: 'Lab Requests', roles: ['doctor'] },
  { to: '/doctor/chat', label: 'Chat', roles: ['doctor'] },

  { to: '/laboratory', label: 'Dashboard', roles: ['laboratory'] },
  { to: '/laboratory/requests', label: 'Requests', roles: ['laboratory'] },

  { to: '/pharmacy', label: 'Dashboard', roles: ['pharmacy'] },
  { to: '/pharmacy/queue', label: 'Prescription Queue', roles: ['pharmacy'] },

  { to: '/admin', label: 'Dashboard', roles: ['admin'] },
  { to: '/admin/users', label: 'Users & Roles', roles: ['admin'] },
];

export default function Layout({ children }) {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const visibleNav = NAV_ITEMS.filter((item) => item.roles.some((r) => hasRole(r)));

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="sanad-app">
      <header className="sanad-header">
        <button
          className="sanad-menu-toggle"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          ☰
        </button>
        <div className="sanad-brand">SANAD</div>
        <div className="sanad-header-actions">
          <NotificationBell />
          <span className="sanad-user-name">{user?.name}</span>
          <button className="sanad-btn sanad-btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>
      <div className="sanad-body">
        <nav className={`sanad-sidebar ${menuOpen ? 'open' : ''}`}>
          {visibleNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to.split('/').length === 2}
              className={({ isActive }) => `sanad-nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="sanad-content">{children}</main>
      </div>
    </div>
  );
}
