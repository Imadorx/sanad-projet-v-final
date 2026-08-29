import React, { useCallback, useState, useEffect } from 'react';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import laboratoryService from '../../services/laboratoryService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';
import EmptyState from '../../components/EmptyState';
import KpiChart from '../../components/KpiChart';

export default function PatientLabResults() {
  const fetchData = useCallback(async () => {
    const profile = await patientService.me();
    const results = await laboratoryService.listResults({ patient_id: profile.id });
    return { profile, results };
  }, []);

  const { data, loading, error, refetch } = useApiData(fetchData, []);
  const [kpiSeries, setKpiSeries] = useState({});

  const analysisNames = data
    ? [...new Set(data.results.map((r) => r.analysis_name))]
    : [];

  useEffect(() => {
    if (!data) return;
    let cancelled = false;
    (async () => {
      const entries = await Promise.all(
        analysisNames.map(async (name) => {
          const evolution = await laboratoryService.getKpiEvolution(data.profile.id, name);
          return [name, evolution];
        })
      );
      if (!cancelled) setKpiSeries(Object.fromEntries(entries));
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  if (loading) return <LoadingSpinner fullPage label="Loading lab results..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;
  if (!data.results.length) {
    return <EmptyState title="No lab results" message="Your laboratory results will appear here once available." />;
  }

  return (
    <div className="sanad-page">
      <h1>Laboratory Results</h1>

      <section className="sanad-card">
        <h2>Evolution Over Time</h2>
        <div className="sanad-kpi-grid">
          {analysisNames.map((name) => (
            <KpiChart key={name} analysisName={name} evolution={kpiSeries[name] || []} />
          ))}
        </div>
      </section>

      <section className="sanad-card">
        <h2>All Results</h2>
        <table className="sanad-table">
          <thead>
            <tr><th>Date</th><th>Analysis</th><th>Value</th><th>Unit</th><th>Reference Range</th><th>Status</th></tr>
          </thead>
          <tbody>
            {data.results.map((r) => (
              <tr key={r.id} className={r.is_out_of_range ? 'sanad-row-alert' : ''}>
                <td>{new Date(r.date).toLocaleDateString()}</td>
                <td>{r.analysis_name}</td>
                <td>{r.result_value}</td>
                <td>{r.unit || '—'}</td>
                <td>{r.reference_range || '—'}</td>
                <td>{r.is_out_of_range ? 'Out of range' : 'Normal'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
