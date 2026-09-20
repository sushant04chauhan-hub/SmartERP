import { useEffect, useState } from "react";

import {
  getDepartments,
  getEmployees,
} from "../services/api";

import "./HRPage.css";

function HRPage() {
  const [employees, setEmployees] = useState([]);
  const [employeeCount, setEmployeeCount] = useState(0);
  const [employeePage, setEmployeePage] = useState(1);
  const [employeeHasNext, setEmployeeHasNext] = useState(false);
  const [employeeHasPrevious, setEmployeeHasPrevious] = useState(false);

  const [employeeSearchInput, setEmployeeSearchInput] = useState("");
  const [employeeSearchQuery, setEmployeeSearchQuery] = useState("");

  const [employeeOrdering, setEmployeeOrdering] =
    useState("employee_id");

  const [employeeLoading, setEmployeeLoading] = useState(true);
  const [employeeError, setEmployeeError] = useState("");

  const [departments, setDepartments] = useState([]);
  const [departmentCount, setDepartmentCount] = useState(0);
  const [departmentPage, setDepartmentPage] = useState(1);
  const [departmentHasNext, setDepartmentHasNext] = useState(false);
  const [departmentHasPrevious, setDepartmentHasPrevious] =
    useState(false);

  const [departmentSearchInput, setDepartmentSearchInput] =
    useState("");
  const [departmentSearchQuery, setDepartmentSearchQuery] =
    useState("");

  const [departmentOrdering, setDepartmentOrdering] =
    useState("name");

  const [departmentLoading, setDepartmentLoading] = useState(true);
  const [departmentError, setDepartmentError] = useState("");

  useEffect(() => {
    async function loadEmployees() {
      try {
        setEmployeeLoading(true);
        setEmployeeError("");

        const data = await getEmployees(
          employeePage,
          employeeSearchQuery,
          employeeOrdering,
        );

        setEmployees(data.results);
        setEmployeeCount(data.count);
        setEmployeeHasNext(Boolean(data.next));
        setEmployeeHasPrevious(Boolean(data.previous));
      } catch (err) {
        setEmployeeError(err.message);
      } finally {
        setEmployeeLoading(false);
      }
    }

    loadEmployees();
  }, [
    employeePage,
    employeeSearchQuery,
    employeeOrdering,
  ]);

  useEffect(() => {
    async function loadDepartments() {
      try {
        setDepartmentLoading(true);
        setDepartmentError("");

        const data = await getDepartments(
          departmentPage,
          departmentSearchQuery,
          departmentOrdering,
        );

        setDepartments(data.results);
        setDepartmentCount(data.count);
        setDepartmentHasNext(Boolean(data.next));
        setDepartmentHasPrevious(Boolean(data.previous));
      } catch (err) {
        setDepartmentError(err.message);
      } finally {
        setDepartmentLoading(false);
      }
    }

    loadDepartments();
  }, [
    departmentPage,
    departmentSearchQuery,
    departmentOrdering,
  ]);

  function handleEmployeeSearch(event) {
    event.preventDefault();

    setEmployeePage(1);
    setEmployeeSearchQuery(
      employeeSearchInput.trim(),
    );
  }

  function handleEmployeeClear() {
    setEmployeeSearchInput("");
    setEmployeeSearchQuery("");
    setEmployeePage(1);
  }

  function handleDepartmentSearch(event) {
    event.preventDefault();

    setDepartmentPage(1);
    setDepartmentSearchQuery(
      departmentSearchInput.trim(),
    );
  }

  function handleDepartmentClear() {
    setDepartmentSearchInput("");
    setDepartmentSearchQuery("");
    setDepartmentPage(1);
  }

  return (
    <div className="hr-page">
      <div className="hr-header">
        <h1>Human Resources</h1>

        <p>
          Manage employees and organizational departments.
        </p>
      </div>

      <div className="hr-summary-grid">
        <div className="hr-summary-card">
          <span>Employees</span>
          <strong>{employeeCount}</strong>
        </div>

        <div className="hr-summary-card">
          <span>Departments</span>
          <strong>{departmentCount}</strong>
        </div>
      </div>

      <section className="hr-section">
        <div className="hr-section-header">
          <h2>Employees</h2>

          <p>
            Employee directory, department assignments,
            roles and employment information.
          </p>
        </div>

        <div className="hr-controls">
          <form
            className="hr-search"
            onSubmit={handleEmployeeSearch}
          >
            <input
              type="text"
              value={employeeSearchInput}
              onChange={(event) =>
                setEmployeeSearchInput(
                  event.target.value,
                )
              }
              placeholder="Search employees"
            />

            <button type="submit">
              Search
            </button>

            {employeeSearchQuery && (
              <button
                type="button"
                onClick={handleEmployeeClear}
              >
                Clear
              </button>
            )}
          </form>

          <div className="hr-sort">
            <label htmlFor="employee-ordering">
              Sort by:
            </label>

            <select
              id="employee-ordering"
              value={employeeOrdering}
              onChange={(event) => {
                setEmployeeOrdering(
                  event.target.value,
                );
                setEmployeePage(1);
              }}
            >
              <option value="employee_id">
                Employee ID A-Z
              </option>

              <option value="-employee_id">
                Employee ID Z-A
              </option>

              <option value="first_name">
                First Name A-Z
              </option>

              <option value="-first_name">
                First Name Z-A
              </option>

              <option value="last_name">
                Last Name A-Z
              </option>

              <option value="-joining_date">
                Joining Date Newest
              </option>

              <option value="joining_date">
                Joining Date Oldest
              </option>

              <option value="-salary">
                Salary High-Low
              </option>

              <option value="salary">
                Salary Low-High
              </option>

              <option value="status">
                Status A-Z
              </option>
            </select>
          </div>
        </div>

        {employeeLoading && (
          <div className="hr-loading">
            Loading employees...
          </div>
        )}

        {employeeError && (
          <div className="hr-error">
            {employeeError}
          </div>
        )}

        {!employeeLoading && !employeeError && (
          <>
            <div className="hr-table-wrapper">
              <table className="hr-table employee-table">
                <thead>
                  <tr>
                    <th>Employee ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Designation</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Joining Date</th>
                    <th>Status</th>
                    <th>Salary</th>
                  </tr>
                </thead>

                <tbody>
                  {employees.length > 0 ? (
                    employees.map((employee) => (
                      <tr key={employee.id}>
                        <td>
                          {employee.employee_id}
                        </td>

                        <td>
                          {employee.first_name}{" "}
                          {employee.last_name}
                        </td>

                        <td>
                          {employee.department_name ||
                            "-"}
                        </td>

                        <td>
                          {employee.designation ||
                            "-"}
                        </td>

                        <td>
                          {employee.email || "-"}
                        </td>

                        <td>
                          {employee.phone || "-"}
                        </td>

                        <td>
                          {employee.joining_date ||
                            "-"}
                        </td>

                        <td>
                          <span
                            className={
                              `hr-status ` +
                              `hr-status-${employee.status.toLowerCase()}`
                            }
                          >
                            {employee.status}
                          </span>
                        </td>

                        <td>
                          ₹
                          {Number(
                            employee.salary,
                          ).toLocaleString(
                            "en-IN",
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan="9"
                        className="hr-empty"
                      >
                        No employees found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="hr-pagination">
              <button
                type="button"
                disabled={!employeeHasPrevious}
                onClick={() =>
                  setEmployeePage(
                    (page) => page - 1,
                  )
                }
              >
                Previous
              </button>

              <span>
                Page {employeePage}
              </span>

              <button
                type="button"
                disabled={!employeeHasNext}
                onClick={() =>
                  setEmployeePage(
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

      <section className="hr-section">
        <div className="hr-section-header">
          <h2>Departments</h2>

          <p>
            Organizational departments registered in SmartERP.
          </p>
        </div>

        <div className="hr-controls">
          <form
            className="hr-search"
            onSubmit={handleDepartmentSearch}
          >
            <input
              type="text"
              value={departmentSearchInput}
              onChange={(event) =>
                setDepartmentSearchInput(
                  event.target.value,
                )
              }
              placeholder="Search departments"
            />

            <button type="submit">
              Search
            </button>

            {departmentSearchQuery && (
              <button
                type="button"
                onClick={handleDepartmentClear}
              >
                Clear
              </button>
            )}
          </form>

          <div className="hr-sort">
            <label htmlFor="department-ordering">
              Sort by:
            </label>

            <select
              id="department-ordering"
              value={departmentOrdering}
              onChange={(event) => {
                setDepartmentOrdering(
                  event.target.value,
                );
                setDepartmentPage(1);
              }}
            >
              <option value="name">
                Department A-Z
              </option>

              <option value="-name">
                Department Z-A
              </option>
            </select>
          </div>
        </div>

        {departmentLoading && (
          <div className="hr-loading">
            Loading departments...
          </div>
        )}

        {departmentError && (
          <div className="hr-error">
            {departmentError}
          </div>
        )}

        {!departmentLoading && !departmentError && (
          <>
            <div className="hr-table-wrapper">
              <table className="hr-table department-table">
                <thead>
                  <tr>
                    <th>Department</th>
                    <th>Description</th>
                  </tr>
                </thead>

                <tbody>
                  {departments.length > 0 ? (
                    departments.map((department) => (
                      <tr key={department.id}>
                        <td>
                          {department.name}
                        </td>

                        <td>
                          {department.description ||
                            "-"}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan="2"
                        className="hr-empty"
                      >
                        No departments found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="hr-pagination">
              <button
                type="button"
                disabled={!departmentHasPrevious}
                onClick={() =>
                  setDepartmentPage(
                    (page) => page - 1,
                  )
                }
              >
                Previous
              </button>

              <span>
                Page {departmentPage}
              </span>

              <button
                type="button"
                disabled={!departmentHasNext}
                onClick={() =>
                  setDepartmentPage(
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

export default HRPage;