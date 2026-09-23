# SmartERP

SmartERP is a full-stack Enterprise Resource Planning and analytics platform built to manage and connect core business operations including inventory, procurement, sales, finance, and human resources.

The project combines traditional ERP workflows with analytics and intelligent features such as demand forecasting, expense anomaly detection, supplier performance scoring, and inventory reorder recommendations.

---

## Overview

SmartERP is designed around connected business workflows rather than isolated modules.

For example:

- Receiving a purchase order automatically updates inventory and creates a finance expense.
- Completing a sales order reduces inventory and automatically records revenue.
- Inventory movements are recorded with complete stock history.
- Important business actions are recorded in an audit trail.
- Business events can generate persistent user notifications.

The system includes a Django REST API and a React frontend with responsive ERP dashboards and module-specific interfaces.

---

## Core Features

### Authentication & Role-Based Access Control

SmartERP supports authenticated access with role-based permissions.

Available roles include:

- Administrator
- Manager
- HR
- Inventory
- Procurement
- Sales
- Finance
- Employee

Django superusers have full system access.

---

### Inventory Management

- Product catalogue
- Product codes and categories
- Purchase and selling prices
- Current stock quantity
- Reorder levels
- Safety stock
- Stock movement tracking
- Purchase stock movements
- Sales stock movements
- Returns
- Adjustments
- Damaged stock
- Low-stock monitoring

Inventory updates are handled through transactional services to keep stock quantities consistent.

---

### Procurement Management

- Supplier management
- Purchase order creation
- Multi-item purchase orders
- Purchase approval workflow
- Order tracking
- Purchase receiving
- Purchase cancellation
- Automatic inventory updates
- Automatic finance expense creation

Purchase orders move through:

```text
DRAFT → APPROVED → ORDERED → RECEIVED
```

Orders can also be cancelled when allowed by the workflow.

---

### Sales Management

- Customer management
- Sales order creation
- Multi-item sales orders
- Selling-price integration
- Stock availability validation
- Sales confirmation
- Sales completion
- Sales cancellation
- Automatic inventory deduction
- Automatic revenue creation

Sales orders move through:

```text
DRAFT → CONFIRMED → COMPLETED
```

---

### Finance Management

#### Expenses

- Expense creation and editing
- Expense categories
- Pending approval workflow
- Approval and rejection
- Payment processing
- Payment-method tracking
- Expense references
- Reviewer tracking
- Payment timestamps
- Procurement-linked expenses

Expense workflow:

```text
PENDING → APPROVED → PAID
        ↘ REJECTED
```

#### Revenue

- Revenue records
- Automatic revenue generation from completed sales
- Sales-order linkage
- Revenue dates
- Reference tracking

---

### Human Resources

- Department management
- Employee management
- Employee IDs
- Designations
- Joining dates
- Salary information
- Employee status
- Department assignment

---

## Analytics Dashboard

SmartERP includes an analytics dashboard that provides operational and financial insights.

Dashboard metrics include:

- Total employees
- Active employees
- Departments
- Products
- Low-stock products
- Estimated inventory value
- Total revenue
- Paid expenses
- Pending finance approvals
- Completed sales orders
- Received purchase orders

Visual analytics include:

- Monthly revenue
- Revenue vs paid expenses
- Paid expenses by category
- Top-selling products
- Monthly procurement value
- Top suppliers by received purchase value
- Inventory stock status
- Demand forecasts
- Supplier performance scores

The React dashboard uses Chart.js for data visualization.

---

## Intelligent Features

### Demand Forecasting

SmartERP analyses historical product sales and estimates future product demand.

Forecast results can be used by the inventory system to support replenishment decisions.

---

### Reorder Recommendations

The reorder recommendation engine combines:

- Current stock
- Forecast demand
- Reorder level
- Safety stock

It calculates projected inventory and recommends replenishment quantities when necessary.

Recommendations can also be classified by urgency.

---

### Expense Anomaly Detection

The finance analytics module analyses expense records and identifies statistically unusual transactions that may require review.

An anomaly represents an unusual record and does not automatically mean that the transaction is incorrect or fraudulent.

---

### Supplier Performance Scoring

Suppliers are evaluated using several operational factors including:

- On-time delivery
- Delivery delays
- Cancellation rate
- Order fulfilment
- Data confidence

The resulting supplier score helps compare procurement performance.

---

## Audit Logging

Important ERP actions are recorded in a persistent audit trail.

Audit records contain information such as:

- Acting user
- Action performed
- ERP module
- Entity type
- Entity identifier
- Human-readable description
- Event metadata
- Timestamp

Examples of audited events include:

- Purchase approval
- Purchase receiving
- Purchase cancellation
- Sales confirmation
- Sales completion
- Sales cancellation
- Stock movements
- Expense approval
- Expense rejection
- Expense payment
- Automatic revenue and expense creation

Audit history is exposed through a protected read-only API for authorized administrators and managers.

---

## Persistent Notifications

SmartERP includes a persistent notification system for important ERP events.

Notifications support:

