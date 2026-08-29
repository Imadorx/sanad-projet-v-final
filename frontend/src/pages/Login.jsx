import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useFormValidation, validators } from '../hooks/useFormValidation';

const ROLE_HOME = {
  admin: '/admin',
  doctor: '/doctor',
  patient: '/patient',
  laboratory: '/laboratory',
  pharmacy: '/pharmacy',
};

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState(null);

  const { values, errors, setField, validate } = useFormValidation(
    { login: '', password: '' },
    {
      login: validators.required('Email or username'),
      password: validators.required('Password'),
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      const user = await login(values.login, values.password);
      const from = location.state?.from?.pathname;
      const home = ROLE_HOME[user.roles[0]] || '/';
      navigate(from || home, { replace: true });
    } catch (err) {
      setServerError(err.apiMessage || 'Login failed. Check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="sanad-auth-page">
      <form className="sanad-auth-card" onSubmit={handleSubmit} noValidate>
        <h1>SANAD</h1>
        <p className="sanad-muted">Healthcare Management Platform</p>

        {serverError && <div className="sanad-alert sanad-alert-error">{serverError}</div>}

        <label htmlFor="login">Email / Username</label>
        <input
          id="login"
          type="text"
          value={values.login}
          onChange={(e) => setField('login', e.target.value)}
          autoComplete="username"
        />
        {errors.login && <span className="sanad-field-error">{errors.login}</span>}

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={values.password}
          onChange={(e) => setField('password', e.target.value)}
          autoComplete="current-password"
        />
        {errors.password && <span className="sanad-field-error">{errors.password}</span>}

        <button type="submit" className="sanad-btn sanad-btn-primary" disabled={submitting}>
          {submitting ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}
