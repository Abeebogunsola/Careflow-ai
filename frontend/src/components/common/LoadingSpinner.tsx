import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading care data...',
  size = 32,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 20px',
        gap: '12px',
        color: 'var(--text-muted)',
      }}
    >
      <Loader2
        size={size}
        style={{
          color: 'var(--primary)',
          animation: 'spin 1s linear infinite',
        }}
      />
      {message && (
        <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 500 }}>
          {message}
        </span>
      )}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
