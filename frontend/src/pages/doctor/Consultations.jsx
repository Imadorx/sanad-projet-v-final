import React, { useCallback, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useApiData } from '../../hooks/useApiData';
import { useFormValidation, validators } from '../../hooks/useFormValidation';
import medicalService from '../../services/medicalService';
import patientService from '../../services/patientService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

export default function DoctorConsultations() {
  const [searchParams] = useSearchParams();
  const preselectedPatientId = searchParams.get('patient_id');
  const [showForm, setShowForm] = useState(Boolean(preselectedPatientId));
  const [submitError, setSubmitError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchData = useCallback(async () => {
    const [consultations, patients] = await Promise.all([
      medicalService.listConsultations(),
      patientService.list(),
    ]);
    return { consultations, patients };
  }, []);
  const { data, loading, error, refetch } = useApiData(fetchData, []);

  const { values, errors, setField, validate, reset } = useFormValidation(
    { patient_id: preselectedPatientId || '', reason: '', symptoms: '', observations: '' },
    {
      patient_id: validators.required('Patient'),
      reason: validators.required('Reason for visit'),
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      await medicalService.createConsultation({
        patient_id: parseInt(values.patient_id, 10),
        reason: values.reason,
        symptoms: values.symptoms,
        observations: values.observations,
      });
      reset();
      setShowForm(false);
      refetch();
    } catch (err) {
      setSubmitError(err.apiMessage || 'Failed to create consultation.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner fullPage label="Loading consultations..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div className="sanad-page">
      <div className="sanad-page-header">
        <h1>Consultations</h1>
        <button className="sanad-btn sanad-btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancel' : 'New Consultation'}
        </button>
      </div>

      {showForm && (
        <form className="sanad-card sanad-form" onSubmit={handleSubmit} noValidate>
          {submitError && <div className="sanad-alert sanad-alert-error">{submitError}</div>}

          <label>Patient</label>
          <select value={values.patient_id} onChange={(e) => setField('patient_id', e.target.value)}>
            <option value="">Select a patient...</option>
            {data.patients.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          {errors.patient_id && <span className="sanad-field-error">{errors.patient_id}</span>}

          <label>Reason for Visit</label>
          <input type="text" value={values.reason} onChange={(e) => setField('reason', e.target.value)} />
          {errors.reason && <span className="sanad-field-error">{errors.reason}</span>}

          <label>Symptoms</label>
          <textarea value={values.symptoms} onChange={(e) => setField('symptoms', e.target.value)} />

          <label>Observations / Clinical Notes</label>
          <textarea value={values.observations} onChange={(e) => setField('observations', e.target.value)} />

          <button type="submit" className="sanad-btn sanad-btn-primary" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save Consultation'}
          </button>
        </form>
      )}

      {data.consultations.length === 0 ? (
        <EmptyState title="No consultations yet" />
      ) : (
        <table className="sanad-table">
          <thead><tr><th>Date</th><th>Patient</th><th>Reason</th></tr></thead>
          <tbody>
            {data.consultations.map((c) => (
              <tr key={c.id}>
                <td>{new Date(c.date).toLocaleDateString()}</td>
                <td>{c.patient_name}</td>
                <td>{c.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
