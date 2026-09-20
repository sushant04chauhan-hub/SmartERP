import { useEffect, useState } from "react";

import { getSalesOrders } from "../services/api";

import "./SalesPage.css";

function SalesPage() {
  const [salesOrders, setSalesOrders] = useState([]);
  const [salesOrderCount, setSalesOrderCount] = useState(0);

  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);

  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const [ordering, setOrdering] = useState("-order_date");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadSalesOrders() {
      try {
        setLoading(true);
        setError("");

        const data = await getSalesOrders(
          currentPage,
          searchQuery,
          ordering,
        );

        setSalesOrders(data.results);
        setSalesOrderCount(data.count);

        setHasNextPage(Boolean(data.next));
        setHasPreviousPage(Boolean(data.previous));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadSalesOrders();
  }, [
    currentPage,
    searchQuery,
    ordering,
  ]);

  function handleSearch(event) {
    event.preventDefault();

    setCurrentPage(1);
    setSearchQuery(searchInput.trim());
  }

  function handleClearSearch() {
    setSearchInput("");
    setSearchQuery("");
    setCurrentPage(1);
  }

  return (
    <div className="sales-page">
      <div className="sales-header">
        <h1>Sales</h1>

        <p className="sales-summary">
          Total Sales Orders:{" "}
          <strong>{salesOrderCount}</strong>
        </p>
      </div>

      <div className="sales-controls">
        <form
          className="sales-search"
          onSubmit={handleSearch}
        >
          <input
            type="text"
            value={searchInput}
            onChange={(event) =>
              setSearchInput(event.target.value)
            }
            placeholder="Search by order number, customer, status, or notes"
          />

          <button type="submit">
            Search
          </button>

          {searchQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
            >
              Clear
            </button>
          )}
        </form>

        <div className="sales-sort">
          <label htmlFor="sales-ordering">
            Sort by:
          </label>

          <select
            id="sales-ordering"
            value={ordering}
            onChange={(event) => {
              setOrdering(event.target.value);
              setCurrentPage(1);
            }}
          >
            <option value="-order_date">
              Order Date Newest
            </option>

            <option value="order_date">
              Order Date Oldest
            </option>

            <option value="order_number">
              Order Number A-Z
            </option>

            <option value="-order_number">
              Order Number Z-A
            </option>

            <option value="status">
              Status A-Z
            </option>

            <option value="-status">
              Status Z-A
            </option>

            <option value="-total_amount">
              Total Amount High-Low
            </option>

            <option value="total_amount">
              Total Amount Low-High
            </option>

            <option value="-completed_date">
              Completed Date Latest
            </option>

            <option value="completed_date">
              Completed Date Earliest
            </option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="sales-loading">
          Loading sales orders...
        </div>
      )}

      {error && (
        <div className="sales-error">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="sales-table-wrapper">
            <table className="sales-table">
              <thead>
                <tr>
                  <th>Order Number</th>
                  <th>Customer</th>
                  <th>Status</th>
                  <th>Order Date</th>
                  <th>Completed Date</th>
                  <th>Items</th>
                  <th>Total Amount</th>
                </tr>
              </thead>

              <tbody>
                {salesOrders.length > 0 ? (
                  salesOrders.map((order) => (
                    <tr key={order.id}>
                      <td>
                        {order.order_number}
                      </td>

                      <td>
                        {order.customer_name}
                      </td>

                      <td>
                        <span
                          className={
                            `sales-status ` +
                            `sales-status-${order.status.toLowerCase()}`
                          }
                        >
                          {order.status}
                        </span>
                      </td>

                      <td>
                        {order.order_date}
                      </td>

                      <td>
                        {order.completed_date || "-"}
                      </td>

                      <td>
                        {order.items.length}
                      </td>

                      <td>
                        ₹
                        {Number(
                          order.total_amount,
                        ).toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="7"
                      className="sales-empty"
                    >
                      No sales orders found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="sales-pagination">
            <button
              type="button"
              disabled={!hasPreviousPage}
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

export default SalesPage;