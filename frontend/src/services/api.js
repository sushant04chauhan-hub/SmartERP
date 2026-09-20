async function apiRequest(url, errorMessage) {
  const response = await fetch(url, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(
      `${errorMessage} with status ${response.status}`,
    );
  }

  return response.json();
}

function buildListUrl(
  endpoint,
  page,
  search,
  ordering,
) {
  const params = new URLSearchParams({
    page: page.toString(),
    ordering,
  });

  if (search) {
    params.set("search", search);
  }

  return `${endpoint}?${params.toString()}`;
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