import React, { useCallback, useState } from 'react';
import { useApiData } from '../../hooks/useApiData';
import { useFormValidation, validators } from '../../hooks/useFormValidation';
import laboratoryService from '../../services/laboratoryService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

const NEXT_ACTION = {
  sent: { action: 'accept', label: 'Accept' },
  accepted: { action: 'start_processing', label: 'Start Processing' },
  processing: { action: 'complete', label: 'Mark Completed' },
};

export default function LabRequests() {
  const fetchData = useCallback(() => laboratoryService.listRequests(), []);
  const { data: requests, loading, error, refetch } = useApiData(fetchData, []);
  const [actionError, setActionError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [resultForm, setResultForm] = useState(null);

  const handleTransition = async (id, action) => {
    setActionError(null);
    try {
      await laboratoryService.transitionRequest(id, action);
      refetch();
    } catch (err) {
      setActionError(err.apiMessage || 'Action failed.');
    }
  };

  if (loading) return <LoadingSpinner fullPage label="Loading requests..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!requests.length) return <EmptyState title="No requests" message="Analysis requests routed to your laboratory will appear here." />;

  return (
    <div className="sanad-page">
      <h1>Analysis Requests</h1>
      {actionError && <div className="sanad-alert sanad-alert-error">{actionError}</div>}
      <table className="sanad-table">
        <thead><tr><th>Date</th><th>Patient</th><th>Analysis</th><th>Doctor</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {requests.map((r) => {
            const next = NEXT_ACTION[r.status];
            return (
              <React.Fragment key={r.id}>
                <tr>
                  <td>{new Date(r.date).toLocaleDateString()}</td>
                  <td>{r.patient_name}</td>
                  <td>{r.analysis_type}</td>
                  <td>Dr. {r.doctor_name}</td>
                  <td><span className={`sanad-tag sanad-tag-${r.status}`}>{r.status}</span></td>
                  <td className="sanad-actions">
                    {next && (
                      <button className="sanad-btn sanad-btn-small" onClick={() => handleTransition(r.id, next.action)}>
                        {next.label}
                      </button>
                    )}
                    {r.status === 'processing' && (
                      <button className="sanad-btn sanad-btn-small sanad-btn-secondary"
                              onClick={() => setResultForm(resultForm === r.id ? null : r.id)}>
                        Upload Result
                      </button>
                    )}
                  </td>
                </tr>
                {resultForm === r.id && (
                  <tr>
                    <td colSpan={6}>
                      <ResultForm requestId={r.id} onDone={() => { setResultForm(null); refetch(); }} />
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function ResultForm({ requestId, onDone }) {
  const { values, errors, setField, validate } = useFormValidation(
    { analysis_name: '', result_value: '', unit: '', reference_range: '' },
    { analysis_name: validators.required('Analysis name'), result_value: validators.required('Result value') }
  );
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      await laboratoryService.createResult({
        request_id: requestId,
        analysis_name: values.analysis_name,
        result_value: parseFloat(values.result_value),
        unit: values.unit,
        reference_range: values.reference_range,
      });
      onDone();
    } catch (err) {
      setFormError(err.apiMessage || 'Failed to save result.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="sanad-form sanad-form-inline" onSubmit={handleSubmit} noValidate>
      {formError && <div className="sanad-alert sanad-alert-error">{formError}</div>}
      <input placeholder="Analysis name" value={values.analysis_name} onChange={(e) => setField('analysis_name', e.target.value)} />
      <input placeholder="Value" type="number" step="any" value={values.result_value} onChange={(e) => setField('result_value', e.target.value)} />
      <input placeholder="Unit" value={values.unit} onChange={(e) => setField('unit', e.target.value)} />
      <input placeholder="Reference range e.g. 70-100" value={values.reference_range} onChange={(e) => setField('reference_range', e.target.value)} />
      <button type="submit" className="sanad-btn sanad-btn-primary" disabled={submitting}>
        {submitting ? 'Saving...' : 'Save Result'}
      </button>
      {(errors.analysis_name || errors.result_value) && (
        <span className="sanad-field-error">Analysis name and value are required.</span>
      )}
    </form>
  );
}
