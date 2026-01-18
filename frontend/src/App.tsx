import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HomePage } from '@/pages/HomePage';
import { IndividualVerificationPage } from '@/pages/IndividualVerificationPage';
import { CorporateVerificationPage } from '@/pages/CorporateVerificationPage';
import { DashboardPage } from '@/pages/DashboardPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/verify/individual" element={<IndividualVerificationPage />} />
        <Route path="/verify/corporate" element={<CorporateVerificationPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
