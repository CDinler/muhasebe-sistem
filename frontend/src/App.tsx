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
import AccountsPage from './domains/accounting/accounts/pages/AccountsPage';
import TransactionsPage from './domains/accounting/transactions/pages/TransactionsPage';
import TransactionDetailPage from './domains/accounting/transactions/pages/TransactionDetailPage';
import NewTransactionPage from './domains/accounting/transactions/pages/NewTransactionPage';
import ContactsPage from './domains/partners/contacts/pages/ContactsPage';
import CostCentersPage from './domains/partners/cost_centers/pages/CostCentersPage';
import ReportsPage from './domains/reporting/reports/pages/ReportsPage';
import MuavinPage from './domains/accounting/transactions/pages/MuavinPage';
import EInvoicesPage from './domains/invoicing/einvoices/pages/EInvoicesPage';
import UnpaidInvoicesPage from './domains/invoicing/einvoices/pages/UnpaidInvoicesPage';
import SystemConfigPage from './domains/settings/config/pages/SystemConfigPage';
import LucaBordroUploadPage from './domains/personnel/payroll/pages/LucaBordroUploadPage';
import LucaBordroListPage from './domains/personnel/payroll/pages/LucaBordroListPage';
import MonthlyRecordsUploadPage from './domains/personnel/monthly-records/pages/MonthlyRecordsUploadPage';
import MonthlyRecordsListPage from './domains/personnel/monthly-records/pages/MonthlyRecordsListPage';
import PersonnelContractsPage from './domains/personnel/contracts/pages/PersonnelContractsPage';
import BordroCalculationPage from './domains/personnel/payroll/pages/BordroCalculationPage';
import BordroCalculationPageGrouped from './domains/personnel/payroll/pages/BordroCalculationPageGrouped';
import PuantajPage from './domains/personnel/payroll/pages/PuantajPage';
import PuantajGridPage from './domains/personnel/payroll/pages/PuantajGridPage';
import UsersPage from './domains/settings/users/pages/UsersPage';
import SettingsPage from './domains/settings/config/pages/SettingsPage';
// NEW: Domain-based personnel page
import { PersonnelPage as PersonnelPageV2 } from './domains/personnel/pages/PersonnelPage';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={trTR}>
        <BrowserRouter>
          <AuthProvider>
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

                <Route path="reports" element={<ReportsPage />} />
                <Route path="muavin" element={<MuavinPage />} />
                <Route path="system-config" element={<SystemConfigPage />} />
                <Route path="luca-bordro-upload" element={<LucaBordroUploadPage />} />
                <Route path="luca-bordro-list" element={<LucaBordroListPage />} />
                <Route path="monthly-records-upload" element={<MonthlyRecordsUploadPage />} />
                <Route path="monthly-records-list" element={<MonthlyRecordsListPage />} />
                <Route path="personnel-contracts" element={<PersonnelContractsPage />} />
                <Route path="puantaj" element={<PuantajPage />} />
                <Route path="puantaj-grid" element={<PuantajGridPage />} />
                <Route path="bordro-calculation" element={<BordroCalculationPageGrouped />} />
                <Route path="bordro-calculation-old" element={<BordroCalculationPage />} />
                {/* NEW: Use domain-driven personnel page */}
                <Route path="personnel" element={<PersonnelPageV2 />} />
                <Route path="users" element={<UsersPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