- Recipient-specific delivery
- Notification types
- Priority levels
- Read/unread state
- Read timestamps
- Related ERP entities
- Navigation targets
- Unread notification count
- Mark-as-read
- Mark-all-as-read

Workflow notifications include events such as:

- Purchase-order updates
- Finance review requests
- Recorded sales revenue
- Expense approval or rejection
- Low-stock alerts

Notifications are persisted in PostgreSQL rather than existing only temporarily in the browser.

---

## REST API

The backend exposes authenticated REST APIs using Django REST Framework.

Major API resources include:

```text
/api/status/
/api/dashboard/

/api/products/
/api/purchase-orders/
/api/sales-orders/

/api/expenses/
/api/revenues/

/api/departments/
/api/employees/

/api/demand-forecasts/
/api/expense-anomalies/
/api/supplier-scores/
/api/reorder-recommendations/

/api/audit-logs/

/api/notifications/
/api/notifications/unread-count/
/api/notifications/<id>/read/
/api/notifications/mark-all-read/
```

Major list APIs support features such as:

- Authentication
- Pagination
- Search
- Ordering
- Related-object serialization

---

## Frontend

The React frontend provides dedicated interfaces for:

- Dashboard
- Inventory
- Procurement
- Sales
- Finance
- Human Resources

Frontend features include:

- Responsive layout
- Sidebar navigation
- Search
- Sorting
- Pagination
- Loading states
- Error states
- Empty states
- Status indicators
- Analytics charts
- Real Django REST API data

---

## Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL

### Frontend

- React
- Vite
- JavaScript
- CSS
- Chart.js
- React Chart.js 2

### Engineering Practices

- REST API architecture
- Role-based access control
- Database transactions
- Row-level locking for critical workflows
- Service-layer business logic
- Automated testing
- Audit logging
- Persistent notifications
- Git and GitHub version control

---

## System Architecture

```text
                    ┌─────────────────────┐
                    │    React + Vite     │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │ Django REST         │
                    │ Framework API       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Business Services   Analytics       Authentication
              │             Services          + RBAC
              │                │
              └────────┬───────┘
                       ▼
                ┌───────────────┐
                │  PostgreSQL   │
                └───────────────┘
```

---

## Connected Business Workflow

One of the main goals of SmartERP is connecting ERP modules together.

### Procurement Flow

```text
Purchase Order
      ↓
Approval
      ↓
Ordered
      ↓
Received
      ↓
Inventory Stock Increase
      ↓
Finance Expense Created
      ↓
Finance Review
```

### Sales Flow

```text
Sales Order
     ↓
Confirmed
     ↓
Stock Validation
     ↓
Completed
     ↓
Inventory Stock Reduction
     ↓
Revenue Created
```

These operations use database transactions to reduce the possibility of partial business updates.

---

## Testing

The project contains automated Django tests covering:

- Authentication and permissions
- Inventory workflows
- Procurement workflows
- Sales workflows
- Finance workflows
- REST APIs
- Dashboard APIs
- Intelligent analytics
- Audit logging
- Audit workflow integration
- Notification APIs
- Notification workflow integration
- Invalid workflow transitions
- Duplicate-operation protection

Current verified backend test suite:

```text
162 tests passed
```

Frontend verification:

```bash
npm run lint
npm run build
```

Both currently complete successfully.

---

## Project Structure

```text
SmartERP/
│
├── accounts/          # Authentication, roles and dashboard
├── api/               # REST API layer
├── audit/             # Audit logging
├── finance/           # Expenses and revenue
├── hr/                # Employees and departments
├── inventory/         # Products and stock management
├── notifications/     # Persistent notifications
├── procurement/       # Suppliers and purchase orders
├── sales/             # Customers and sales orders
│
├── config/            # Django project configuration
│
├── frontend/
│   └── src/
│       ├── layouts/
│       ├── pages/
│       └── services/
│
├── manage.py
└── requirements.txt
```

---

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/sushant04chauhan-hub/SmartERP.git
cd SmartERP
```

### 2. Create a Python virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Configure the required database and environment settings used by the Django project.

### 5. Apply migrations

```powershell
python manage.py migrate
```

### 6. Create an administrator account

```powershell
python manage.py createsuperuser
```

### 7. Start Django

```powershell
python manage.py runserver 127.0.0.1:8000
```

### 8. Install frontend dependencies

Open another terminal:

```powershell
cd frontend
npm install
```

### 9. Start React

```powershell
npm run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173/
```

---

## Verification

Backend:

```powershell
python manage.py check
python manage.py test
```

Frontend:

```powershell
npm run lint
npm run build
```

Verified project state:

```text
Django system checks: Passed
Django tests: 162 / 162 Passed
React ESLint: Passed
React production build: Passed
```

---

## Author

**Sushant Chauhan**

Final-year B.Tech Computer Science Engineering student specializing in Data Science.

GitHub: `sushant04chauhan-hub`

---

SmartERP was developed as an end-to-end project to explore how enterprise modules, transactional workflows, REST APIs, analytics, and intelligent decision-support features can be integrated into one system.