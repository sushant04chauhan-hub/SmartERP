import { useEffect, useState } from "react";

import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";

import {
  Bar,
  Doughnut,
  Line,
} from "react-chartjs-2";

import { getDashboardData } from "../services/api";

import "./DashboardPage.css";


ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
);


const currencyFormatter = new Intl.NumberFormat(
  "en-IN",
  {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  },
);


function formatCurrency(value) {
  return currencyFormatter.format(
    Number(value || 0),
  );
}


function formatForecastMonth(value) {
  if (!value) {
    return "N/A";
  }

  const date = new Date(
    `${value}T00:00:00`,
  );

  return date.toLocaleDateString(
    "en-IN",
    {
      month: "long",
      year: "numeric",
    },
  );
}


function DashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const data = await getDashboardData();

        setDashboard(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);


  if (loading) {
    return (
      <div className="dashboard-message">
        Loading dashboard analytics...
      </div>
    );
  }


  if (error) {
    return (
      <div className="dashboard-message dashboard-error">
        {error}
      </div>
    );
  }


  if (!dashboard) {
    return null;
  }


  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: "bottom",
      },
    },

    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };


  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        display: false,
      },
    },

    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };


  const horizontalBarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: "y",

    plugins: {
      legend: {
        display: false,
      },
    },

    scales: {
      x: {
        beginAtZero: true,
      },
    },
  };


  const supplierScoreOptions = {
    ...horizontalBarOptions,

    scales: {
      x: {
        beginAtZero: true,
        max: 100,
      },
    },
  };


  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>

          <p>
            SmartERP operational, financial and
            intelligent analytics overview.
          </p>
        </div>
      </div>


      <div className="dashboard-kpi-grid">
        <div className="dashboard-kpi">
          <span>Employees</span>
          <strong>
            {dashboard.employee_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Active Employees</span>
          <strong>
            {dashboard.active_employee_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Departments</span>
          <strong>
            {dashboard.department_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Products</span>
          <strong>
            {dashboard.product_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Low Stock</span>
          <strong>
            {dashboard.low_stock_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Inventory Value</span>
          <strong>
            {formatCurrency(
              dashboard.inventory_value,
            )}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Total Revenue</span>
          <strong>
            {formatCurrency(
              dashboard.total_revenue,
            )}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Paid Expenses</span>
          <strong>
            {formatCurrency(
              dashboard.total_paid_expenses,
            )}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Pending Finance Approvals</span>
          <strong>
            {dashboard.pending_expense_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Completed Sales</span>
          <strong>
            {dashboard.completed_sales_count}
          </strong>
        </div>

        <div className="dashboard-kpi">
          <span>Received Purchases</span>
          <strong>
            {dashboard.received_purchase_count}
          </strong>
        </div>

        <div className="dashboard-kpi dashboard-kpi-alert">
          <span>Expense Anomalies</span>
          <strong>
            {dashboard.expense_anomaly_count}
          </strong>
        </div>

        <div className="dashboard-kpi dashboard-kpi-warning">
          <span>Reorder Recommendations</span>
          <strong>
            {
              dashboard
                .reorder_recommendation_count
            }
          </strong>
        </div>
      </div>


      <div className="dashboard-section-title">
        <h2>Financial Analytics</h2>
      </div>


      <div className="dashboard-chart-grid">
        <div className="dashboard-card">
          <h3>Monthly Revenue</h3>

          <div className="dashboard-chart">
            <Line
              data={{
                labels:
                  dashboard
                    .revenue_chart_labels,

                datasets: [
                  {
                    label: "Revenue",
                    data:
                      dashboard
                        .revenue_chart_data,
                    borderColor: "#2563eb",
                    backgroundColor:
                      "rgba(37, 99, 235, 0.12)",
                    tension: 0.3,
                  },
                ],
              }}
              options={lineOptions}
            />
          </div>
        </div>


        <div className="dashboard-card">
          <h3>
            Revenue vs Paid Expenses
          </h3>

          <div className="dashboard-chart">
            <Line
              data={{
                labels:
                  dashboard
                    .finance_chart_labels,

                datasets: [
                  {
                    label: "Revenue",
                    data:
                      dashboard
                        .finance_revenue_data,
                    borderColor: "#2563eb",
                    tension: 0.3,
                  },

                  {
                    label: "Paid Expenses",
                    data:
                      dashboard
                        .finance_expense_data,
                    borderColor: "#dc2626",
                    tension: 0.3,
                  },
                ],
              }}
              options={lineOptions}
            />
          </div>
        </div>


        <div className="dashboard-card">
          <h3>Paid Expenses by Category</h3>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels:
                  dashboard
                    .expense_category_labels,

                datasets: [
                  {
                    label: "Paid Expenses",
                    data:
                      dashboard
                        .expense_category_data,
                    backgroundColor:
                      "#dc2626",
                  },
                ],
              }}
              options={horizontalBarOptions}
            />
          </div>
        </div>
      </div>


      <div className="dashboard-section-title">
        <h2>Sales & Procurement</h2>
      </div>


      <div className="dashboard-chart-grid">
        <div className="dashboard-card">
          <h3>Top Selling Products</h3>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels:
                  dashboard
                    .top_product_labels,

                datasets: [
                  {
                    label: "Units Sold",
                    data:
                      dashboard
                        .top_product_data,
                    backgroundColor:
                      "#2563eb",
                  },
                ],
              }}
              options={barOptions}
            />
          </div>
        </div>


        <div className="dashboard-card">
          <h3>Monthly Procurement Value</h3>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels:
                  dashboard
                    .procurement_chart_labels,

                datasets: [
                  {
                    label:
                      "Procurement Value",
                    data:
                      dashboard
                        .procurement_chart_data,
                    backgroundColor:
                      "#7c3aed",
                  },
                ],
              }}
              options={barOptions}
            />
          </div>
        </div>


        <div className="dashboard-card">
          <h3>
            Top Suppliers by Received Value
          </h3>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels:
                  dashboard
                    .top_supplier_labels,

                datasets: [
                  {
                    label: "Received Value",
                    data:
                      dashboard
                        .top_supplier_data,
                    backgroundColor:
                      "#0891b2",
                  },
                ],
              }}
              options={horizontalBarOptions}
            />
          </div>
        </div>
      </div>


      <div className="dashboard-section-title">
        <h2>Inventory Analytics</h2>
      </div>


      <div className="dashboard-chart-grid">
        <div className="dashboard-card">
          <h3>Inventory Stock Status</h3>

          <div className="dashboard-chart dashboard-chart-small">
            <Doughnut
              data={{
                labels:
                  dashboard
                    .inventory_status_labels,

                datasets: [
                  {
                    data:
                      dashboard
                        .inventory_status_data,

                    backgroundColor: [
                      "#16a34a",
                      "#f59e0b",
                      "#dc2626",
                    ],
                  },
                ],
              }}

              options={{
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                  legend: {
                    position: "bottom",
                  },
                },
              }}
            />
          </div>
        </div>


        <div className="dashboard-card">
          <h3>
            Demand Forecast
          </h3>

          <p className="dashboard-card-subtitle">
            Forecast month:{" "}
            {formatForecastMonth(
              dashboard.forecast_month,
            )}
          </p>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels:
                  dashboard
                    .forecast_chart_labels,

                datasets: [
                  {
                    label:
                      "Predicted Demand",
                    data:
                      dashboard
                        .forecast_chart_data,
                    backgroundColor:
                      "#2563eb",
                  },
                ],
              }}
              options={horizontalBarOptions}
            />
          </div>
        </div>


        <div className="dashboard-card">
          <h3>
            Supplier Performance Scores
          </h3>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels:
                  dashboard
                    .supplier_score_labels,

                datasets: [
                  {
                    label:
                      "Supplier Score",
                    data:
                      dashboard
                        .supplier_score_data,
                    backgroundColor:
                      "#16a34a",
                  },
                ],
              }}
              options={supplierScoreOptions}
            />
          </div>
        </div>
      </div>


      <div className="dashboard-section-title">
        <h2>Intelligent Insights</h2>
      </div>


      <div className="dashboard-insight-grid">
        <div className="dashboard-table-card">
          <div className="dashboard-table-header">
            <div>
              <h3>Demand Forecast Details</h3>

              <p>
                Predicted next-month product
                demand.
              </p>
            </div>
          </div>

          <div className="dashboard-table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Forecast</th>
                  <th>Method</th>
                </tr>
              </thead>

              <tbody>
                {dashboard
                  .demand_forecasts
                  .slice(0, 5)
                  .map((item) => (
                    <tr
                      key={item.product_code}
                    >
                      <td>
                        {item.product_name}
                      </td>

                      <td>
                        {
                          item
                            .predicted_demand
                        }
                      </td>

                      <td>
                        {item.method}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>


        <div className="dashboard-table-card">
          <div className="dashboard-table-header">
            <div>
              <h3>
                Expenses Needing Review
              </h3>

              <p>
                Statistical anomalies are
                unusual records and are not
                automatically incorrect or
                fraudulent.
              </p>
            </div>
          </div>

          <div className="dashboard-table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Expense</th>
                  <th>Category</th>
                  <th>Amount</th>
                  <th>Score</th>
                </tr>
              </thead>

              <tbody>
                {dashboard
                  .top_expense_anomalies
                  .length > 0 ? (
                  dashboard
                    .top_expense_anomalies
                    .map((item) => (
                      <tr
                        key={item.expense_id}
                      >
                        <td>
                          {item.title}
                        </td>

                        <td>
                          {
                            item
                              .category_label
                          }
                        </td>

                        <td>
                          {formatCurrency(
                            item.amount,
                          )}
                        </td>

                        <td>
                          {
                            item
                              .anomaly_score
                          }
                        </td>
                      </tr>
                    ))
                ) : (
                  <tr>
                    <td
                      colSpan="4"
                      className="dashboard-empty"
                    >
                      No anomalies detected.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>


        <div className="dashboard-table-card">
          <div className="dashboard-table-header">
            <div>
              <h3>
                Supplier Performance
              </h3>

              <p>
                Delivery, fulfillment and
                reliability scoring.
              </p>
            </div>
          </div>

          <div className="dashboard-table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Score</th>
                  <th>Rating</th>
                  <th>On-Time</th>
                </tr>
              </thead>

              <tbody>
                {dashboard
                  .supplier_scores
                  .slice(0, 5)
                  .map((supplier) => (
                    <tr
                      key={
                        supplier
                          .supplier_id
                      }
                    >
                      <td>
                        {
                          supplier
                            .supplier_name
                        }
                      </td>

                      <td>
                        {
                          supplier
                            .supplier_score
                        }
                      </td>

                      <td>
                        {supplier.rating}
                      </td>

                      <td>
                        {
                          supplier
                            .on_time_rate
                        }
                        %
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>


        <div className="dashboard-table-card">
          <div className="dashboard-table-header">
            <div>
              <h3>
                Reorder Recommendations
              </h3>

              <p>
                Forecast-aware inventory
                replenishment suggestions.
              </p>
            </div>
          </div>

          <div className="dashboard-table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Projected</th>
                  <th>Recommended</th>
                  <th>Urgency</th>
                </tr>
              </thead>

              <tbody>
                {dashboard
                  .top_reorder_recommendations
                  .length > 0 ? (
                  dashboard
                    .top_reorder_recommendations
                    .map((item) => (
                      <tr
                        key={item.product_code}
                      >
                        <td>
                          {
                            item
                              .product_name
                          }
                        </td>

                        <td>
                          {
                            item
                              .projected_stock
                          }
                        </td>

                        <td>
                          {
                            item
                              .recommended_quantity
                          }
                        </td>

                        <td>
                          <span
                            className={
                              `dashboard-urgency ` +
                              `dashboard-urgency-${item.urgency.toLowerCase()}`
                            }
                          >
                            {item.urgency}
                          </span>
                        </td>
                      </tr>
                    ))
                ) : (
                  <tr>
                    <td
                      colSpan="4"
                      className="dashboard-empty"
                    >
                      Current inventory levels
                      are sufficient for forecast
                      demand.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}


export default DashboardPage;