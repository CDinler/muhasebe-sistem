# Pages Migration Plan - Step by Step

## Migration Mapping

| # | Source | Destination | Status |
|---|--------|-------------|--------|
| 1 | CostCentersPage.tsx | domains/partners/cost_centers/pages/ | ✅ Copied |
| 2 | AccountsPage.tsx | domains/accounting/accounts/pages/ | ⏳ Next |
| 3 | TransactionsPage.tsx | domains/accounting/transactions/pages/ | ⏳ |
| 4 | TransactionDetailPage.tsx | domains/accounting/transactions/pages/ | ⏳ |
| 5 | NewTransactionPage.tsx | domains/accounting/transactions/pages/ | ⏳ |
| 6 | MuavinPage.tsx | domains/accounting/transactions/pages/ | ⏳ |
| 7 | EInvoicesPage.tsx | domains/invoicing/einvoices/pages/ | ⏳ |
| 8 | EInvoicesPage.compact.css | domains/invoicing/einvoices/styles/ | ⏳ |
| 9 | UnpaidInvoicesPage.tsx | domains/invoicing/einvoices/pages/ | ⏳ |
| 10 | ContactsPage.tsx | domains/partners/contacts/pages/ | ⏳ |
| 11 | PersonnelContractsPage.tsx | domains/personnel/contracts/pages/ | ⏳ |
| 12 | DraftContractsTab.tsx | domains/personnel/draft_contracts/pages/ | ⏳ |
| 13 | LucaBordroListPage.tsx | domains/personnel/payroll/pages/ | ⏳ |
| 14 | LucaBordroUploadPage.tsx | domains/personnel/payroll/pages/ | ⏳ |
| 15 | MonthlyRecordsListPage.tsx | domains/personnel/monthly-records/pages/ | ⏳ |
| 16 | MonthlyRecordsUploadPage.tsx | domains/personnel/monthly-records/pages/ | ⏳ |
| 17 | PuantajGridPage.tsx | domains/personnel/payroll/pages/ | ⏳ |
| 18 | PuantajPage.tsx | domains/personnel/payroll/pages/ | ⏳ |
| 19 | BordroCalculationPage.tsx | domains/personnel/payroll/pages/ | ⏳ |
| 20 | BordroCalculationPageGrouped.tsx | domains/personnel/payroll/pages/ | ⏳ |
| 21 | ReportsPage.tsx | domains/reporting/reports/pages/ | ⏳ |
| 22 | SystemConfigPage.tsx | domains/settings/config/pages/ | ⏳ |
| 23 | SettingsPage.tsx | domains/settings/config/pages/ | ⏳ |
| 24 | UsersPage.tsx | domains/settings/users/pages/ | ⏳ |
| -- | Dashboard.tsx | pages/ (stays) | ✅ Root page |
| -- | LoginPage.tsx | pages/ (stays) | ✅ Auth page |

## App.tsx Import Changes Required

Each migration will update App.tsx import from:
```tsx
import PageName from './pages/PageName';
```

To:
```tsx
import PageName from './domains/{domain}/{subdomain}/pages/PageName';
```

## Execution Steps

### Phase 1: Simple Pages (No complex dependencies)
- [x] Step 1: CostCentersPage → Already using domain hooks
- [ ] Step 2: AccountsPage → Already using domain hooks
- [ ] Step 3: LucaBordroListPage → Simple list
- [ ] Step 4: LucaBordroUploadPage → Simple upload
- [ ] Step 5: MonthlyRecordsListPage → Simple list
- [ ] Step 6: MonthlyRecordsUploadPage → Simple upload
- [ ] Step 7: SettingsPage → Simple settings
- [ ] Step 8: UsersPage → User management

### Phase 2: Medium Pages (Some dependencies)
- [ ] Step 9: TransactionsPage
- [ ] Step 10: TransactionDetailPage
- [ ] Step 11: PersonnelContractsPage
- [ ] Step 12: DraftContractsTab
- [ ] Step 13: PuantajPage
- [ ] Step 14: SystemConfigPage
- [ ] Step 15: ReportsPage

### Phase 3: Complex Pages (Many dependencies)
- [ ] Step 16: ContactsPage (1051 lines)
- [ ] Step 17: NewTransactionPage
- [ ] Step 18: MuavinPage
- [ ] Step 19: UnpaidInvoicesPage
- [ ] Step 20: BordroCalculationPage
- [ ] Step 21: PuantajGridPage (1439 lines)
- [ ] Step 22: BordroCalculationPageGrouped (1303 lines)

### Phase 4: Largest Page (Needs special care)
- [ ] Step 23: EInvoicesPage (2724 lines) + CSS file

## Testing After Each Step

After each page migration:
1. ✅ Check import path updated in App.tsx
2. ✅ Run `npm run build` to check TypeScript errors
3. ✅ Manually test the page route
4. ✅ Verify all functionality works
5. ✅ Commit: `git commit -m "migrate: move PageName to domain"`

## Rollback Strategy

If any step fails:
```bash
# Restore old import in App.tsx
git checkout App.tsx

# Remove migrated file
rm src/domains/{path}/pages/PageName.tsx
```
