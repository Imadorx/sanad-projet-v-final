import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Unauthorized from './pages/Unauthorized';

import PatientDashboard from './pages/patient/PatientDashboard';
import MedicalRecord from './pages/patient/MedicalRecord';
import PatientPrescriptions from './pages/patient/Prescriptions';
import PatientLabResults from './pages/patient/LabResults';
import PatientAiAssistant from './pages/patient/AiAssistant';
import PatientChat from './pages/patient/Chat';

import DoctorDashboard from './pages/doctor/DoctorDashboard';
import DoctorPatients from './pages/doctor/Patients';
import DoctorPatientDetail from './pages/doctor/PatientDetail';
import DoctorConsultations from './pages/doctor/Consultations';
import DoctorPrescriptions from './pages/doctor/Prescriptions';
import DoctorLabRequests from './pages/doctor/LabRequests';
import DoctorChat from './pages/doctor/Chat';

import LabDashboard from './pages/laboratory/LabDashboard';
import LabRequests from './pages/laboratory/Requests';
import LabChat from './pages/laboratory/Chat';

import PharmacyDashboard from './pages/pharmacy/PharmacyDashboard';
import PharmacyQueue from './pages/pharmacy/Queue';
import PharmacyChat from './pages/pharmacy/Chat';

import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/Users';

const ROLE_HOME = {
  admin: '/admin', doctor: '/doctor', patient: '/patient',
  laboratory: '/laboratory', pharmacy: '/pharmacy',
};

function HomeRedirect() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <Navigate to={ROLE_HOME[user.roles[0]] || '/login'} replace />;
}

function withLayout(element) {
  return <Layout>{element}</Layout>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />
          <Route path="/" element={<HomeRedirect />} />

          {/* Patient */}
          <Route path="/patient" element={<ProtectedRoute allowedRoles={['patient']}>{withLayout(<PatientDashboard />)}</ProtectedRoute>} />
          <Route path="/patient/records" element={<ProtectedRoute allowedRoles={['patient']}>{withLayout(<MedicalRecord />)}</ProtectedRoute>} />
          <Route path="/patient/prescriptions" element={<ProtectedRoute allowedRoles={['patient']}>{withLayout(<PatientPrescriptions />)}</ProtectedRoute>} />
          <Route path="/patient/lab-results" element={<ProtectedRoute allowedRoles={['patient']}>{withLayout(<PatientLabResults />)}</ProtectedRoute>} />
          <Route path="/patient/ai-assistant" element={<ProtectedRoute allowedRoles={['patient']}>{withLayout(<PatientAiAssistant />)}</ProtectedRoute>} />
          <Route path="/patient/chat" element={<ProtectedRoute allowedRoles={['patient']}>{withLayout(<PatientChat />)}</ProtectedRoute>} />

          {/* Doctor */}
          <Route path="/doctor" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorDashboard />)}</ProtectedRoute>} />
          <Route path="/doctor/patients" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorPatients />)}</ProtectedRoute>} />
          <Route path="/doctor/patients/:patientId" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorPatientDetail />)}</ProtectedRoute>} />
          <Route path="/doctor/consultations" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorConsultations />)}</ProtectedRoute>} />
          <Route path="/doctor/prescriptions" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorPrescriptions />)}</ProtectedRoute>} />
          <Route path="/doctor/lab-requests" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorLabRequests />)}</ProtectedRoute>} />
          <Route path="/doctor/chat" element={<ProtectedRoute allowedRoles={['doctor']}>{withLayout(<DoctorChat />)}</ProtectedRoute>} />

          {/* Laboratory */}
          <Route path="/laboratory" element={<ProtectedRoute allowedRoles={['laboratory']}>{withLayout(<LabDashboard />)}</ProtectedRoute>} />
          <Route path="/laboratory/requests" element={<ProtectedRoute allowedRoles={['laboratory']}>{withLayout(<LabRequests />)}</ProtectedRoute>} />
          <Route path="/laboratory/chat" element={<ProtectedRoute allowedRoles={['laboratory']}>{withLayout(<LabChat />)}</ProtectedRoute>} />

          {/* Pharmacy */}
          <Route path="/pharmacy" element={<ProtectedRoute allowedRoles={['pharmacy']}>{withLayout(<PharmacyDashboard />)}</ProtectedRoute>} />
          <Route path="/pharmacy/queue" element={<ProtectedRoute allowedRoles={['pharmacy']}>{withLayout(<PharmacyQueue />)}</ProtectedRoute>} />
          <Route path="/pharmacy/chat" element={<ProtectedRoute allowedRoles={['pharmacy']}>{withLayout(<PharmacyChat />)}</ProtectedRoute>} />

          {/* Admin */}
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin']}>{withLayout(<AdminDashboard />)}</ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute allowedRoles={['admin']}>{withLayout(<AdminUsers />)}</ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
