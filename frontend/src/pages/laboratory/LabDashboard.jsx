import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { useApiData } from '../../hooks/useApiData';
import laboratoryService from '../../services/laboratoryService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';

export default function LabDashboard() {
  const { user } = useAuth();
  const fetchData = useCallback(() => laboratoryService.listRequests(), []);
  const { data: requests, loading, error, refetch } = useApiData(fetchData, []);

  if (loading) return <LoadingSpinner fullPage label="Loading dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const byStatus = (status) => requests.filter((r) => r.status === status).length;

  return (
    <div className="sanad-page">
      <h1>Welcome, {user.name}</h1>
      <div className="sanad-stat-grid">
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('sent')}</span><span>New Requests</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('accepted')}</span><span>Accepted</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('processing')}</span><span>Processing</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{byStatus('completed')}</span><span>Completed</span></div>
      </div>
      <div className="sanad-quick-links">
        <Link className="sanad-btn sanad-btn-primary" to="/laboratory/requests">View All Requests</Link>
      </div>
    </div>
  );
}
