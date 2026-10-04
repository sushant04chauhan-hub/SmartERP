import {
  useEffect,
  useState,
} from "react";

import { getAuditLogs } from "../services/api";

import "./AuditLogsPage.css";


function formatLabel(value) {
  if (!value) {
    return "—";
  }

  return value
    .replaceAll("_", " ")
    .replaceAll(".", " / ")
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


function AuditLogsPage() {
  const [logs, setLogs] =
    useState([]);

  const [logCount, setLogCount] =
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

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [forbidden, setForbidden] =
    useState(false);


  useEffect(() => {
    async function loadAuditLogs() {
      try {
        setLoading(true);
        setError("");
        setForbidden(false);

        const data = await getAuditLogs(
          currentPage,
          searchQuery,
          ordering,
        );

        setLogs(
          data.results || [],
        );

        setLogCount(
          data.count || 0,
        );

        setHasNextPage(
          Boolean(data.next),
        );

        setHasPreviousPage(
          Boolean(data.previous),
        );
      } catch (err) {
        if (err.status === 403) {
          setForbidden(true);
        } else {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    loadAuditLogs();
  }, [
    currentPage,
    searchQuery,
    ordering,
  ]);


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


  if (forbidden) {
    return (
      <div className="audit-page">
        <div className="audit-header">
          <h1>Audit Logs</h1>
        </div>

        <div className="audit-access-denied">
          <h2>Access Restricted</h2>

          <p>
            Audit history is available only
            to administrators and managers.
          </p>
        </div>
      </div>
    );
  }


  return (
    <div className="audit-page">
      <div className="audit-header">
        <div>
          <h1>Audit Logs</h1>

          <p>
            Read-only history of important
            actions performed across SmartERP.
          </p>
        </div>

        <div className="audit-count-card">
          <span>Total Records</span>

          <strong>
            {logCount}
          </strong>
        </div>
      </div>


      <div className="audit-controls">
        <form
          className="audit-search"
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
            placeholder="Search actor, action, module, entity or description"
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


        <div className="audit-sort">
          <label htmlFor="audit-ordering">
            Sort by:
          </label>

          <select
            id="audit-ordering"
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

            <option value="module">
              Module A-Z
            </option>

            <option value="action">
              Action A-Z
            </option>

            <option value="actor__username">
              Actor A-Z
            </option>
          </select>
        </div>
      </div>


      {loading && (
        <div className="audit-message">
          Loading audit history...
        </div>
      )}


      {error && (
        <div className="audit-message audit-error">
          {error}
        </div>
      )}


      {!loading
        && !error
        && logs.length === 0
        && (
          <div className="audit-empty">
            No audit records match the
            current filters.
          </div>
        )}


      {!loading
        && !error
        && logs.length > 0
        && (
          <>
            <div className="audit-table-wrapper">
              <table className="audit-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Actor</th>
                    <th>Action</th>
                    <th>Module</th>
                    <th>Entity</th>
                    <th>Description</th>
                    <th>Metadata</th>
                  </tr>
                </thead>

                <tbody>
                  {logs.map((log) => {
                    const hasMetadata =
                      log.metadata
                      && Object.keys(
                        log.metadata,
                      ).length > 0;

                    return (
                      <tr key={log.id}>
                        <td className="audit-time">
                          {formatDate(
                            log.created_at,
                          )}
                        </td>

                        <td>
                          {log.actor_username
                            || "System"}
                        </td>

                        <td>
                          <span
                            className={
                              `audit-action `
                              + `audit-action-${log.action.toLowerCase()}`
                            }
                          >
                            {formatLabel(
                              log.action,
                            )}
                          </span>
                        </td>

                        <td>
                          {formatLabel(
                            log.module,
                          )}
                        </td>

                        <td>
                          <div className="audit-entity">
                            <strong>
                              {log.entity_repr
                                || formatLabel(
                                  log.entity_type,
                                )}
                            </strong>

                            {log.entity_id && (
                              <span>
                                ID:{" "}
                                {
                                  log.entity_id
                                }
                              </span>
                            )}
                          </div>
                        </td>

                        <td className="audit-description">
                          {log.description
                            || "—"}
                        </td>

                        <td>
                          {hasMetadata ? (
                            <details className="audit-metadata">
                              <summary>
                                View
                              </summary>

                              <pre>
                                {JSON.stringify(
                                  log.metadata,
                                  null,
                                  2,
                                )}
                              </pre>
                            </details>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>


            <div className="audit-pagination">
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


export default AuditLogsPage;