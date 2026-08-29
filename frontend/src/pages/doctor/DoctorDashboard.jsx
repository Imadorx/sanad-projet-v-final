import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import laboratoryService from '../../services/laboratoryService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';

export default function DoctorDashboard() {
  const { user } = useAuth();

  const fetchAll = useCallback(async () => {
    const [patients, consultations, prescriptions, labRequests] = await Promise.all([
      patientService.list(),
      medicalService.listConsultations(),
      medicalService.listPrescriptions(),
      laboratoryService.listRequests({ status: 'sent' }),
    ]);
    return { patients, consultations, prescriptions, labRequests };
  }, []);

  const { data, loading, error, refetch } = useApiData(fetchAll, []);

  if (loading) return <LoadingSpinner fullPage label="Loading your dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { patients, consultations, prescriptions, labRequests } = data;
  const recentConsultations = [...consultations]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5);

  return (
    <div className="sanad-page">
      <h1>Welcome, Dr. {user.name}</h1>
      <div className="sanad-stat-grid">
        <div className="sanad-stat-card"><span className="sanad-stat-number">{patients.length}</span><span>Assigned Patients</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{consultations.length}</span><span>Consultations</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{prescriptions.length}</span><span>Prescriptions Issued</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{labRequests.length}</span><span>Pending Lab Requests</span></div>
      </div>

      <div className="sanad-quick-links">
        <Link className="sanad-btn sanad-btn-primary" to="/doctor/consultations">New Consultation</Link>
        <Link className="sanad-btn sanad-btn-secondary" to="/doctor/patients">View Patients</Link>
      </div>

      <section>
        <h2>Recent Consultations</h2>
        {recentConsultations.length === 0 ? (
          <p className="sanad-muted">No consultations recorded yet.</p>
        ) : (
          <ul className="sanad-list">
            {recentConsultations.map((c) => (
              <li key={c.id}>
                <strong>{c.patient_name}</strong> — {c.reason}
                <span className="sanad-muted"> ({new Date(c.date).toLocaleDateString()})</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
