import { useEffect, useState } from "react";

import {
  getExpenses,
  getRevenues,
} from "../services/api";

import "./FinancePage.css";

function FinancePage() {
  const [expenses, setExpenses] = useState([]);
  const [expenseCount, setExpenseCount] = useState(0);
  const [expensePage, setExpensePage] = useState(1);
  const [expenseHasNext, setExpenseHasNext] = useState(false);
  const [expenseHasPrevious, setExpenseHasPrevious] = useState(false);
  const [expenseSearchInput, setExpenseSearchInput] = useState("");
  const [expenseSearchQuery, setExpenseSearchQuery] = useState("");
  const [expenseOrdering, setExpenseOrdering] =
    useState("-expense_date");
  const [expenseLoading, setExpenseLoading] = useState(true);
  const [expenseError, setExpenseError] = useState("");

  const [revenues, setRevenues] = useState([]);
  const [revenueCount, setRevenueCount] = useState(0);
  const [revenuePage, setRevenuePage] = useState(1);
  const [revenueHasNext, setRevenueHasNext] = useState(false);
  const [revenueHasPrevious, setRevenueHasPrevious] = useState(false);
  const [revenueSearchInput, setRevenueSearchInput] = useState("");
  const [revenueSearchQuery, setRevenueSearchQuery] = useState("");
  const [revenueOrdering, setRevenueOrdering] =
    useState("-revenue_date");
  const [revenueLoading, setRevenueLoading] = useState(true);
  const [revenueError, setRevenueError] = useState("");

  useEffect(() => {
    async function loadExpenses() {
      try {
        setExpenseLoading(true);
        setExpenseError("");

        const data = await getExpenses(
          expensePage,
          expenseSearchQuery,
          expenseOrdering,
        );

        setExpenses(data.results);
        setExpenseCount(data.count);
        setExpenseHasNext(Boolean(data.next));
        setExpenseHasPrevious(Boolean(data.previous));
      } catch (err) {
        setExpenseError(err.message);
      } finally {
        setExpenseLoading(false);
      }
    }

    loadExpenses();
  }, [
    expensePage,
    expenseSearchQuery,
    expenseOrdering,
  ]);

  useEffect(() => {
    async function loadRevenues() {
      try {
        setRevenueLoading(true);
        setRevenueError("");

        const data = await getRevenues(
          revenuePage,
          revenueSearchQuery,
          revenueOrdering,
        );

        setRevenues(data.results);
        setRevenueCount(data.count);
        setRevenueHasNext(Boolean(data.next));
        setRevenueHasPrevious(Boolean(data.previous));
      } catch (err) {
        setRevenueError(err.message);
      } finally {
        setRevenueLoading(false);
      }
    }

    loadRevenues();
  }, [
    revenuePage,
    revenueSearchQuery,
    revenueOrdering,
  ]);

  function handleExpenseSearch(event) {
    event.preventDefault();

    setExpensePage(1);
    setExpenseSearchQuery(
      expenseSearchInput.trim(),
    );
  }

  function handleExpenseClear() {
    setExpenseSearchInput("");
    setExpenseSearchQuery("");
    setExpensePage(1);
  }

  function handleRevenueSearch(event) {
    event.preventDefault();

    setRevenuePage(1);
    setRevenueSearchQuery(
      revenueSearchInput.trim(),
    );
  }

  function handleRevenueClear() {
    setRevenueSearchInput("");
    setRevenueSearchQuery("");
    setRevenuePage(1);
  }

  return (
    <div className="finance-page">
      <div className="finance-header">
        <h1>Finance</h1>

        <p>
          Monitor expenses and revenue generated
          across SmartERP business workflows.
        </p>
      </div>

      <div className="finance-summary-grid">
        <div className="finance-summary-card">
          <span>Expense Records</span>
          <strong>{expenseCount}</strong>
        </div>

        <div className="finance-summary-card">
          <span>Revenue Records</span>
          <strong>{revenueCount}</strong>
        </div>
      </div>

      <section className="finance-section">
        <div className="finance-section-header">
          <div>
            <h2>Expenses</h2>

            <p>
              Procurement and operational expense records.
            </p>
          </div>
        </div>

        <div className="finance-controls">
          <form
            className="finance-search"
            onSubmit={handleExpenseSearch}
          >
            <input
              type="text"
              value={expenseSearchInput}
              onChange={(event) =>
                setExpenseSearchInput(
                  event.target.value,
                )
              }
              placeholder="Search expenses"
            />

            <button type="submit">
              Search
            </button>

            {expenseSearchQuery && (
              <button
                type="button"
                onClick={handleExpenseClear}
              >
                Clear
              </button>
            )}
          </form>

          <div className="finance-sort">
            <label htmlFor="expense-ordering">
              Sort by:
            </label>

            <select
              id="expense-ordering"
              value={expenseOrdering}
              onChange={(event) => {
                setExpenseOrdering(
                  event.target.value,
                );
                setExpensePage(1);
              }}
            >
              <option value="-expense_date">
                Expense Date Newest
              </option>

              <option value="expense_date">
                Expense Date Oldest
              </option>

              <option value="-amount">
                Amount High-Low
              </option>

              <option value="amount">
                Amount Low-High
              </option>

              <option value="title">
                Title A-Z
              </option>

              <option value="-title">
                Title Z-A
              </option>

              <option value="category">
                Category A-Z
              </option>

              <option value="status">
                Status A-Z
              </option>

              <option value="-paid_at">
                Paid Date Latest
              </option>
            </select>
          </div>
        </div>

        {expenseLoading && (
          <div className="finance-loading">
            Loading expenses...
          </div>
        )}

        {expenseError && (
          <div className="finance-error">
            {expenseError}
          </div>
        )}

        {!expenseLoading && !expenseError && (
          <>
            <div className="finance-table-wrapper">
              <table className="finance-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Source PO</th>
                    <th>Payment</th>
                    <th>Reference</th>
                    <th>Amount</th>
                  </tr>
                </thead>

                <tbody>
                  {expenses.length > 0 ? (
                    expenses.map((expense) => (
                      <tr key={expense.id}>
                        <td>
                          {expense.title}
                        </td>

                        <td>
                          {expense.category}
                        </td>

                        <td>
                          <span
                            className={
                              `finance-status ` +
                              `finance-status-${expense.status.toLowerCase()}`
                            }
                          >
                            {expense.status}
                          </span>
                        </td>

                        <td>
                          {expense.expense_date}
                        </td>

                        <td>
                          {expense.purchase_order_number ||
                            "-"}
                        </td>

                        <td>
                          {expense.payment_method ||
                            "-"}
                        </td>

                        <td>
                          {expense.reference_number ||
                            "-"}
                        </td>

                        <td>
                          ₹
                          {Number(
                            expense.amount,
                          ).toLocaleString(
                            "en-IN",
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan="8"
                        className="finance-empty"
                      >
                        No expenses found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="finance-pagination">
              <button
                type="button"
                disabled={!expenseHasPrevious}
                onClick={() =>
                  setExpensePage(
                    (page) => page - 1,
                  )
                }
              >
                Previous
              </button>

              <span>
                Page {expensePage}
              </span>

              <button
                type="button"
                disabled={!expenseHasNext}
                onClick={() =>
                  setExpensePage(
                    (page) => page + 1,
                  )
                }
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>

      <section className="finance-section">
        <div className="finance-section-header">
          <div>
            <h2>Revenue</h2>

            <p>
              Revenue generated from completed sales
              orders.
            </p>
          </div>
        </div>

        <div className="finance-controls">
          <form
            className="finance-search"
            onSubmit={handleRevenueSearch}
          >
            <input
              type="text"
              value={revenueSearchInput}
              onChange={(event) =>
                setRevenueSearchInput(
                  event.target.value,
                )
              }
              placeholder="Search by reference or sales order"
            />

            <button type="submit">
              Search
            </button>

            {revenueSearchQuery && (
              <button
                type="button"
                onClick={handleRevenueClear}
              >
                Clear
              </button>
            )}
          </form>

          <div className="finance-sort">
            <label htmlFor="revenue-ordering">
              Sort by:
            </label>

            <select
              id="revenue-ordering"
              value={revenueOrdering}
              onChange={(event) => {
                setRevenueOrdering(
                  event.target.value,
                );
                setRevenuePage(1);
              }}
            >
              <option value="-revenue_date">
                Revenue Date Newest
              </option>

              <option value="revenue_date">
                Revenue Date Oldest
              </option>

              <option value="-amount">
                Amount High-Low
              </option>

              <option value="amount">
                Amount Low-High
              </option>

              <option value="reference_number">
                Reference A-Z
              </option>

              <option value="-reference_number">
                Reference Z-A
              </option>

              <option value="-created_at">
                Created Latest
              </option>
            </select>
          </div>
        </div>

        {revenueLoading && (
          <div className="finance-loading">
            Loading revenue...
          </div>
        )}

        {revenueError && (
          <div className="finance-error">
            {revenueError}
          </div>
        )}

        {!revenueLoading && !revenueError && (
          <>
            <div className="finance-table-wrapper">
              <table className="finance-table">
                <thead>
                  <tr>
                    <th>Sales Order</th>
                    <th>Revenue Date</th>
                    <th>Reference</th>
                    <th>Created By</th>
                    <th>Amount</th>
                  </tr>
                </thead>

                <tbody>
                  {revenues.length > 0 ? (
                    revenues.map((revenue) => (
                      <tr key={revenue.id}>
                        <td>
                          {revenue.sales_order_number ||
                            "-"}
                        </td>

                        <td>
                          {revenue.revenue_date}
                        </td>

                        <td>
                          {revenue.reference_number ||
                            "-"}
                        </td>

                        <td>
                          {revenue.created_by_username ||
                            "-"}
                        </td>

                        <td>
                          ₹
                          {Number(
                            revenue.amount,
                          ).toLocaleString(
                            "en-IN",
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan="5"
                        className="finance-empty"
                      >
                        No revenue records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="finance-pagination">
              <button
                type="button"
                disabled={!revenueHasPrevious}
                onClick={() =>
                  setRevenuePage(
                    (page) => page - 1,
                  )
                }
              >
                Previous
              </button>

              <span>
                Page {revenuePage}
              </span>

              <button
                type="button"
                disabled={!revenueHasNext}
                onClick={() =>
                  setRevenuePage(
                    (page) => page + 1,
                  )
                }
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  );
}

export default FinancePage;