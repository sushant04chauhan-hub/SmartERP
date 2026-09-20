import { useEffect, useState } from "react";

import { getProducts } from "../services/api";

import "./InventoryPage.css";

function InventoryPage() {
  const [products, setProducts] = useState([]);
  const [productCount, setProductCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [ordering, setOrdering] = useState("product_code");

  useEffect(() => {
    async function loadProducts() {
      try {
        const data = await getProducts(
          currentPage,
          searchQuery,
          ordering,
        );

        setProducts(data.results);
        setProductCount(data.count);
        setHasNextPage(Boolean(data.next));
        setHasPreviousPage(Boolean(data.previous));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
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
    <div className="inventory-page">
      <div className="inventory-header">
        <h1>Inventory</h1>

        <p className="inventory-summary">
          Total Products:{" "}
          <strong>{productCount}</strong>
        </p>
      </div>

      <form
        className="inventory-search"
        onSubmit={handleSearch}
      >
        <input
          type="text"
          value={searchInput}
          onChange={(event) =>
            setSearchInput(event.target.value)
          }
          placeholder="Search by code, name, or category"
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

      <div className="inventory-sort">
        <label htmlFor="product-ordering">
          Sort by:
        </label>

        <select
          id="product-ordering"
          value={ordering}
          onChange={(event) => {
            setOrdering(event.target.value);
            setCurrentPage(1);
          }}
        >
          <option value="product_code">
            Product Code A-Z
          </option>
        
          <option value="-product_code">
            Product Code Z-A
          </option>
        
          <option value="name">
            Product Name A-Z
          </option>
        
          <option value="-name">
            Product Name Z-A
          </option>
        
          <option value="category">
            Category A-Z
          </option>
        
          <option value="-category">
            Category Z-A
          </option>
        </select>
      </div>

      {loading && (
        <div className="inventory-loading">
          Loading products...
        </div>
      )}

      {error && (
        <div className="inventory-error">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="inventory-table-wrapper">
            <table className="inventory-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Stock</th>
                  <th>Status</th>
                  <th>Reorder Level</th>
                  <th>Safety Stock</th>
                  <th>Unit</th>
                </tr>
              </thead>

              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.product_code}</td>
                    <td>{product.name}</td>
                    <td>{product.category}</td>
                    <td>{product.quantity}</td>
                    <td>
                      <span
                        className={
                          product.quantity <= product.reorder_level
                            ? "stock-badge stock-badge-low"
                            : "stock-badge stock-badge-ok"
                        }
                      >
                        {product.quantity <= product.reorder_level
                          ? "Low Stock"
                          : "In Stock"}
                      </span>
                    </td>
                    <td>{product.reorder_level}</td>
                    <td>{product.safety_stock}</td>
                    <td>{product.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="inventory-pagination">
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

export default InventoryPage;