import { NavLink, Outlet } from "react-router-dom";

import "./MainLayout.css";

function MainLayout() {
  return (
    <div className="main-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>SmartERP</h2>
          <span>Management System</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/inventory"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Inventory
          </NavLink>

          <NavLink
            to="/procurement"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Procurement
          </NavLink>

          <NavLink
            to="/sales"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Sales
          </NavLink>

          <NavLink
            to="/finance"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Finance
          </NavLink>

          <NavLink
            to="/hr"
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            HR
          </NavLink>
        </nav>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div>
            <h1>SmartERP</h1>
            <p>Enterprise Resource Planning System</p>
          </div>

          <div className="topbar-user">
            <span>Account</span>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;