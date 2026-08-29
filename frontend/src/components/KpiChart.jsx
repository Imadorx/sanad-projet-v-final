import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

/**
 * Renders the KPI evolution trend for a single analysis type (PRD 10.4:
 * "compare Analysis 1..N over time, e.g. Jan 120, Feb 115, Mar 105").
 * Data comes straight from /api/lab-results/kpi (backed by
 * sanad.lab.result.get_kpi_evolution on the model) - no synthetic data.
 */
export default function KpiChart({ analysisName, evolution }) {
  if (!evolution || evolution.length === 0) {
    return <p className="sanad-muted">Not enough history for {analysisName} yet.</p>;
  }
  const chartData = evolution.map((point) => ({
    date: new Date(point.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    value: point.value,
  }));
  const unit = evolution[0]?.unit || '';

  return (
    <div className="sanad-kpi-chart">
      <h4>{analysisName} {unit && `(${unit})`}</h4>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#0b6e4f" strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
