function getCookie(name) {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) =>
      row.startsWith(`${name}=`),
    );

  if (!cookieValue) {
    return null;
  }

  return decodeURIComponent(
    cookieValue.split("=")[1],
  );
}


async function apiRequest(
  url,
  errorMessage,
  options = {},
) {
  const method = (
    options.method || "GET"
  ).toUpperCase();

  const headers = {
    ...(options.headers || {}),
  };

  const safeMethods = [
    "GET",
    "HEAD",
    "OPTIONS",
    "TRACE",
  ];

  if (!safeMethods.includes(method)) {
    const csrfToken = getCookie(
      "csrftoken",
    );

    if (csrfToken) {
      headers["X-CSRFToken"] = (
        csrfToken
      );
    }
  }

  const response = await fetch(
    url,
    {
      ...options,
      method,
      headers,
      credentials: "include",
    },
  );

  if (!response.ok) {
    const error = new Error(
      `${errorMessage} with status ${response.status}`,
    );

    error.status = response.status;

    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}


function buildListUrl(
  endpoint,
  page,
  search,
  ordering,
  extraParams = {},
) {
  const params = new URLSearchParams({
    page: page.toString(),
    ordering,
  });

  if (search) {
    params.set(
      "search",
      search,
    );
  }

  Object.entries(
    extraParams,
  ).forEach(
    ([key, value]) => {
      if (
        value !== ""
        && value !== null
        && value !== undefined
      ) {
        params.set(
          key,
          value,
        );
      }
    },
  );

  return (
    `${endpoint}?${params.toString()}`
  );
}


export async function getApiStatus() {
  return apiRequest(
    "/api/status/",
    "API request failed",
  );
}


export async function getDashboardData() {
  return apiRequest(
    "/api/dashboard/",
    "Dashboard request failed",
  );
}


export async function getProducts(
  page = 1,
  search = "",
  ordering = "product_code",
) {
  return apiRequest(
    buildListUrl(
      "/api/products/",
      page,
      search,
      ordering,
    ),
    "Products request failed",
  );
}


export async function getPurchaseOrders(
  page = 1,
  search = "",
  ordering = "-order_date",
) {
  return apiRequest(
    buildListUrl(
      "/api/purchase-orders/",
      page,
      search,
      ordering,
    ),
    "Purchase orders request failed",
  );
}


export async function getSalesOrders(
  page = 1,
  search = "",
  ordering = "-order_date",
) {
  return apiRequest(
    buildListUrl(
      "/api/sales-orders/",
      page,
      search,
      ordering,
    ),
    "Sales orders request failed",
  );
}


export async function getExpenses(
  page = 1,
  search = "",
  ordering = "-expense_date",
) {
  return apiRequest(
    buildListUrl(
      "/api/expenses/",
      page,
      search,
      ordering,
    ),
    "Expenses request failed",
  );
}


export async function getRevenues(
  page = 1,
  search = "",
  ordering = "-revenue_date",
) {
  return apiRequest(
    buildListUrl(
      "/api/revenues/",
      page,
      search,
      ordering,
    ),
    "Revenues request failed",
  );
}


export async function getEmployees(
  page = 1,
  search = "",
  ordering = "employee_id",
) {
  return apiRequest(
    buildListUrl(
      "/api/employees/",
      page,
      search,
      ordering,
    ),
    "Employees request failed",
  );
}


export async function getDepartments(
  page = 1,
  search = "",
  ordering = "name",
) {
  return apiRequest(
    buildListUrl(
      "/api/departments/",
      page,
      search,
      ordering,
    ),
    "Departments request failed",
  );
}


export async function getNotifications(
  page = 1,
  search = "",
  ordering = "-created_at",
  unread = "",
) {
  return apiRequest(
    buildListUrl(
      "/api/notifications/",
      page,
      search,
      ordering,
      {
        unread,
      },
    ),
    "Notifications request failed",
  );
}


export async function getNotificationUnreadCount() {
  return apiRequest(
    "/api/notifications/unread-count/",
    "Unread notification count request failed",
  );
}


export async function markNotificationRead(
  notificationId,
) {
  return apiRequest(
    `/api/notifications/${notificationId}/read/`,
    "Mark notification read request failed",
    {
      method: "POST",
    },
  );
}


export async function markAllNotificationsRead() {
  return apiRequest(
    "/api/notifications/mark-all-read/",
    "Mark all notifications read request failed",
    {
      method: "POST",
    },
  );
}


export async function getAuditLogs(
  page = 1,
  search = "",
  ordering = "-created_at",
) {
  return apiRequest(
    buildListUrl(
      "/api/audit-logs/",
      page,
      search,
      ordering,
    ),
    "Audit logs request failed",
  );
}