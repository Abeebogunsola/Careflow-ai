import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  '/': {
    title: 'Dashboard',
    subtitle: 'Program overview, today’s activity, and care retention metrics',
  },
  '/clients': {
    title: 'Client Directory',
    subtitle: 'Manage client care retention, communication preferences, and profiles',
  },
  '/appointments': {
    title: 'Appointments',
    subtitle: 'Track clinical reviews, medication refills, and attendance history',
  },
  '/interactions': {
    title: 'Interactions History',
    subtitle: 'Communication audit ledger across Web, SMS, and WhatsApp channels',
  },
  '/followups': {
    title: 'Follow-Up Tasks',
    subtitle: 'Care navigation outreach tasks requiring staff action',
  },
  '/escalations': {
    title: 'Clinical & Support Escalations',
    subtitle: 'Human-review queue: AI routes sensitive or clinical situations to staff',
  },
  '/approved-information': {
    title: 'Approved Information',
    subtitle: 'Program-authorized education and clinic logistics content for AI reference',
  },
};

export const AppLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();

  const getPageMeta = (pathname: string) => {
    if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname];
    if (pathname.startsWith('/clients/')) {
      return {
        title: 'Client Profile & Care Record',
        subtitle: 'Care plan, communication channel, retention history, and support tasks',
      };
    }
    return {
      title: 'CareFlow AI',
      subtitle: 'HIV Care Retention & Support Platform',
    };
  };

  const currentMeta = getPageMeta(location.pathname);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100%' }}>
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Header
          onMobileMenuToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          title={currentMeta.title}
          subtitle={currentMeta.subtitle}
        />

        <main
          style={{
            flex: 1,
            padding: '28px',
            maxWidth: '1400px',
            width: '100%',
            margin: '0 auto',
          }}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
};
