import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Calendar,
  MessageSquare,
  ClipboardList,
  AlertTriangle,
  BookOpen,
  HeartHandshake,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/clients', label: 'Clients', icon: Users },
  { path: '/appointments', label: 'Appointments', icon: Calendar },
  { path: '/interactions', label: 'Interactions', icon: MessageSquare },
  { path: '/followups', label: 'Follow-ups', icon: ClipboardList },
  { path: '/escalations', label: 'Escalations', icon: AlertTriangle },
  { path: '/approved-information', label: 'Approved Info', icon: BookOpen },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  return (
    <aside
      style={{
        width: collapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)',
        backgroundColor: 'var(--bg-sidebar)',
        color: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.2s ease',
        flexShrink: 0,
        position: 'sticky',
        top: 0,
        height: '100vh',
        zIndex: 40,
        borderRight: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          padding: collapsed ? '0' : '0 16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--primary-600)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              boxShadow: '0 2px 8px rgba(13, 148, 136, 0.4)',
            }}
          >
            <HeartHandshake size={22} />
          </div>

          {!collapsed && (
            <div>
              <h1 style={{ fontSize: '1.05rem', fontWeight: 700, letterSpacing: '-0.02em', color: '#ffffff' }}>
                CareFlow <span style={{ color: 'var(--primary-200)' }}>AI</span>
              </h1>
              <p style={{ fontSize: '0.68rem', color: '#94a3b8', lineHeight: 1.1 }}>
                HIV Care Retention Platform
              </p>
            </div>
          )}
        </div>

        {!collapsed && (
          <button
            onClick={onToggle}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: 'var(--radius-sm)',
            }}
            title="Collapse sidebar"
            aria-label="Collapse sidebar"
          >
            <ChevronLeft size={18} />
          </button>
        )}
      </div>

      {collapsed && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '8px 0' }}>
          <button
            onClick={onToggle}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              padding: '6px',
            }}
            title="Expand sidebar"
            aria-label="Expand sidebar"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}

      {/* Navigation Links */}
      <nav
        style={{
          flex: 1,
          padding: '16px 8px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          overflowY: 'auto',
        }}
      >
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: collapsed ? '12px 0' : '10px 14px',
                justifyContent: collapsed ? 'center' : 'flex-start',
                borderRadius: 'var(--radius-md)',
                color: isActive ? '#ffffff' : '#94a3b8',
                backgroundColor: isActive ? 'var(--bg-sidebar-active)' : 'transparent',
                fontWeight: isActive ? 600 : 500,
                fontSize: 'var(--font-size-sm)',
                transition: 'all 0.15s ease',
              })}
              title={collapsed ? item.label : undefined}
            >
              <Icon size={20} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Human Oversight & Privacy Tag */}
      {!collapsed && (
        <div
          style={{
            padding: '14px 16px',
            margin: '12px',
            backgroundColor: 'rgba(255, 255, 255, 0.04)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <ShieldCheck size={16} style={{ color: 'var(--primary-200)' }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#f8fafc' }}>
              Human Oversight
            </span>
          </div>
          <p style={{ fontSize: '0.68rem', color: '#94a3b8', lineHeight: 1.3 }}>
            AI assists; authorized healthcare staff retain full clinical authority.
          </p>
        </div>
      )}
    </aside>
  );
};
