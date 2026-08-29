import React, { useCallback } from 'react';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';

export default function MedicalRecord() {
  const fetchRecord = useCallback(async () => {
    const profile = await patientService.me();
    try {
      const record = await medicalService.getMedicalRecord(profile.id);
      return { profile, record };
    } catch (err) {
      if (err.apiStatus === 404) return { profile, record: null };
      throw err;
    }
  }, []);

  const { data, loading, error, refetch } = useApiData(fetchRecord, []);

  if (loading) return <LoadingSpinner fullPage label="Loading medical record..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { profile, record } = data;

  return (
    <div className="sanad-page">
      <h1>Medical Record</h1>

      <section className="sanad-card">
        <h2>Profile</h2>
        <div className="sanad-detail-grid">
          <div><label>Full Name</label><p>{profile.name}</p></div>
          <div><label>Date of Birth</label><p>{profile.birth_date || '—'}</p></div>
          <div><label>Age</label><p>{profile.age}</p></div>
          <div><label>Gender</label><p>{profile.gender || '—'}</p></div>
          <div><label>Blood Group</label><p>{profile.blood_group || '—'}</p></div>
          <div><label>Allergies</label><p>{profile.allergies || 'None recorded'}</p></div>
          <div><label>Chronic Diseases</label><p>{profile.chronic_diseases || 'None recorded'}</p></div>
        </div>
      </section>

      {!record ? (
        <EmptyState
          title="No medical record yet"
          message="Your medical record will be created automatically after your first consultation."
        />
      ) : (
        <>
          <section className="sanad-card">
            <h2>Consultations ({record.consultation_count})</h2>
            {record.consultations.length === 0 ? (
              <EmptyState title="No consultations yet" />
            ) : (
              <ul className="sanad-list">
                {record.consultations.map((c) => (
                  <li key={c.id}>
                    <strong>{c.reason}</strong> — Dr. {c.doctor_name}
                    <span className="sanad-muted"> ({new Date(c.date).toLocaleDateString()})</span>
                    {c.observations && <p className="sanad-muted">{c.observations}</p>}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="sanad-card">
            <h2>Prescriptions ({record.prescription_count})</h2>
            {record.prescriptions.length === 0 ? (
              <EmptyState title="No prescriptions yet" />
            ) : (
              <ul className="sanad-list">
                {record.prescriptions.map((p) => (
                  <li key={p.id}>
                    <strong>{p.medication}</strong> — {p.dosage}, {p.frequency}, {p.duration}
                    <span className={`sanad-tag sanad-tag-${p.pharmacy_status}`}>{p.pharmacy_status}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </div>
  );
}
