import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { HomePage } from '@/pages/HomePage';
import { IndividualVerificationPage } from '@/pages/IndividualVerificationPage';
import { CorporateVerificationPage } from '@/pages/CorporateVerificationPage';
import './App.css';

function DashboardLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  
  return (
    <div className="dashboard">
      <aside className="dashboard-sidebar">
        <h3>Verification</h3>
        <nav>
          <Link 
            to="/verify/individual" 
            className={location.pathname === '/verify/individual' ? 'active' : ''}
          >
            👤 Individual
          </Link>
          <Link 
            to="/verify/corporate"
            className={location.pathname === '/verify/corporate' ? 'active' : ''}
          >
            🏢 Corporate
          </Link>
        </nav>
      </aside>
      <div className="dashboard-content">
        {children}
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <Link to="/" className="logo">
              <span className="logo-icon">🔐</span>
              <span className="logo-text">E-KYC Check</span>
            </Link>
            <nav className="main-nav">
              <Link to="/verify/individual">Individual</Link>
              <Link to="/verify/corporate">Corporate</Link>
            </nav>
          </div>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route 
              path="/verify/individual" 
              element={
                <DashboardLayout>
                  <IndividualVerificationPage />
                </DashboardLayout>
              } 
            />
            <Route 
              path="/verify/corporate" 
              element={
                <DashboardLayout>
                  <CorporateVerificationPage />
                </DashboardLayout>
              } 
            />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>© 2026 E-KYC Check. All rights reserved.</p>
          <p className="footer-note">FATF/CBN Compliant KYC Verification Platform</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
