import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import laboratoryService from '../../services/laboratoryService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';

export default function PatientDashboard() {
  const { user } = useAuth();

  const fetchAll = useCallback(async () => {
    const profile = await patientService.me();
    const [consultations, prescriptions, labRequests] = await Promise.all([
      medicalService.listConsultations(profile.id),
      medicalService.listPrescriptions(profile.id),
      laboratoryService.listRequests({ patient_id: profile.id }),
    ]);
    return { profile, consultations, prescriptions, labRequests };
  }, []);

  const { data, loading, error, refetch } = useApiData(fetchAll, []);

  if (loading) return <LoadingSpinner fullPage label="Loading your dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { profile, consultations, prescriptions, labRequests } = data;

  return (
    <div className="sanad-page">
      <h1>Welcome, {user.name}</h1>
      <div className="sanad-stat-grid">
        <div className="sanad-stat-card">
          <span className="sanad-stat-number">{consultations.length}</span>
          <span>Consultations</span>
        </div>
        <div className="sanad-stat-card">
          <span className="sanad-stat-number">{prescriptions.length}</span>
          <span>Prescriptions</span>
        </div>
        <div className="sanad-stat-card">
          <span className="sanad-stat-number">{labRequests.length}</span>
          <span>Lab Requests</span>
        </div>
        <div className="sanad-stat-card">
          <span className="sanad-stat-number">{profile.doctor_ids.length}</span>
          <span>Treating Doctors</span>
        </div>
      </div>

      <div className="sanad-quick-links">
        <Link className="sanad-btn sanad-btn-primary" to="/patient/records">View Medical Record</Link>
        <Link className="sanad-btn sanad-btn-secondary" to="/patient/lab-results">View Lab Results</Link>
        <Link className="sanad-btn sanad-btn-secondary" to="/patient/chat">Message My Doctor</Link>
      </div>

      <section>
        <h2>Recent Consultations</h2>
        {consultations.length === 0 ? (
          <p className="sanad-muted">No consultations yet.</p>
        ) : (
          <ul className="sanad-list">
            {consultations.slice(0, 5).map((c) => (
              <li key={c.id}>
                <strong>{c.reason}</strong> — Dr. {c.doctor_name} ({new Date(c.date).toLocaleDateString()})
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
