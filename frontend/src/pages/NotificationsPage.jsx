import {
  useCallback,
  useEffect,
  useState,
} from "react";

import { useNavigate } from "react-router-dom";

import {
  getNotificationUnreadCount,
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from "../services/api";

import "./NotificationsPage.css";


function formatLabel(value) {
  if (!value) {
    return "";
  }

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}


function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString(
    "en-IN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}


function NotificationsPage() {
  const navigate = useNavigate();

  const [notifications, setNotifications] =
    useState([]);

  const [notificationCount, setNotificationCount] =
    useState(0);

  const [unreadCount, setUnreadCount] =
    useState(0);

  const [currentPage, setCurrentPage] =
    useState(1);

  const [hasNextPage, setHasNextPage] =
    useState(false);

  const [
    hasPreviousPage,
    setHasPreviousPage,
  ] = useState(false);

  const [searchInput, setSearchInput] =
    useState("");

  const [searchQuery, setSearchQuery] =
    useState("");

  const [ordering, setOrdering] =
    useState("-created_at");

  const [unreadFilter, setUnreadFilter] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [
    actionLoadingId,
    setActionLoadingId,
  ] = useState(null);

  const [
    markAllLoading,
    setMarkAllLoading,
  ] = useState(false);


  const loadNotifications = useCallback(
    async () => {
      try {
        setLoading(true);
        setError("");

        const data = await getNotifications(
          currentPage,
          searchQuery,
          ordering,
          unreadFilter,
        );

        setNotifications(
          data.results || [],
        );

        setNotificationCount(
          data.count || 0,
        );

        setHasNextPage(
          Boolean(data.next),
        );

        setHasPreviousPage(
          Boolean(data.previous),
        );
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [
      currentPage,
      searchQuery,
      ordering,
      unreadFilter,
    ],
  );


  const refreshUnreadCount = useCallback(
    async () => {
      try {
        const data =
          await getNotificationUnreadCount();

        setUnreadCount(
          data.unread_count || 0,
        );
      } catch {
        setUnreadCount(0);
      }
    },
    [],
  );


    useEffect(() => {
      const timeoutId = window.setTimeout(() => {
        loadNotifications();
      }, 0);
  
      return () => {
        window.clearTimeout(timeoutId);
      };
    }, [loadNotifications]);
    
    
    useEffect(() => {
      const timeoutId = window.setTimeout(() => {
        refreshUnreadCount();
      }, 0);
  
      return () => {
        window.clearTimeout(timeoutId);
      };
    }, [refreshUnreadCount]);


  function notifyHeader() {
    window.dispatchEvent(
      new Event(
        "notifications-updated",
      ),
    );
  }


  function handleSearch(event) {
    event.preventDefault();

    setCurrentPage(1);

    setSearchQuery(
      searchInput.trim(),
    );
  }


  function handleClearSearch() {
    setSearchInput("");
    setSearchQuery("");
    setCurrentPage(1);
  }


  async function handleMarkRead(
    notification,
  ) {
    if (notification.is_read) {
      return;
    }

    try {
      setActionLoadingId(
        notification.id,
      );

      setError("");

      await markNotificationRead(
        notification.id,
      );

      notifyHeader();

      await Promise.all([
        loadNotifications(),
        refreshUnreadCount(),
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoadingId(null);
    }
  }


  async function handleOpen(
    notification,
  ) {
    try {
      setActionLoadingId(
        notification.id,
      );

      setError("");

      if (!notification.is_read) {
        await markNotificationRead(
          notification.id,
        );

        notifyHeader();
      }

      if (notification.target_url) {
        navigate(
          notification.target_url,
        );
      } else {
        await Promise.all([
          loadNotifications(),
          refreshUnreadCount(),
        ]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoadingId(null);
    }
  }


  async function handleMarkAllRead() {
    try {
      setMarkAllLoading(true);
      setError("");

      await markAllNotificationsRead();

      notifyHeader();

      await Promise.all([
        loadNotifications(),
        refreshUnreadCount(),
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setMarkAllLoading(false);
    }
  }


  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <div>
          <h1>Notifications</h1>

          <p>
            Review important ERP events,
            workflow updates and alerts.
          </p>
        </div>

        <button
          type="button"
          className="notifications-mark-all"
          onClick={handleMarkAllRead}
          disabled={
            markAllLoading
            || unreadCount === 0
          }
        >
          {markAllLoading
            ? "Updating..."
            : "Mark all as read"}
        </button>
      </div>


      <div className="notifications-summary-grid">
        <div className="notifications-summary-card">
          <span>
            Matching Notifications
          </span>

          <strong>
            {notificationCount}
          </strong>
        </div>

        <div className="notifications-summary-card notifications-unread-card">
          <span>Unread</span>

          <strong>
            {unreadCount}
          </strong>
        </div>
      </div>


      <div className="notifications-controls">
        <form
          className="notifications-search"
          onSubmit={handleSearch}
        >
          <input
            type="text"
            value={searchInput}
            onChange={(event) =>
              setSearchInput(
                event.target.value,
              )
            }
            placeholder="Search notifications"
          />

          <button type="submit">
            Search
          </button>

          {searchQuery && (
            <button
              type="button"
              onClick={
                handleClearSearch
              }
            >
              Clear
            </button>
          )}
        </form>


        <div className="notifications-filter-group">
          <div className="notifications-filter">
            <label htmlFor="notification-read-filter">
              Status:
            </label>

            <select
              id="notification-read-filter"
              value={unreadFilter}
              onChange={(event) => {
                setUnreadFilter(
                  event.target.value,
                );

                setCurrentPage(1);
              }}
            >
              <option value="">
                All
              </option>

              <option value="true">
                Unread
              </option>

              <option value="false">
                Read
              </option>
            </select>
          </div>


          <div className="notifications-filter">
            <label htmlFor="notification-ordering">
              Sort:
            </label>

            <select
              id="notification-ordering"
              value={ordering}
              onChange={(event) => {
                setOrdering(
                  event.target.value,
                );

                setCurrentPage(1);
              }}
            >
              <option value="-created_at">
                Newest First
              </option>

              <option value="created_at">
                Oldest First
              </option>

              <option value="is_read">
                Unread First
              </option>
            </select>
          </div>
        </div>
      </div>


      {loading && (
        <div className="notifications-message">
          Loading notifications...
        </div>
      )}


      {error && (
        <div className="notifications-message notifications-error">
          {error}
        </div>
      )}


      {!loading
        && !error
        && notifications.length === 0
        && (
          <div className="notifications-empty">
            <h3>
              No notifications found
            </h3>

            <p>
              There are no notifications
              matching the current filters.
            </p>
          </div>
        )}


      {!loading
        && !error
        && notifications.length > 0
        && (
          <>
            <div className="notifications-list">
              {notifications.map(
                (notification) => (
                  <article
                    key={
                      notification.id
                    }
                    className={
                      notification.is_read
                        ? "notification-item"
                        : (
                          "notification-item "
                          + "notification-item-unread"
                        )
                    }
                  >
                    <div className="notification-main">
                      <div className="notification-title-row">
                        <div>
                          <h3>
                            {
                              notification
                                .title
                            }
                          </h3>

                          <div className="notification-badges">
                            <span
                              className={
                                `notification-type `
                                + `notification-type-${notification.notification_type.toLowerCase()}`
                              }
                            >
                              {formatLabel(
                                notification
                                  .notification_type,
                              )}
                            </span>

                            <span
                              className={
                                `notification-priority `
                                + `notification-priority-${notification.priority.toLowerCase()}`
                              }
                            >
                              {formatLabel(
                                notification
                                  .priority,
                              )}
                            </span>

                            {!notification.is_read && (
                              <span className="notification-unread-label">
                                Unread
                              </span>
                            )}
                          </div>
                        </div>

                        <time>
                          {formatDate(
                            notification
                              .created_at,
                          )}
                        </time>
                      </div>


                      <p className="notification-message">
                        {
                          notification
                            .message
                        }
                      </p>


                      <div className="notification-meta">
                        {notification.module && (
                          <span>
                            Module:{" "}
                            <strong>
                              {formatLabel(
                                notification
                                  .module,
                              )}
                            </strong>
                          </span>
                        )}

                        {notification.entity_id && (
                          <span>
                            Entity ID:{" "}
                            <strong>
                              {
                                notification
                                  .entity_id
                              }
                            </strong>
                          </span>
                        )}
                      </div>
                    </div>


                    <div className="notification-actions">
                      {!notification.is_read && (
                        <button
                          type="button"
                          className="notification-secondary-button"
                          disabled={
                            actionLoadingId
                            === notification.id
                          }
                          onClick={() =>
                            handleMarkRead(
                              notification,
                            )
                          }
                        >
                          {actionLoadingId
                            === notification.id
                            ? "Updating..."
                            : "Mark as read"}
                        </button>
                      )}

                      {notification.target_url && (
                        <button
                          type="button"
                          className="notification-primary-button"
                          disabled={
                            actionLoadingId
                            === notification.id
                          }
                          onClick={() =>
                            handleOpen(
                              notification,
                            )
                          }
                        >
                          Open
                        </button>
                      )}
                    </div>
                  </article>
                ),
              )}
            </div>


            <div className="notifications-pagination">
              <button
                type="button"
                disabled={
                  !hasPreviousPage
                }
                onClick={() =>
                  setCurrentPage(
                    (page) => page - 1,
                  )
                }
              >
                Previous
              </button>

              <span>
                Page {currentPage}
              </span>

              <button
                type="button"
                disabled={!hasNextPage}
                onClick={() =>
                  setCurrentPage(
                    (page) => page + 1,
                  )
                }
              >
                Next
              </button>
            </div>
          </>
        )}
    </div>
  );
}


export default NotificationsPage;