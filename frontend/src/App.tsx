import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { ClientsPage } from './pages/ClientsPage';
import { ClientDetailPage } from './pages/ClientDetailPage';
import { AppointmentsPage } from './pages/AppointmentsPage';
import { InteractionsPage } from './pages/InteractionsPage';
import { FollowUpsPage } from './pages/FollowUpsPage';
import { EscalationsPage } from './pages/EscalationsPage';
import { ApprovedInfoPage } from './pages/ApprovedInfoPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/clients/:id" element={<ClientDetailPage />} />
          <Route path="/appointments" element={<AppointmentsPage />} />
          <Route path="/interactions" element={<InteractionsPage />} />
          <Route path="/followups" element={<FollowUpsPage />} />
          <Route path="/escalations" element={<EscalationsPage />} />
          <Route path="/approved-information" element={<ApprovedInfoPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
