import React, { useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

export default function DoctorPatients() {
  const fetchData = useCallback(() => patientService.list(), []);
  const { data: patients, loading, error, refetch } = useApiData(fetchData, []);

  if (loading) return <LoadingSpinner fullPage label="Loading patients..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!patients.length) {
    return <EmptyState title="No assigned patients"
      message="Patients you have an active care relationship with will appear here." />;
  }

  return (
    <div className="sanad-page">
      <h1>My Patients</h1>
      <table className="sanad-table">
        <thead><tr><th>Name</th><th>Age</th><th>Gender</th><th>Blood Group</th><th></th></tr></thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{p.age}</td>
              <td>{p.gender || '—'}</td>
              <td>{p.blood_group || '—'}</td>
              <td><Link className="sanad-btn sanad-btn-small" to={`/doctor/patients/${p.id}`}>View</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
