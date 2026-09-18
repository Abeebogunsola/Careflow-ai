import React, { useEffect, useState } from 'react';
import { Menu, Activity, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { getHealth } from '../../api';
import { HealthData } from '../../types';

interface HeaderProps {
  onMobileMenuToggle: () => void;
  title: string;
  subtitle?: string;
  actionButton?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({
  onMobileMenuToggle,
  title,
  subtitle,
  actionButton,
}) => {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    getHealth()
      .then((data) => {
        if (mounted) {
          setHealth(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setHealth(null);
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 30,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          onClick={onMobileMenuToggle}
          className="btn btn-ghost btn-sm"
          style={{ display: 'none' }}
          id="mobile-menu-btn"
          aria-label="Toggle menu"
        >
          <Menu size={20} />
        </button>

        <div>
          <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, color: 'var(--text-main)' }}>
            {title}
          </h2>
          {subtitle && (
            <p style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Synthetic Demo Banner */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--bg-subtle)',
            border: '1px solid var(--border-color)',
            fontSize: 'var(--font-size-xs)',
            color: 'var(--text-secondary)',
          }}
          title="All patient identifiers and records are synthetic demonstration data for evaluation."
        >
          <ShieldAlert size={14} style={{ color: 'var(--status-warning)' }} />
          <span>Synthetic Demo Data</span>
        </div>

        {/* Backend & DB Health Indicator */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: health?.database === 'ok' ? 'var(--status-success-bg)' : 'var(--status-warning-bg)',
            border: `1px solid ${health?.database === 'ok' ? 'var(--status-success-border)' : 'var(--status-warning-border)'}`,
            fontSize: 'var(--font-size-xs)',
            fontWeight: 600,
            color: health?.database === 'ok' ? 'var(--status-success)' : 'var(--status-warning)',
          }}
        >
          {loading ? (
            <>
              <Activity size={13} className="animate-spin" />
              <span>Connecting...</span>
            </>
          ) : health?.database === 'ok' ? (
            <>
              <CheckCircle2 size={13} />
              <span>API & DB Online</span>
            </>
          ) : (
            <>
              <Activity size={13} />
              <span>API Live (DB offline)</span>
            </>
          )}
        </div>

        {actionButton && <div>{actionButton}</div>}
      </div>

      <style>{`
        @media (max-width: 768px) {
          #mobile-menu-btn {
            display: inline-flex !important;
          }
        }
      `}</style>
    </header>
  );
};
