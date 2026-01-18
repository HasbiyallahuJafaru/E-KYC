/**
 * Corporate verification page
 */

import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Settings, 
  TrendingUp
} from 'lucide-react';
import { useState } from 'react';
import { CorporateVerificationForm } from '@/components/CorporateVerificationForm';
import { ScrollNavBar } from '@/components/ScrollNavBar';

export function CorporateVerificationPage() {
  const [activeTab, setActiveTab] = useState('verifications');

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#fafbfc' }}>
      <ScrollNavBar />
      {/* Sidebar */}
      <aside style={{
        width: '260px',
        backgroundColor: '#ffffff',
        borderRight: '1px solid #eaeaea',
        padding: '1.5rem 0',
        position: 'fixed',
        height: '100vh',
        overflowY: 'auto'
      }}>
        {/* Logo */}
        <div style={{ padding: '0 1.5rem', marginBottom: '2rem' }}>
          <div style={{ 
            fontWeight: '700',
            fontSize: '1.25rem',
            color: '#0a0a0a',
            letterSpacing: '-0.02em'
          }}>
            E-KYC Check
          </div>
        </div>

        {/* Navigation */}
        <nav>
          {[
            { icon: LayoutDashboard, label: 'Overview', id: 'overview', path: '/dashboard' },
            { icon: Users, label: 'Verifications', id: 'verifications', path: '/verify/individual' },
            { icon: FileText, label: 'Reports', id: 'reports', path: '/dashboard' },
            { icon: TrendingUp, label: 'Analytics', id: 'analytics', path: '/dashboard' },
            { icon: Settings, label: 'Settings', id: 'settings', path: '/dashboard' }
          ].map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <Link
                key={item.id}
                to={item.path}
                onClick={() => setActiveTab(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 1.5rem',
                  backgroundColor: isActive ? '#f0f9ff' : 'transparent',
                  color: isActive ? '#0070f3' : '#737373',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.9375rem',
                  fontWeight: isActive ? '600' : '500',
                  transition: 'all 0.15s ease',
                  borderLeft: isActive ? '3px solid #0070f3' : '3px solid transparent',
                  textDecoration: 'none'
                }}
              >
                <Icon size={20} strokeWidth={isActive ? 2 : 1.5} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Quick Actions */}
        <div style={{ padding: '0 1.5rem', marginTop: '2rem' }}>
          <div style={{ 
            fontSize: '0.75rem',
            fontWeight: '600',
            color: '#a3a3a3',
            marginBottom: '1rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Quick Actions
          </div>
          <Link to="/verify/individual" className="btn-primary" style={{ 
            width: '100%',
            fontSize: '0.875rem',
            padding: '0.75rem 1rem',
            justifyContent: 'center'
          }}>
            Individual Verification
          </Link>
        </div>

        {/* Back to Home */}
        <div style={{ padding: '0 1.5rem', marginTop: '2rem' }}>
          <Link to="/" style={{ 
            fontSize: '0.875rem',
            color: '#737373',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            ← Back to Home
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ marginLeft: '260px', flex: 1, padding: '2rem' }}>
        <CorporateVerificationForm />
      </main>
    </div>
  );
}
