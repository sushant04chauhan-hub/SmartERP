import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  NavLink,
  Outlet,
} from "react-router-dom";

import {
  getApiStatus,
  getNotificationUnreadCount,
} from "../services/api";

import "./MainLayout.css";


function formatRole(role) {
  if (!role) {
    return "Account";
  }

  return role
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function navClassName({
  isActive,
}) {
  return isActive
    ? "nav-link active"
    : "nav-link";
}


function MainLayout() {
  const [account, setAccount] =
    useState(null);

  const [unreadCount, setUnreadCount] =
    useState(0);


  useEffect(() => {
    let active = true;

    async function loadHeaderData() {
      const [
        accountResult,
        notificationResult,
      ] = await Promise.allSettled([
        getApiStatus(),
        getNotificationUnreadCount(),
      ]);

      if (!active) {
        return;
      }

      if (
        accountResult.status
        === "fulfilled"
      ) {
        setAccount(
          accountResult.value,
        );
      }

      if (
        notificationResult.status
        === "fulfilled"
      ) {
        setUnreadCount(
          notificationResult
            .value
            .unread_count || 0,
        );
      }
    }

    loadHeaderData();

    return () => {
      active = false;
    };
  }, []);


  useEffect(() => {
    async function refreshUnreadCount() {
      try {
        const data =
          await getNotificationUnreadCount();

        setUnreadCount(
          data.unread_count || 0,
        );
      } catch {
        setUnreadCount(0);
      }
    }

    function handleNotificationsUpdated() {
      refreshUnreadCount();
    }

    window.addEventListener(
      "notifications-updated",
      handleNotificationsUpdated,
    );

    return () => {
      window.removeEventListener(
        "notifications-updated",
        handleNotificationsUpdated,
      );
    };
  }, []);


  const accountRole = (
    account?.is_superuser
      ? "Superuser"
      : formatRole(
        account?.role,
      )
  );


  return (
    <div className="main-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2>SmartERP</h2>

          <span>
            Management System
          </span>
        </div>


        <nav className="sidebar-nav">
          <NavLink
            to="/"
            end
            className={
              navClassName
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/inventory"
            className={
              navClassName
            }
          >
            Inventory
          </NavLink>

          <NavLink
            to="/procurement"
            className={
              navClassName
            }
          >
            Procurement
          </NavLink>

          <NavLink
            to="/sales"
            className={
              navClassName
            }
          >
            Sales
          </NavLink>

          <NavLink
            to="/finance"
            className={
              navClassName
            }
          >
            Finance
          </NavLink>

          <NavLink
            to="/hr"
            className={
              navClassName
            }
          >
            HR
          </NavLink>

          <NavLink
            to="/notifications"
            className={
              navClassName
            }
          >
            Notifications

            {unreadCount > 0 && (
              <span className="sidebar-notification-count">
                {unreadCount > 99
                  ? "99+"
                  : unreadCount}
              </span>
            )}
          </NavLink>

          {account?.can_view_audit_logs && (
            <NavLink
              to="/audit-logs"
              className={
                navClassName
              }
            >
              Audit Logs
            </NavLink>
          )}
        </nav>
      </aside>


      <div className="main-content">
        <header className="topbar">
          <div className="topbar-brand-copy">
            <h1>SmartERP</h1>

            <p>
              Enterprise Resource
              Planning System
            </p>
          </div>


          <div className="topbar-actions">
            <Link
              to="/notifications"
              className="topbar-notification-button"
              aria-label={
                unreadCount > 0
                  ? `${unreadCount} unread notifications`
                  : "Notifications"
              }
              title="Notifications"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"
                />

                <path
                  d="M13.73 21a2 2 0 0 1-3.46 0"
                />
              </svg>

              {unreadCount > 0 && (
                <span className="topbar-notification-badge">
                  {unreadCount > 99
                    ? "99+"
                    : unreadCount}
                </span>
              )}
            </Link>


            <div className="topbar-user">
              <div className="topbar-user-avatar">
                {account?.user
                  ? account.user
                    .charAt(0)
                    .toUpperCase()
                  : "A"}
              </div>

              <div className="topbar-user-details">
                <strong>
                  {account?.user
                    || "Account"}
                </strong>

                <span>
                  {accountRole}
                </span>
              </div>
            </div>
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