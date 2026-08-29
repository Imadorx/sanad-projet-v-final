import React, { useCallback } from 'react';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

const STATUS_LABEL = {
  pending: 'Pending', received: 'Received by Pharmacy',
  prepared: 'Prepared', completed: 'Completed',
};

export default function PatientPrescriptions() {
  const fetchData = useCallback(async () => {
    const profile = await patientService.me();
    return medicalService.listPrescriptions(profile.id);
  }, []);

  const { data: prescriptions, loading, error, refetch } = useApiData(fetchData, []);

  if (loading) return <LoadingSpinner fullPage label="Loading prescriptions..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!prescriptions.length) return <EmptyState title="No prescriptions" message="You have no prescriptions on record." />;

  return (
    <div className="sanad-page">
      <h1>My Prescriptions</h1>
      <table className="sanad-table">
        <thead>
          <tr>
            <th>Date</th><th>Medication</th><th>Dosage</th><th>Frequency</th>
            <th>Duration</th><th>Doctor</th><th>Status</th>
          </tr>
        </thead>
        <tbody>
          {prescriptions.map((p) => (
            <tr key={p.id}>
              <td>{new Date(p.date).toLocaleDateString()}</td>
              <td>{p.medication}</td>
              <td>{p.dosage}</td>
              <td>{p.frequency}</td>
              <td>{p.duration}</td>
              <td>Dr. {p.doctor_name}</td>
              <td><span className={`sanad-tag sanad-tag-${p.pharmacy_status}`}>{STATUS_LABEL[p.pharmacy_status]}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
