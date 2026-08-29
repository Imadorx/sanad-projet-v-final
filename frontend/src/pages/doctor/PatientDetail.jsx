import React, { useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import laboratoryService from '../../services/laboratoryService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';
import KpiChart from '../../components/KpiChart';

export default function DoctorPatientDetail() {
  const { patientId } = useParams();
  const id = parseInt(patientId, 10);

  const fetchData = useCallback(async () => {
    const [patient, consultations, prescriptions, labRequests, labResults] = await Promise.all([
      patientService.get(id),
      medicalService.listConsultations(id),
      medicalService.listPrescriptions(id),
      laboratoryService.listRequests({ patient_id: id }),
      laboratoryService.listResults({ patient_id: id }),
    ]);
    return { patient, consultations, prescriptions, labRequests, labResults };
  }, [id]);

  const { data, loading, error, refetch } = useApiData(fetchData, [id]);

  if (loading) return <LoadingSpinner fullPage label="Loading patient..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { patient, consultations, prescriptions, labRequests, labResults } = data;
  const analysisNames = [...new Set(labResults.map((r) => r.analysis_name))];

  return (
    <div className="sanad-page">
      <h1>{patient.name}</h1>
      <div className="sanad-quick-links">
        <Link className="sanad-btn sanad-btn-primary" to={`/doctor/consultations/new?patient_id=${id}`}>
          New Consultation
        </Link>
        <Link className="sanad-btn sanad-btn-secondary" to={`/doctor/prescriptions/new?patient_id=${id}`}>
          New Prescription
        </Link>
        <Link className="sanad-btn sanad-btn-secondary" to={`/doctor/lab-requests/new?patient_id=${id}`}>
          Request Lab Analysis
        </Link>
      </div>

      <section className="sanad-card">
        <h2>Profile</h2>
        <div className="sanad-detail-grid">
          <div><label>Age</label><p>{patient.age}</p></div>
          <div><label>Gender</label><p>{patient.gender || '—'}</p></div>
          <div><label>Blood Group</label><p>{patient.blood_group || '—'}</p></div>
          <div><label>Allergies</label><p>{patient.allergies || 'None recorded'}</p></div>
          <div><label>Chronic Diseases</label><p>{patient.chronic_diseases || 'None recorded'}</p></div>
        </div>
      </section>

      <section className="sanad-card">
        <h2>Consultation History</h2>
        {consultations.length === 0 ? (
          <EmptyState title="No consultations yet" />
        ) : (
          <ul className="sanad-list">
            {consultations.map((c) => (
              <li key={c.id}><strong>{c.reason}</strong> <span className="sanad-muted">({new Date(c.date).toLocaleDateString()})</span></li>
            ))}
          </ul>
        )}
      </section>

      <section className="sanad-card">
        <h2>Prescriptions</h2>
        {prescriptions.length === 0 ? (
          <EmptyState title="No prescriptions yet" />
        ) : (
          <ul className="sanad-list">
            {prescriptions.map((p) => (
              <li key={p.id}>{p.medication} — {p.dosage} <span className={`sanad-tag sanad-tag-${p.pharmacy_status}`}>{p.pharmacy_status}</span></li>
            ))}
          </ul>
        )}
      </section>

      <section className="sanad-card">
        <h2>Laboratory Evolution</h2>
        {analysisNames.length === 0 ? (
          <EmptyState title="No lab results yet" />
        ) : (
          <div className="sanad-kpi-grid">
            {analysisNames.map((name) => (
              <KpiChartLoader key={name} patientId={id} analysisName={name} />
            ))}
          </div>
        )}
      </section>

      <section className="sanad-card">
        <h2>Laboratory Requests</h2>
        {labRequests.length === 0 ? (
          <EmptyState title="No lab requests yet" />
        ) : (
          <ul className="sanad-list">
            {labRequests.map((r) => (
              <li key={r.id}>{r.analysis_type} — {r.laboratory_name} <span className={`sanad-tag sanad-tag-${r.status}`}>{r.status}</span></li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function KpiChartLoader({ patientId, analysisName }) {
  const fetchEvolution = useCallback(
    () => laboratoryService.getKpiEvolution(patientId, analysisName),
    [patientId, analysisName]
  );
  const { data: evolution, loading } = useApiData(fetchEvolution, [patientId, analysisName]);
  if (loading) return <LoadingSpinner label={`Loading ${analysisName}...`} />;
  return <KpiChart analysisName={analysisName} evolution={evolution} />;
}
