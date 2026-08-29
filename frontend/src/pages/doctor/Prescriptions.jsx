import React, { useCallback, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useApiData } from '../../hooks/useApiData';
import { useFormValidation, validators } from '../../hooks/useFormValidation';
import medicalService from '../../services/medicalService';
import patientService from '../../services/patientService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

export default function DoctorPrescriptions() {
  const [searchParams] = useSearchParams();
  const preselectedPatientId = searchParams.get('patient_id');
  const [showForm, setShowForm] = useState(Boolean(preselectedPatientId));
  const [submitError, setSubmitError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchData = useCallback(async () => {
    const [prescriptions, patients] = await Promise.all([
      medicalService.listPrescriptions(),
      patientService.list(),
    ]);
    return { prescriptions, patients };
  }, []);
  const { data, loading, error, refetch } = useApiData(fetchData, []);

  const { values, errors, setField, validate, reset } = useFormValidation(
    { patient_id: preselectedPatientId || '', medication: '', dosage: '', frequency: '', duration: '', instructions: '' },
    {
      patient_id: validators.required('Patient'),
      medication: validators.required('Medication'),
      dosage: validators.required('Dosage'),
      frequency: validators.required('Frequency'),
      duration: validators.required('Duration'),
    }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;
    setSubmitting(true);
    try {
      await medicalService.createPrescription({
        patient_id: parseInt(values.patient_id, 10),
        medication: values.medication,
        dosage: values.dosage,
        frequency: values.frequency,
        duration: values.duration,
        instructions: values.instructions,
      });
      reset();
      setShowForm(false);
      refetch();
    } catch (err) {
      setSubmitError(err.apiMessage || 'Failed to create prescription.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner fullPage label="Loading prescriptions..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  return (
    <div className="sanad-page">
      <div className="sanad-page-header">
        <h1>Prescriptions</h1>
        <button className="sanad-btn sanad-btn-primary" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancel' : 'New Prescription'}
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

          <div className="sanad-form-row">
            <div>
              <label>Medication</label>
              <input type="text" value={values.medication} onChange={(e) => setField('medication', e.target.value)} />
              {errors.medication && <span className="sanad-field-error">{errors.medication}</span>}
            </div>
            <div>
              <label>Dosage</label>
              <input type="text" placeholder="e.g. 500mg" value={values.dosage} onChange={(e) => setField('dosage', e.target.value)} />
              {errors.dosage && <span className="sanad-field-error">{errors.dosage}</span>}
            </div>
          </div>
          <div className="sanad-form-row">
            <div>
              <label>Frequency</label>
              <input type="text" placeholder="e.g. 3x daily" value={values.frequency} onChange={(e) => setField('frequency', e.target.value)} />
              {errors.frequency && <span className="sanad-field-error">{errors.frequency}</span>}
            </div>
            <div>
              <label>Duration</label>
              <input type="text" placeholder="e.g. 7 days" value={values.duration} onChange={(e) => setField('duration', e.target.value)} />
              {errors.duration && <span className="sanad-field-error">{errors.duration}</span>}
            </div>
          </div>

          <label>Instructions</label>
          <textarea value={values.instructions} onChange={(e) => setField('instructions', e.target.value)} />

          <button type="submit" className="sanad-btn sanad-btn-primary" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save Prescription'}
          </button>
        </form>
      )}

      {data.prescriptions.length === 0 ? (
        <EmptyState title="No prescriptions yet" />
      ) : (
        <table className="sanad-table">
          <thead><tr><th>Date</th><th>Patient</th><th>Medication</th><th>Status</th></tr></thead>
          <tbody>
            {data.prescriptions.map((p) => (
              <tr key={p.id}>
                <td>{new Date(p.date).toLocaleDateString()}</td>
                <td>{p.patient_name}</td>
                <td>{p.medication}</td>
                <td><span className={`sanad-tag sanad-tag-${p.pharmacy_status}`}>{p.pharmacy_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
