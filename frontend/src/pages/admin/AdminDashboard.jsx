import React, { useCallback } from 'react';
import { useAuth } from '../../auth/AuthContext';
import { useApiData } from '../../hooks/useApiData';
import patientService from '../../services/patientService';
import medicalService from '../../services/medicalService';
import laboratoryService from '../../services/laboratoryService';
import pharmacyService from '../../services/pharmacyService';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorState from '../../components/ErrorState';

/**
 * Admin sees platform-wide figures because admin's ir.rule grants full
 * (unrestricted) access on every model - the same /api/* endpoints used
 * by doctors/patients simply return the full dataset for an admin
 * caller, since the record rules (not the controller) decide scope.
 */
export default function AdminDashboard() {
  const { user } = useAuth();

  const fetchAll = useCallback(async () => {
    const [patients, consultations, prescriptions, labRequests, pharmacyQueue] = await Promise.all([
      patientService.list(),
      medicalService.listConsultations(),
      medicalService.listPrescriptions(),
      laboratoryService.listRequests(),
      pharmacyService.listPrescriptions(),
    ]);
    return { patients, consultations, prescriptions, labRequests, pharmacyQueue };
  }, []);

  const { data, loading, error, refetch } = useApiData(fetchAll, []);

  if (loading) return <LoadingSpinner fullPage label="Loading platform overview..." />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const { patients, consultations, prescriptions, labRequests, pharmacyQueue } = data;

  return (
    <div className="sanad-page">
      <h1>Welcome, {user.name}</h1>
      <div className="sanad-stat-grid">
        <div className="sanad-stat-card"><span className="sanad-stat-number">{patients.length}</span><span>Total Patients</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{consultations.length}</span><span>Consultations</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{prescriptions.length}</span><span>Prescriptions</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{labRequests.length}</span><span>Lab Requests</span></div>
        <div className="sanad-stat-card"><span className="sanad-stat-number">{pharmacyQueue.length}</span><span>Pharmacy Queue</span></div>
      </div>
      <p className="sanad-muted">
        For user creation, role assignment, and organization management (medical cabinets,
        laboratories, pharmacies), use the Odoo backend admin interface — see Users & Roles.
      </p>
    </div>
  );
}
