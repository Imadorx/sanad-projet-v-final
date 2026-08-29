import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

/**
 * Wraps a route that requires authentication and, optionally, one of a
 * set of SANAD roles. Redirects to /login (preserving the intended
 * destination) if unauthenticated, or to /unauthorized if authenticated
 * but lacking a required role - this is a UI convenience only; the
 * actual access control is enforced server-side by Odoo record rules,
 * so this component can never itself be the source of a security bug.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <LoadingSpinner fullPage label="Checking your session..." />;

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const hasAccess = user.roles.some((r) => allowedRoles.includes(r));
    if (!hasAccess) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return children;
}
