import React from 'react';
import { Link } from 'react-router-dom';

export default function Unauthorized() {
  return (
    <div className="sanad-auth-page">
      <div className="sanad-auth-card">
        <h1>Access Denied</h1>
        <p>You do not have permission to view this page.</p>
        <Link className="sanad-btn sanad-btn-primary" to="/">Go Home</Link>
      </div>
    </div>
  );
}
