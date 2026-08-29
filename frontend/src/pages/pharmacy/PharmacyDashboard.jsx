import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { useApiData } from '../../hooks/useApiData';
import pharmacyService from '../../services/pharmacyService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';

export default function PharmacyDashboard() {
  const { user } = useAuth();
  const fetchData = useCallback(() => pharmacyService.listPrescriptions(), []);
  const { data: prescriptions, loading, error, refetch } = useApiData(fetchData, []);

  if (loading) return <LoadingSpinner fullPage label="Loading dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const byStatus = (status) => prescriptions.filter((p) => p.pharmacy_status === status).length;

  return (
    <div className="sanad-page">
      <h1>Welcome, {user.name}</h1>
      <div className="sanad-stat-grid">
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('pending')}</span><span>Pending</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('received')}</span><span>Received</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('prepared')}</span><span>Prepared</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('completed')}</span><span>Completed</span></div>
      </div>
      <div className="sanad-quick-links">
        <Link className="sanad-btn sanad-btn-primary" to="/pharmacy/queue">View Queue</Link>
      </div>
    </div>
  );
}
