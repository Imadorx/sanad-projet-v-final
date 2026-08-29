import React, { useCallback, useState } from 'react';
import { useApiData } from '../../hooks/useApiData';
import pharmacyService from '../../services/pharmacyService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

const NEXT_ACTION = {
  pending: { action: 'receive', label: 'Mark Received' },
  received: { action: 'prepare', label: 'Mark Prepared' },
  prepared: { action: 'complete', label: 'Mark Completed' },
};

export default function PharmacyQueue() {
  const fetchData = useCallback(() => pharmacyService.listPrescriptions(), []);
  const { data: prescriptions, loading, error, refetch } = useApiData(fetchData, []);
  const [actionError, setActionError] = useState(null);

  const handleTransition = async (id, action) => {
    setActionError(null);
    try {
      await pharmacyService.transitionPrescription(id, action);
      refetch();
    } catch (err) {
      setActionError(err.apiMessage || 'Action failed.');
    }
  };

  if (loading) return <LoadingSpinner fullPage label="Loading queue..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!prescriptions.length) return <EmptyState title="No prescriptions" message="Prescriptions routed to your pharmacy will appear here." />;

  return (
    <div className="sanad-page">
      <h1>Prescriptions to Process</h1>
      {actionError && <div className="sanad-alert sanad-alert-error">{actionError}</div>}
      <table className="sanad-table">
        <thead><tr><th>Date</th><th>Patient</th><th>Medication</th><th>Dosage</th><th>Frequency</th><th>Duration</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {prescriptions.map((p) => {
            const next = NEXT_ACTION[p.pharmacy_status];
            return (
              <tr key={p.id}>
                <td>{new Date(p.date).toLocaleDateString()}</td>
                <td>{p.patient_name}</td>
                <td>{p.medication}</td>
                <td>{p.dosage}</td>
                <td>{p.frequency}</td>
                <td>{p.duration}</td>
                <td><span className={`sanad-tag sanad-tag-${p.pharmacy_status}`}>{p.pharmacy_status}</span></td>
                <td>
                  {next && (
                    <button className="sanad-btn sanad-btn-small" onClick={() => handleTransition(p.id, next.action)}>
                      {next.label}
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
