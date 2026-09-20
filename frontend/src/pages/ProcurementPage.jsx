import { useEffect, useState } from "react";

import { getPurchaseOrders } from "../services/api";
import "./ProcurementPage.css";

function ProcurementPage() {
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [purchaseOrderCount, setPurchaseOrderCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [ordering, setOrdering] = useState("-order_date");

  useEffect(() => {
    async function loadPurchaseOrders() {
      try {
        const data = await getPurchaseOrders(
          currentPage,
          searchQuery,
          ordering,
        );

        setPurchaseOrders(data.results);
        setPurchaseOrderCount(data.count);
        setHasNextPage(Boolean(data.next));
        setHasPreviousPage(Boolean(data.previous));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadPurchaseOrders();
  }, [currentPage, searchQuery, ordering]);

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
    <div className="procurement-page">
      <div className="procurement-header">
        <h1>Procurement</h1>

        <p className="procurement-summary">
          Total Purchase Orders:{" "}
          <strong>{purchaseOrderCount}</strong>
        </p>
      </div>

      {loading && (
        <div className="procurement-loading">
          Loading purchase orders...
        </div>
      )}

      {error && (
        <div className="procurement-error">
          {error}
        </div>
      )}

      <form
        className="procurement-search"
        onSubmit={handleSearch}
      >
        <input
          type="text"
          value={searchInput}
          onChange={(event) =>
            setSearchInput(event.target.value)
          }
          placeholder="Search by order number, supplier, or status"
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

      <div className="procurement-sort">
        <label htmlFor="purchase-ordering">
          Sort by:
        </label>
            
        <select
          id="purchase-ordering"
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
        
          <option value="expected_delivery_date">
            Expected Delivery Earliest
          </option>
        
          <option value="-expected_delivery_date">
            Expected Delivery Latest
          </option>
        </select>
      </div>

      {!loading && !error && (
        <>
          <div className="procurement-table-wrapper">
            <table className="procurement-table">
              <thead>
                <tr>
                  <th>Order Number</th>
                  <th>Supplier</th>
                  <th>Status</th>
                  <th>Order Date</th>
                  <th>Expected Delivery</th>
                  <th>Received Date</th>
                  <th>Items</th>
                  <th>Total Amount</th>
                </tr>
              </thead>
      
              <tbody>
                {purchaseOrders.map((order) => (
                  <tr key={order.id}>
                    <td>{order.order_number}</td>
                
                    <td>{order.supplier_name}</td>
                
                    <td>
                      <span
                        className={`procurement-status procurement-status-${order.status.toLowerCase()}`}
                      >
                        {order.status}
                      </span>
                    </td>
                
                    <td>{order.order_date}</td>
                
                    <td>
                      {order.expected_delivery_date || "-"}
                    </td>
                
                    <td>
                      {order.received_date || "-"}
                    </td>
                
                    <td>{order.items.length}</td>
                
                    <td>
                      ₹
                      {Number(
                        order.total_amount,
                      ).toLocaleString("en-IN")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
              
          <div className="procurement-pagination">
            <button
              type="button"
              disabled={!hasPreviousPage}
              onClick={() =>
                setCurrentPage((page) => page - 1)
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
                setCurrentPage((page) => page + 1)
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

export default ProcurementPage;