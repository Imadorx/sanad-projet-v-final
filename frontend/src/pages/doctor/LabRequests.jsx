import React, { useCallback, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useApiData } from '../../hooks/useApiData';
import { useFormValidation, validators } from '../../hooks/useFormValidation';
import laboratoryService from '../../services/laboratoryService';
import patientService from '../../services/patientService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

export default function DoctorLabRequests() {
  const [searchParams] = useSearchParams();
  const preselectedPatientId = searchParams.get('patient_id');
  const [showForm, setShowForm] = useState(Boolean(preselectedPatientId));
  const [submitError, setSubmitError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchData = useCallback(async () => {
    const [requests, patients] = await Promise.all([
      laboratoryService.listRequests(),
      patientService.list(),
    ]);
    return { requests, patients };
  }, []);
  const { data, loading, error, refetch } = useApiData(fetchData, []);

  const { values, errors, setField, validate, reset } = useFormValidation(
    { patient_id: preselectedPatientId || '', laboratory_id: '', analysis_type: '', instructions: '' },
    {
      patient_id: validators.required('Patient'),
      analysis_type: validators.required('Analysis type'),
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;
    if (!values.laboratory_id) {
      setSubmitError('Please select a laboratory (configured by an administrator).');
      return;
    }
    setSubmitting(true);
    try {
      const created = await laboratoryService.createRequest({
        patient_id: parseInt(values.patient_id, 10),
        laboratory_id: parseInt(values.laboratory_id, 10),
        analysis_type: values.analysis_type,
        instructions: values.instructions,
      });
      await laboratoryService.transitionRequest(created.id, 'send');
      reset();
      setShowForm(false);
      refetch();
    } catch (err) {
      setSubmitError(err.apiMessage || 'Failed to create laboratory request.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner fullPage label="Loading lab requests..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div className="sanad-page">
      <div className="sanad-page-header">
        <h1>Laboratory Requests</h1>
        <button className="sanad-btn sanad-btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancel' : 'New Request'}
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

          <label>Laboratory ID</label>
          <input type="number" placeholder="Laboratory record ID"
                 value={values.laboratory_id} onChange={(e) => setField('laboratory_id', e.target.value)} />
          <span className="sanad-hint">Ask your administrator for the laboratory ID, or select from the Odoo backend directory.</span>

          <label>Analysis Type</label>
          <input type="text" placeholder="e.g. Complete Blood Count"
                 value={values.analysis_type} onChange={(e) => setField('analysis_type', e.target.value)} />
          {errors.analysis_type && <span className="sanad-field-error">{errors.analysis_type}</span>}

          <label>Instructions</label>
          <textarea value={values.instructions} onChange={(e) => setField('instructions', e.target.value)} />

          <button type="submit" className="sanad-btn sanad-btn-primary" disabled={submitting}>
            {submitting ? 'Sending...' : 'Send Request'}
          </button>
        </form>
      )}

      {data.requests.length === 0 ? (
        <EmptyState title="No laboratory requests yet" />
      ) : (
        <table className="sanad-table">
          <thead><tr><th>Date</th><th>Patient</th><th>Analysis</th><th>Laboratory</th><th>Status</th></tr></thead>
          <tbody>
            {data.requests.map((r) => (
              <tr key={r.id}>
                <td>{new Date(r.date).toLocaleDateString()}</td>
                <td>{r.patient_name}</td>
                <td>{r.analysis_type}</td>
                <td>{r.laboratory_name}</td>
                <td><span className={`sanad-tag sanad-tag-${r.status}`}>{r.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
