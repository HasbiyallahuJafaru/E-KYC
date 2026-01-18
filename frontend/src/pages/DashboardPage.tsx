import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Settings, 
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Search,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle
} from 'lucide-react';
import { useState } from 'react';
import { ScrollNavBar } from '@/components/ScrollNavBar';

export function DashboardPage() {
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data - replace with real API calls
  const stats = [
    { label: 'Total Verifications', value: '1,247', change: '+12.5%', trend: 'up' },
    { label: 'Success Rate', value: '94.2%', change: '+2.1%', trend: 'up' },
    { label: 'Avg Response Time', value: '18s', change: '-5.2%', trend: 'up' },
    { label: 'This Month', value: '₦1,247k', change: '+18.3%', trend: 'up' }
  ];

  const recentVerifications = [
    { id: 'VER-001234', type: 'Individual', customer: 'John Doe', status: 'Verified', risk: 'Low', date: '2 hours ago' },
    { id: 'VER-001233', type: 'Corporate', customer: 'ABC Ltd', status: 'Verified', risk: 'Medium', date: '3 hours ago' },
    { id: 'VER-001232', type: 'Individual', customer: 'Jane Smith', status: 'Failed', risk: 'High', date: '5 hours ago' },
    { id: 'VER-001231', type: 'Corporate', customer: 'XYZ Plc', status: 'Pending', risk: '-', date: '6 hours ago' },
    { id: 'VER-001230', type: 'Individual', customer: 'Mike Johnson', status: 'Verified', risk: 'Low', date: '1 day ago' }
  ];

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
            { icon: LayoutDashboard, label: 'Overview', id: 'overview' },
            { icon: Users, label: 'Verifications', id: 'verifications' },
            { icon: FileText, label: 'Reports', id: 'reports' },
            { icon: TrendingUp, label: 'Analytics', id: 'analytics' },
            { icon: Settings, label: 'Settings', id: 'settings' }
          ].map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
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
                  textAlign: 'left'
                }}
              >
                <Icon size={20} strokeWidth={isActive ? 2 : 1.5} />
                {item.label}
              </button>
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <Link to="/verify/individual" className="btn-primary" style={{ 
              width: '100%',
              fontSize: '0.875rem',
              padding: '0.75rem 1rem',
              justifyContent: 'center',
              textDecoration: 'none'
            }}>
              Individual Verification
            </Link>
            <Link to="/verify/corporate" className="btn-secondary" style={{ 
              width: '100%',
              fontSize: '0.875rem',
              padding: '0.75rem 1rem',
              justifyContent: 'center',
              textDecoration: 'none'
            }}>
              Corporate Verification
            </Link>
          </div>
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
        {/* Header */}
        <header style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem', color: '#0a0a0a' }}>
                Dashboard
              </h1>
              <p style={{ color: '#737373', fontSize: '0.9375rem' }}>
                Welcome back! Here's what's happening today.
              </p>
            </div>
            
            {/* Search */}
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ 
                position: 'absolute',
                left: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#a3a3a3'
              }} />
              <input 
                type="text"
                placeholder="Search verifications..."
                style={{
                  width: '320px',
                  padding: '0.75rem 1rem 0.75rem 3rem',
                  border: '1px solid #d0d7de',
                  borderRadius: '8px',
                  fontSize: '0.9375rem',
                  backgroundColor: 'white'
                }}
              />
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div style={{ 
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          {stats.map((stat, index) => (
            <div key={index} style={{
              backgroundColor: 'white',
              padding: '1.5rem',
              borderRadius: '12px',
              border: '1px solid #eaeaea',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.875rem', color: '#737373', fontWeight: '500' }}>
                  {stat.label}
                </div>
                <div style={{ 
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: stat.trend === 'up' ? '#10b981' : '#ef4444'
                }}>
                  {stat.trend === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                  {stat.change}
                </div>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: '700', color: '#0a0a0a' }}>
                {stat.value}
              </div>
            </div>
          ))}
        </div>

        {/* Recent Verifications Table */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          border: '1px solid #eaeaea',
          overflow: 'hidden',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)'
        }}>
          <div style={{ 
            padding: '1.5rem',
            borderBottom: '1px solid #eaeaea',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#0a0a0a' }}>
              Recent Verifications
            </h2>
            <button className="btn-secondary" style={{ 
              fontSize: '0.875rem',
              padding: '0.5rem 1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Download size={16} />
              Export
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#fafbfc', borderBottom: '1px solid #eaeaea' }}>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>ID</th>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>Type</th>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>Customer</th>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>Status</th>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>Risk</th>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>Date</th>
                  <th style={{ padding: '1rem 1.5rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: '#525252' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentVerifications.map((verification, index) => (
                  <tr key={verification.id} style={{ 
                    borderBottom: index < recentVerifications.length - 1 ? '1px solid #eaeaea' : 'none',
                    transition: 'background-color 0.15s ease'
                  }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#fafbfc'}
                     onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                    <td style={{ padding: '1rem 1.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#0070f3' }}>
                      {verification.id}
                    </td>
                    <td style={{ padding: '1rem 1.5rem', fontSize: '0.875rem', color: '#3c4043' }}>
                      {verification.type}
                    </td>
                    <td style={{ padding: '1rem 1.5rem', fontSize: '0.875rem', color: '#3c4043', fontWeight: '500' }}>
                      {verification.customer}
                    </td>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.375rem 0.75rem',
                        borderRadius: '6px',
                        fontSize: '0.8125rem',
                        fontWeight: '500',
                        backgroundColor: 
                          verification.status === 'Verified' ? '#f0fdf4' :
                          verification.status === 'Failed' ? '#fef2f2' : '#fef3c7',
                        color:
                          verification.status === 'Verified' ? '#15803d' :
                          verification.status === 'Failed' ? '#dc2626' : '#d97706'
                      }}>
                        {verification.status === 'Verified' && <CheckCircle size={14} />}
                        {verification.status === 'Failed' && <XCircle size={14} />}
                        {verification.status === 'Pending' && <Clock size={14} />}
                        {verification.status}
                      </div>
                    </td>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      {verification.risk !== '-' ? (
                        <div style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                          fontSize: '0.8125rem',
                          fontWeight: '500',
                          color:
                            verification.risk === 'Low' ? '#15803d' :
                            verification.risk === 'Medium' ? '#d97706' : '#dc2626'
                        }}>
                          <AlertCircle size={14} />
                          {verification.risk}
                        </div>
                      ) : (
                        <span style={{ color: '#a3a3a3', fontSize: '0.875rem' }}>-</span>
                      )}
                    </td>
                    <td style={{ padding: '1rem 1.5rem', fontSize: '0.875rem', color: '#737373' }}>
                      {verification.date}
                    </td>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      <button style={{
                        padding: '0.375rem 0.75rem',
                        fontSize: '0.8125rem',
                        color: '#0070f3',
                        backgroundColor: 'transparent',
                        border: '1px solid #d0d7de',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: '500',
                        transition: 'all 0.15s ease'
                      }}>
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid #eaeaea',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ fontSize: '0.875rem', color: '#737373' }}>
              Showing 1 to 5 of 1,247 verifications
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                border: '1px solid #d0d7de',
                backgroundColor: 'white',
                borderRadius: '6px',
                cursor: 'pointer',
                color: '#737373',
                fontWeight: '500'
              }}>
                Previous
              </button>
              <button className="btn-primary" style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem'
              }}>
                Next
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
