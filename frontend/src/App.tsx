import { ConfigProvider } from 'antd';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import trTR from 'antd/locale/tr_TR';
import './styles/global.css';
import { AuthProvider } from './contexts/AuthContext';
import { queryClient } from './config/queryClient';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import AccountsPage from './pages/AccountsPage';
import TransactionsPage from './pages/TransactionsPage';
import TransactionDetailPage from './pages/TransactionDetailPage';
import NewTransactionPage from './pages/NewTransactionPage';
import ContactsPage from './pages/ContactsPage';
import CostCentersPage from './pages/CostCentersPage';
import ReportsPage from './pages/ReportsPage';
import MuavinPage from './pages/MuavinPage';
import EInvoicesPage from './pages/EInvoicesPage';
import UnpaidInvoicesPage from './pages/UnpaidInvoicesPage';
import InvoiceMatchingPage from './pages/InvoiceMatchingPage';
import SystemConfigPage from './pages/SystemConfigPage';
import LucaBordroPage from './pages/LucaBordroPage';
import LucaSicilPage from './pages/LucaSicilPage_v2';
import PersonnelContractsPage from './pages/PersonnelContractsPage';
import BordroCalculationPage from './pages/BordroCalculationPage';
import PersonnelPage from './pages/PersonnelPage';
import PuantajPage from './pages/PuantajPage';
import PuantajGridPage from './pages/PuantajGridPage';
// NEW: Domain-based personnel page
import { PersonnelPage as PersonnelPageV2 } from './domains/personnel/pages/PersonnelPage';

function App() {
  return (
    <ConfigProvider locale={trTR}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Dashboard />} />
                <Route path="accounts" element={<AccountsPage />} />
                <Route path="transactions" element={<TransactionsPage />} />
                <Route path="transactions/new" element={<NewTransactionPage />} />
                <Route path="transactions/:id" element={<TransactionDetailPage />} />
                <Route path="transactions/:id/edit" element={<NewTransactionPage />} />
                <Route path="contacts" element={<ContactsPage />} />
                <Route path="cost-centers" element={<CostCentersPage />} />
                <Route path="einvoices" element={<EInvoicesPage />} />
                <Route path="einvoices/unpaid" element={<UnpaidInvoicesPage />} />
                <Route path="invoice-matching" element={<InvoiceMatchingPage />} />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="muavin" element={<MuavinPage />} />
                <Route path="system-config" element={<SystemConfigPage />} />
                <Route path="luca-bordro" element={<LucaBordroPage />} />
                <Route path="luca-sicil" element={<LucaSicilPage />} />
                <Route path="personnel-contracts" element={<PersonnelContractsPage />} />
                <Route path="puantaj" element={<PuantajPage />} />
                <Route path="puantaj-grid" element={<PuantajGridPage />} />
                <Route path="bordro-calculation" element={<BordroCalculationPage />} />
                {/* NEW: Use domain-driven personnel page */}
                <Route path="personnel" element={<PersonnelPageV2 />} />
                <Route path="settings" element={<div>Ayarlar (Yakında)</div>} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </ConfigProvider>
  );
}

export default App;
