import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import MainLayout from "./layouts/MainLayout";

import AuditLogsPage from "./pages/AuditLogsPage";
import DashboardPage from "./pages/DashboardPage";
import FinancePage from "./pages/FinancePage";
import HRPage from "./pages/HRPage";
import InventoryPage from "./pages/InventoryPage";
import NotificationsPage from "./pages/NotificationsPage";
import ProcurementPage from "./pages/ProcurementPage";
import SalesPage from "./pages/SalesPage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route
            path="/"
            element={<DashboardPage />}
          />

          <Route
            path="/inventory"
            element={<InventoryPage />}
          />

          <Route
            path="/procurement"
            element={<ProcurementPage />}
          />

          <Route
            path="/sales"
            element={<SalesPage />}
          />

          <Route
            path="/finance"
            element={<FinancePage />}
          />

          <Route
            path="/hr"
            element={<HRPage />}
          />

          <Route
            path="/notifications"
            element={<NotificationsPage />}
          />

          <Route
            path="/audit-logs"
            element={<AuditLogsPage />}
          />
        </Route>

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}


export default App;