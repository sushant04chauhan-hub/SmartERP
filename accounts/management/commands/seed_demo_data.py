from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from finance.models import Expense, Revenue
from hr.models import Department, Employee
from inventory.models import Product, StockMovement
from procurement.models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Supplier,
)

from sales.models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
)


class Command(BaseCommand):

    help = "Create realistic historical demo data for SmartERP."

    def add_arguments(self, parser):

        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm that demo data should be created.",
        )

    def historical_datetime(self, value, hour=12):

        return timezone.make_aware(
            datetime.combine(
                value,
                time(hour=hour),
            )
        )

    def seed_departments(self):

        departments = [
            {
                "name": "Engineering",
                "description": (
                    "Software development, systems, and technical operations."
                ),
            },
            {
                "name": "Sales",
                "description": (
                    "Customer acquisition, sales operations, and account management."
                ),
            },
            {
                "name": "Procurement",
                "description": (
                    "Supplier management, purchasing, and procurement operations."
                ),
            },
            {
                "name": "Finance",
                "description": (
                    "Accounting, expense management, payments, and financial operations."
                ),
            },
            {
                "name": "Human Resources",
                "description": (
                    "Employee management, recruitment, and people operations."
                ),
            },
        ]

        created_count = 0

        for department_data in departments:

            _, created = Department.objects.update_or_create(
                name=department_data["name"],
                defaults={
                    "description": department_data["description"],
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Departments ready: "
                f"{len(departments)} total, "
                f"{created_count} created."
            )
        )

    def seed_employees(self):

        employees = [
            {
                "employee_id": "EMP001",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "email": "aarav.sharma@smarterp.demo",
                "phone": "9876501001",
                "department": "Engineering",
                "designation": "Software Engineer",
                "joining_date": date(2024, 7, 15),
                "salary": Decimal("65000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP002",
                "first_name": "Ishita",
                "last_name": "Verma",
                "email": "ishita.verma@smarterp.demo",
                "phone": "9876501002",
                "department": "Engineering",
                "designation": "Data Analyst",
                "joining_date": date(2025, 1, 10),
                "salary": Decimal("58000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP003",
                "first_name": "Rohan",
                "last_name": "Mehta",
                "email": "rohan.mehta@smarterp.demo",
                "phone": "9876501003",
                "department": "Sales",
                "designation": "Sales Executive",
                "joining_date": date(2024, 9, 2),
                "salary": Decimal("48000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP004",
                "first_name": "Neha",
                "last_name": "Kapoor",
                "email": "neha.kapoor@smarterp.demo",
                "phone": "9876501004",
                "department": "Sales",
                "designation": "Account Manager",
                "joining_date": date(2023, 11, 20),
                "salary": Decimal("62000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP005",
                "first_name": "Karan",
                "last_name": "Singh",
                "email": "karan.singh@smarterp.demo",
                "phone": "9876501005",
                "department": "Procurement",
                "designation": "Procurement Executive",
                "joining_date": date(2024, 3, 18),
                "salary": Decimal("52000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP006",
                "first_name": "Priya",
                "last_name": "Nair",
                "email": "priya.nair@smarterp.demo",
                "phone": "9876501006",
                "department": "Procurement",
                "designation": "Supplier Coordinator",
                "joining_date": date(2025, 2, 3),
                "salary": Decimal("47000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP007",
                "first_name": "Aditya",
                "last_name": "Malhotra",
                "email": "aditya.malhotra@smarterp.demo",
                "phone": "9876501007",
                "department": "Finance",
                "designation": "Finance Executive",
                "joining_date": date(2024, 5, 6),
                "salary": Decimal("55000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP008",
                "first_name": "Ananya",
                "last_name": "Gupta",
                "email": "ananya.gupta@smarterp.demo",
                "phone": "9876501008",
                "department": "Finance",
                "designation": "Accounts Analyst",
                "joining_date": date(2025, 4, 14),
                "salary": Decimal("50000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP009",
                "first_name": "Vikram",
                "last_name": "Joshi",
                "email": "vikram.joshi@smarterp.demo",
                "phone": "9876501009",
                "department": "Human Resources",
                "designation": "HR Executive",
                "joining_date": date(2024, 1, 8),
                "salary": Decimal("50000.00"),
                "status": "ACTIVE",
            },
            {
                "employee_id": "EMP010",
                "first_name": "Meera",
                "last_name": "Bose",
                "email": "meera.bose@smarterp.demo",
                "phone": "9876501010",
                "department": "Human Resources",
                "designation": "Recruitment Coordinator",
                "joining_date": date(2025, 6, 9),
                "salary": Decimal("45000.00"),
                "status": "ACTIVE",
            },
        ]

        created_count = 0

        for employee_data in employees:

            department = Department.objects.get(
                name=employee_data["department"]
            )

            _, created = Employee.objects.update_or_create(
                employee_id=employee_data["employee_id"],
                defaults={
                    "first_name": employee_data["first_name"],
                    "last_name": employee_data["last_name"],
                    "email": employee_data["email"],
                    "phone": employee_data["phone"],
                    "department": department,
                    "designation": employee_data["designation"],
                    "joining_date": employee_data["joining_date"],
                    "salary": employee_data["salary"],
                    "status": employee_data["status"],
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Employees ready: "
                f"{len(employees)} total, "
                f"{created_count} created."
            )
        )

    def seed_suppliers(self):

        suppliers = [
            {
                "name": "TechSource India Pvt Ltd",
                "contact_person": "Rahul Khanna",
                "email": "rahul@techsource.demo",
                "phone": "9811101001",
                "address": "Noida, Uttar Pradesh",
                "is_active": True,
            },
            {
                "name": "Digital Components Co",
                "contact_person": "Sneha Arora",
                "email": "sneha@digitalcomponents.demo",
                "phone": "9811101002",
                "address": "New Delhi",
                "is_active": True,
            },
            {
                "name": "OfficeHub Supplies",
                "contact_person": "Manish Batra",
                "email": "manish@officehub.demo",
                "phone": "9811101003",
                "address": "Gurugram, Haryana",
                "is_active": True,
            },
            {
                "name": "Prime Electronics Distribution",
                "contact_person": "Kavita Rao",
                "email": "kavita@primeelectronics.demo",
                "phone": "9811101004",
                "address": "Mumbai, Maharashtra",
                "is_active": True,
            },
            {
                "name": "Nexa Business Solutions",
                "contact_person": "Amit Sethi",
                "email": "amit@nexa.demo",
                "phone": "9811101005",
                "address": "Bengaluru, Karnataka",
                "is_active": True,
            },
        ]

        created_count = 0

        for supplier_data in suppliers:

            _, created = Supplier.objects.update_or_create(
                name=supplier_data["name"],
                defaults={
                    "contact_person": supplier_data["contact_person"],
                    "email": supplier_data["email"],
                    "phone": supplier_data["phone"],
                    "address": supplier_data["address"],
                    "is_active": supplier_data["is_active"],
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Suppliers ready: "
                f"{len(suppliers)} total, "
                f"{created_count} created."
            )
        )

    def seed_customers(self):

        customers = [
            {
                "name": "Vertex Retail Solutions",
                "email": "purchases@vertexretail.demo",
                "phone": "9822201001",
                "address": "New Delhi",
                "is_active": True,
            },
            {
                "name": "BluePeak Technologies",
                "email": "procurement@bluepeak.demo",
                "phone": "9822201002",
                "address": "Noida, Uttar Pradesh",
                "is_active": True,
            },
            {
                "name": "Nova Enterprises",
                "email": "orders@novaenterprises.demo",
                "phone": "9822201003",
                "address": "Gurugram, Haryana",
                "is_active": True,
            },
            {
                "name": "Apex Digital Services",
                "email": "accounts@apexdigital.demo",
                "phone": "9822201004",
                "address": "Jaipur, Rajasthan",
                "is_active": True,
            },
            {
                "name": "Orion Business Systems",
                "email": "purchase@orionbusiness.demo",
                "phone": "9822201005",
                "address": "Chandigarh",
                "is_active": True,
            },
            {
                "name": "Summit InfoTech",
                "email": "orders@summitinfotech.demo",
                "phone": "9822201006",
                "address": "Lucknow, Uttar Pradesh",
                "is_active": True,
            },
        ]

        created_count = 0

        for customer_data in customers:

            _, created = Customer.objects.update_or_create(
                name=customer_data["name"],
                defaults={
                    "email": customer_data["email"],
                    "phone": customer_data["phone"],
                    "address": customer_data["address"],
                    "is_active": customer_data["is_active"],
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Customers ready: "
                f"{len(customers)} total, "
                f"{created_count} created."
            )
        )

    def seed_products(self):

        products = [
            {
                "product_code": "PRD001",
                "name": "Business Laptop 14",
                "category": "Electronics",
                "description": "14-inch business laptop for office and field teams.",
                "quantity": 45,
                "purchase_price": Decimal("42000.00"),
                "selling_price": Decimal("52000.00"),
                "reorder_level": 12,
                "safety_stock": 8,
                "unit": "PCS",
            },
            {
                "product_code": "PRD002",
                "name": "Wireless Mouse",
                "category": "Accessories",
                "description": "Ergonomic wireless mouse for office use.",
                "quantity": 120,
                "purchase_price": Decimal("650.00"),
                "selling_price": Decimal("950.00"),
                "reorder_level": 30,
                "safety_stock": 20,
                "unit": "PCS",
            },
            {
                "product_code": "PRD003",
                "name": "Mechanical Keyboard",
                "category": "Accessories",
                "description": "Mechanical keyboard for professional desktop setups.",
                "quantity": 75,
                "purchase_price": Decimal("1800.00"),
                "selling_price": Decimal("2600.00"),
                "reorder_level": 20,
                "safety_stock": 12,
                "unit": "PCS",
            },
            {
                "product_code": "PRD004",
                "name": "24 Inch Monitor",
                "category": "Electronics",
                "description": "Full HD 24-inch monitor for business workstations.",
                "quantity": 38,
                "purchase_price": Decimal("8200.00"),
                "selling_price": Decimal("10500.00"),
                "reorder_level": 10,
                "safety_stock": 6,
                "unit": "PCS",
            },
            {
                "product_code": "PRD005",
                "name": "USB-C Docking Station",
                "category": "Accessories",
                "description": "Multi-port USB-C docking station for laptops.",
                "quantity": 28,
                "purchase_price": Decimal("3200.00"),
                "selling_price": Decimal("4500.00"),
                "reorder_level": 10,
                "safety_stock": 6,
                "unit": "PCS",
            },
            {
                "product_code": "PRD006",
                "name": "Office Printer",
                "category": "Office Equipment",
                "description": "Network-enabled multifunction office printer.",
                "quantity": 14,
                "purchase_price": Decimal("14500.00"),
                "selling_price": Decimal("18500.00"),
                "reorder_level": 5,
                "safety_stock": 3,
                "unit": "PCS",
            },
            {
                "product_code": "PRD007",
                "name": "HD Webcam",
                "category": "Accessories",
                "description": "1080p webcam for meetings and remote work.",
                "quantity": 55,
                "purchase_price": Decimal("1600.00"),
                "selling_price": Decimal("2400.00"),
                "reorder_level": 15,
                "safety_stock": 10,
                "unit": "PCS",
            },
            {
                "product_code": "PRD008",
                "name": "Noise Cancelling Headset",
                "category": "Accessories",
                "description": "Business headset with microphone and noise cancellation.",
                "quantity": 62,
                "purchase_price": Decimal("2200.00"),
                "selling_price": Decimal("3300.00"),
                "reorder_level": 18,
                "safety_stock": 12,
                "unit": "PCS",
            },
            {
                "product_code": "PRD009",
                "name": "External SSD 1TB",
                "category": "Storage",
                "description": "Portable 1TB solid-state storage drive.",
                "quantity": 33,
                "purchase_price": Decimal("5200.00"),
                "selling_price": Decimal("6800.00"),
                "reorder_level": 10,
                "safety_stock": 6,
                "unit": "PCS",
            },
            {
                "product_code": "PRD010",
                "name": "Wi-Fi Router",
                "category": "Networking",
                "description": "Dual-band wireless router for small office networks.",
                "quantity": 26,
                "purchase_price": Decimal("2400.00"),
                "selling_price": Decimal("3600.00"),
                "reorder_level": 8,
                "safety_stock": 5,
                "unit": "PCS",
            },
        ]

        created_count = 0

        for product_data in products:

            _, created = Product.objects.update_or_create(
                product_code=product_data["product_code"],
                defaults={
                    "name": product_data["name"],
                    "category": product_data["category"],
                    "description": product_data["description"],
                    "quantity": product_data["quantity"],
                    "purchase_price": product_data["purchase_price"],
                    "selling_price": product_data["selling_price"],
                    "reorder_level": product_data["reorder_level"],
                    "safety_stock": product_data["safety_stock"],
                    "unit": product_data["unit"],
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Products ready: "
                f"{len(products)} total, "
                f"{created_count} created."
            )
        )

    def seed_purchase_orders(self):

        purchase_orders = [
            ("2025-09", "TechSource India Pvt Ltd", ["PRD001", "PRD002"]),
            ("2025-09", "Digital Components Co", ["PRD003", "PRD004"]),

            ("2025-10", "OfficeHub Supplies", ["PRD006", "PRD007"]),
            ("2025-10", "Prime Electronics Distribution", ["PRD008", "PRD009"]),

            ("2025-11", "Nexa Business Solutions", ["PRD005", "PRD010"]),
            ("2025-11", "TechSource India Pvt Ltd", ["PRD001", "PRD003"]),

            ("2025-12", "Digital Components Co", ["PRD002", "PRD007"]),
            ("2025-12", "Prime Electronics Distribution", ["PRD004", "PRD009"]),

            ("2026-01", "OfficeHub Supplies", ["PRD006", "PRD008"]),
            ("2026-01", "Nexa Business Solutions", ["PRD005", "PRD010"]),

            ("2026-02", "TechSource India Pvt Ltd", ["PRD001", "PRD004"]),
            ("2026-02", "Digital Components Co", ["PRD002", "PRD003"]),

            ("2026-03", "Prime Electronics Distribution", ["PRD007", "PRD009"]),
            ("2026-03", "OfficeHub Supplies", ["PRD006", "PRD008"]),

            ("2026-04", "Nexa Business Solutions", ["PRD005", "PRD010"]),
            ("2026-04", "TechSource India Pvt Ltd", ["PRD001", "PRD002"]),

            ("2026-05", "Digital Components Co", ["PRD003", "PRD007"]),
            ("2026-05", "Prime Electronics Distribution", ["PRD004", "PRD009"]),

            ("2026-06", "OfficeHub Supplies", ["PRD006", "PRD008"]),
            ("2026-06", "Nexa Business Solutions", ["PRD005", "PRD010"]),

            ("2026-07", "TechSource India Pvt Ltd", ["PRD001", "PRD004"]),
            ("2026-07", "Digital Components Co", ["PRD002", "PRD007"]),

            ("2026-08", "Prime Electronics Distribution", ["PRD003", "PRD009"]),
            ("2026-08", "OfficeHub Supplies", ["PRD006", "PRD008"]),
        ]

        created_count = 0

        for index, (
            month_string,
            supplier_name,
            product_codes,
        ) in enumerate(purchase_orders, start=1):

            year, month = map(
                int,
                month_string.split("-")
            )

            day = 5 if index % 2 else 18

            order_date = date(
                year,
                month,
                day,
            )

            expected_delivery_date = (
                order_date + timedelta(days=7)
            )

            received_date = (
                expected_delivery_date
                + timedelta(days=(index % 3))
            )

            supplier = Supplier.objects.get(
                name=supplier_name
            )

            order_number = (
                f"DEMO-PO-{year}"
                f"{month:02d}-"
                f"{1 if day == 5 else 2:02d}"
            )

            purchase_order, created = (
                PurchaseOrder.objects.update_or_create(
                    order_number=order_number,
                    defaults={
                        "supplier": supplier,
                        "expected_delivery_date": (
                            expected_delivery_date
                        ),
                        "received_date": received_date,
                        "status": "RECEIVED",
                        "notes": (
                            "Historical SmartERP demo "
                            "procurement record."
                        ),
                    },
                )
            )

            PurchaseOrder.objects.filter(
                pk=purchase_order.pk
            ).update(
                order_date=order_date
            )

            purchase_order.refresh_from_db()

            purchase_order.items.all().delete()

            total_amount = Decimal("0.00")

            for product_index, product_code in enumerate(
                product_codes,
                start=1,
            ):

                product = Product.objects.get(
                    product_code=product_code
                )

                quantity = (
                    8
                    + ((index * 3 + product_index * 4) % 18)
                )

                PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.purchase_price,
                )

                total_amount += (
                    product.purchase_price
                    * quantity
                )

            purchase_order.total_amount = total_amount
            purchase_order.save(
                update_fields=["total_amount"]
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Historical purchase orders ready: "
                f"{len(purchase_orders)} total, "
                f"{created_count} created."
            )
        )

    def seed_sales_orders(self):

        sales_orders = [
            ("2025-09", "Vertex Retail Solutions", ["PRD001", "PRD002"]),
            ("2025-09", "BluePeak Technologies", ["PRD003", "PRD007"]),

            ("2025-10", "Nova Enterprises", ["PRD004", "PRD008"]),
            ("2025-10", "Apex Digital Services", ["PRD005", "PRD009"]),

            ("2025-11", "Orion Business Systems", ["PRD002", "PRD010"]),
            ("2025-11", "Summit InfoTech", ["PRD001", "PRD006"]),

            ("2025-12", "Vertex Retail Solutions", ["PRD003", "PRD008"]),
            ("2025-12", "BluePeak Technologies", ["PRD004", "PRD007"]),

            ("2026-01", "Nova Enterprises", ["PRD005", "PRD010"]),
            ("2026-01", "Apex Digital Services", ["PRD001", "PRD002"]),

            ("2026-02", "Orion Business Systems", ["PRD003", "PRD009"]),
            ("2026-02", "Summit InfoTech", ["PRD006", "PRD008"]),

            ("2026-03", "Vertex Retail Solutions", ["PRD001", "PRD004"]),
            ("2026-03", "BluePeak Technologies", ["PRD002", "PRD007"]),

            ("2026-04", "Nova Enterprises", ["PRD003", "PRD008"]),
            ("2026-04", "Apex Digital Services", ["PRD005", "PRD009"]),

            ("2026-05", "Orion Business Systems", ["PRD001", "PRD010"]),
            ("2026-05", "Summit InfoTech", ["PRD004", "PRD006"]),

            ("2026-06", "Vertex Retail Solutions", ["PRD002", "PRD007"]),
            ("2026-06", "BluePeak Technologies", ["PRD003", "PRD008"]),

            ("2026-07", "Nova Enterprises", ["PRD001", "PRD009"]),
            ("2026-07", "Apex Digital Services", ["PRD004", "PRD010"]),

            ("2026-08", "Orion Business Systems", ["PRD002", "PRD006"]),
            ("2026-08", "Summit InfoTech", ["PRD003", "PRD007"]),
        ]

        created_count = 0

        for index, (
            month_string,
            customer_name,
            product_codes,
        ) in enumerate(sales_orders, start=1):

            year, month = map(
                int,
                month_string.split("-")
            )

            day = 8 if index % 2 else 21

            order_date = date(
                year,
                month,
                day,
            )

            completed_date = (
                order_date + timedelta(
                    days=2 + (index % 4)
                )
            )

            customer = Customer.objects.get(
                name=customer_name
            )

            order_number = (
                f"DEMO-SO-{year}"
                f"{month:02d}-"
                f"{1 if day == 8 else 2:02d}"
            )

            sales_order, created = (
                SalesOrder.objects.update_or_create(
                    order_number=order_number,
                    defaults={
                        "customer": customer,
                        "completed_date": completed_date,
                        "status": "COMPLETED",
                        "notes": (
                            "Historical SmartERP demo "
                            "sales record."
                        ),
                    },
                )
            )

            SalesOrder.objects.filter(
                pk=sales_order.pk
            ).update(
                order_date=order_date
            )

            sales_order.refresh_from_db()

            sales_order.items.all().delete()

            total_amount = Decimal("0.00")

            for product_index, product_code in enumerate(
                product_codes,
                start=1,
            ):

                product = Product.objects.get(
                    product_code=product_code
                )

                quantity = (
                    3
                    + ((index * 2 + product_index * 3) % 9)
                )

                SalesOrderItem.objects.create(
                    sales_order=sales_order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.selling_price,
                )

                total_amount += (
                    product.selling_price
                    * quantity
                )

            sales_order.total_amount = total_amount
            sales_order.save(
                update_fields=["total_amount"]
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Historical sales orders ready: "
                f"{len(sales_orders)} total, "
                f"{created_count} created."
            )
        )

    def seed_finance_records(self):

        expense_created_count = 0
        revenue_created_count = 0

        demo_purchase_orders = (
            PurchaseOrder.objects
            .filter(
                order_number__startswith="DEMO-PO-",
                status="RECEIVED",
            )
            .order_by("order_date")
        )

        for purchase_order in demo_purchase_orders:

            expense_date = (
                purchase_order.received_date
                or purchase_order.order_date
            )

            paid_at = self.historical_datetime(
                expense_date,
                hour=15,
            )

            reviewed_at = (
                paid_at - timedelta(days=1)
            )

            _, created = Expense.objects.update_or_create(
                purchase_order=purchase_order,
                defaults={
                    "title": (
                        f"Procurement - "
                        f"{purchase_order.order_number}"
                    ),
                    "category": "PROCUREMENT",
                    "amount": purchase_order.total_amount,
                    "expense_date": expense_date,
                    "description": (
                        "Historical procurement expense "
                        "generated for SmartERP demo data."
                    ),
                    "reference_number": (
                        f"DEMO-EXP-"
                        f"{purchase_order.order_number}"
                    ),
                    "status": "PAID",
                    "payment_method": "BANK_TRANSFER",
                    "reviewed_at": reviewed_at,
                    "paid_at": paid_at,
                },
            )

            if created:
                expense_created_count += 1

        demo_sales_orders = (
            SalesOrder.objects
            .filter(
                order_number__startswith="DEMO-SO-",
                status="COMPLETED",
            )
            .order_by("order_date")
        )

        for sales_order in demo_sales_orders:

            revenue_date = (
                sales_order.completed_date
                or sales_order.order_date
            )

            _, created = Revenue.objects.update_or_create(
                sales_order=sales_order,
                defaults={
                    "amount": sales_order.total_amount,
                    "revenue_date": revenue_date,
                    "reference_number": (
                        f"DEMO-REV-"
                        f"{sales_order.order_number}"
                    ),
                },
            )

            if created:
                revenue_created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Procurement expenses ready: "
                f"{demo_purchase_orders.count()} total, "
                f"{expense_created_count} created."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sales revenues ready: "
                f"{demo_sales_orders.count()} total, "
                f"{revenue_created_count} created."
            )
        )

    def seed_operating_expenses(self):

        months = [
            (2025, 9),
            (2025, 10),
            (2025, 11),
            (2025, 12),
            (2026, 1),
            (2026, 2),
            (2026, 3),
            (2026, 4),
            (2026, 5),
            (2026, 6),
            (2026, 7),
            (2026, 8),
        ]

        monthly_salary = sum(
            (
                employee.salary
                for employee in Employee.objects.filter(
                    status="ACTIVE"
                )
            ),
            Decimal("0.00"),
        )

        created_count = 0
        total_records = 0

        for index, (year, month) in enumerate(
            months,
            start=1,
        ):

            expenses = [
                {
                    "category": "SALARY",
                    "title": "Monthly Employee Payroll",
                    "amount": monthly_salary,
                    "day": 25,
                    "payment_method": "BANK_TRANSFER",
                },
                {
                    "category": "UTILITIES",
                    "title": "Office Utilities",
                    "amount": (
                        Decimal("28000.00")
                        + Decimal(index * 950)
                    ),
                    "day": 10,
                    "payment_method": "BANK_TRANSFER",
                },
                {
                    "category": "OFFICE",
                    "title": "Office Supplies",
                    "amount": (
                        Decimal("12000.00")
                        + Decimal(index * 600)
                    ),
                    "day": 12,
                    "payment_method": "CARD",
                },
                {
                    "category": "MAINTENANCE",
                    "title": "Equipment Maintenance",
                    "amount": (
                        Decimal("16000.00")
                        + Decimal(index * 725)
                    ),
                    "day": 16,
                    "payment_method": "BANK_TRANSFER",
                },
            ]

            # Add travel expenses every third month.
            if index % 3 == 0:

                expenses.append(
                    {
                        "category": "TRAVEL",
                        "title": "Business Travel",
                        "amount": (
                            Decimal("24000.00")
                            + Decimal(index * 1200)
                        ),
                        "day": 20,
                        "payment_method": "CARD",
                    }
                )

            for expense_data in expenses:

                expense_date = date(
                    year,
                    month,
                    expense_data["day"],
                )

                reviewed_at = self.historical_datetime(
                    expense_date,
                    hour=11,
                )

                paid_at = self.historical_datetime(
                    expense_date + timedelta(days=2),
                    hour=15,
                )

                reference_number = (
                    f"DEMO-OPEX-"
                    f"{year}"
                    f"{month:02d}-"
                    f"{expense_data['category']}"
                )

                _, created = Expense.objects.update_or_create(
                    reference_number=reference_number,
                    defaults={
                        "title": expense_data["title"],
                        "category": expense_data["category"],
                        "amount": expense_data["amount"],
                        "expense_date": expense_date,
                        "description": (
                            "Historical operating expense "
                            "generated for SmartERP demo data."
                        ),
                        "purchase_order": None,
                        "status": "PAID",
                        "payment_method": (
                            expense_data["payment_method"]
                        ),
                        "reviewed_at": reviewed_at,
                        "paid_at": paid_at,
                    },
                )

                total_records += 1

                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Operating expenses ready: "
                f"{total_records} total, "
                f"{created_count} created."
            )
        )

    def seed_expense_workflow_records(self):

        workflow_expenses = [
            {
                "reference_number": "DEMO-WF-001",
                "title": "Conference Registration",
                "category": "TRAVEL",
                "amount": Decimal("18000.00"),
                "expense_date": date(2026, 8, 22),
                "status": "PENDING",
                "payment_method": "",
            },
            {
                "reference_number": "DEMO-WF-002",
                "title": "Office Furniture Purchase",
                "category": "OFFICE",
                "amount": Decimal("42000.00"),
                "expense_date": date(2026, 8, 24),
                "status": "PENDING",
                "payment_method": "",
            },
            {
                "reference_number": "DEMO-WF-003",
                "title": "Network Maintenance",
                "category": "MAINTENANCE",
                "amount": Decimal("27500.00"),
                "expense_date": date(2026, 8, 26),
                "status": "PENDING",
                "payment_method": "",
            },
            {
                "reference_number": "DEMO-WF-004",
                "title": "Software Subscription Renewal",
                "category": "OFFICE",
                "amount": Decimal("36000.00"),
                "expense_date": date(2026, 8, 18),
                "status": "APPROVED",
                "payment_method": "",
            },
            {
                "reference_number": "DEMO-WF-005",
                "title": "Office Renovation Work",
                "category": "MAINTENANCE",
                "amount": Decimal("68000.00"),
                "expense_date": date(2026, 8, 15),
                "status": "APPROVED",
                "payment_method": "",
            },
            {
                "reference_number": "DEMO-WF-006",
                "title": "Non-Essential Equipment Request",
                "category": "OTHER",
                "amount": Decimal("51000.00"),
                "expense_date": date(2026, 8, 12),
                "status": "REJECTED",
                "payment_method": "",
            },
        ]

        created_count = 0

        for expense_data in workflow_expenses:

            reviewed_at = None

            if expense_data["status"] in [
                "APPROVED",
                "REJECTED",
            ]:
                reviewed_at = self.historical_datetime(
                    expense_data["expense_date"]
                    + timedelta(days=1),
                    hour=14,
                )

            _, created = Expense.objects.update_or_create(
                reference_number=(
                    expense_data["reference_number"]
                ),
                defaults={
                    "title": expense_data["title"],
                    "category": expense_data["category"],
                    "amount": expense_data["amount"],
                    "expense_date": (
                        expense_data["expense_date"]
                    ),
                    "description": (
                        "SmartERP demo expense used "
                        "to demonstrate finance workflow states."
                    ),
                    "purchase_order": None,
                    "status": expense_data["status"],
                    "payment_method": (
                        expense_data["payment_method"]
                    ),
                    "reviewed_at": reviewed_at,
                    "paid_at": None,
                },
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Expense workflow records ready: "
                f"{len(workflow_expenses)} total, "
                f"{created_count} created."
            )
        )

    def seed_stock_movements(self):

        purchase_created_count = 0
        sale_created_count = 0

        demo_purchase_orders = (
            PurchaseOrder.objects
            .filter(
                order_number__startswith="DEMO-PO-",
                status="RECEIVED",
            )
            .prefetch_related("items__product")
            .order_by("order_date")
        )

        for purchase_order in demo_purchase_orders:

            movement_date = (
                purchase_order.received_date
                or purchase_order.order_date
            )

            movement_datetime = self.historical_datetime(
                movement_date,
                hour=10,
            )

            for item in purchase_order.items.all():

                movement, created = (
                    StockMovement.objects.update_or_create(
                        product=item.product,
                        movement_type="PURCHASE",
                        reference=purchase_order.order_number,
                        defaults={
                            "quantity": item.quantity,
                            "note": (
                                "Historical demo purchase "
                                f"from {purchase_order.order_number}"
                            ),
                        },
                    )
                )

                StockMovement.objects.filter(
                    pk=movement.pk
                ).update(
                    created_at=movement_datetime
                )

                if created:
                    purchase_created_count += 1

        demo_sales_orders = (
            SalesOrder.objects
            .filter(
                order_number__startswith="DEMO-SO-",
                status="COMPLETED",
            )
            .prefetch_related("items__product")
            .order_by("order_date")
        )

        for sales_order in demo_sales_orders:

            movement_date = (
                sales_order.completed_date
                or sales_order.order_date
            )

            movement_datetime = self.historical_datetime(
                movement_date,
                hour=17,
            )

            for item in sales_order.items.all():

                movement, created = (
                    StockMovement.objects.update_or_create(
                        product=item.product,
                        movement_type="SALE",
                        reference=sales_order.order_number,
                        defaults={
                            "quantity": item.quantity,
                            "note": (
                                "Historical demo sale "
                                f"from {sales_order.order_number}"
                            ),
                        },
                    )
                )

                StockMovement.objects.filter(
                    pk=movement.pk
                ).update(
                    created_at=movement_datetime
                )

                if created:
                    sale_created_count += 1

        purchase_total = sum(
            purchase_order.items.count()
            for purchase_order in demo_purchase_orders
        )

        sale_total = sum(
            sales_order.items.count()
            for sales_order in demo_sales_orders
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Purchase stock movements ready: "
                f"{purchase_total} total, "
                f"{purchase_created_count} created."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sale stock movements ready: "
                f"{sale_total} total, "
                f"{sale_created_count} created."
            )
        )

    def handle(self, *args, **options):

        if not options["confirm"]:

            self.stdout.write(
                self.style.WARNING(
                    "No data was created."
                )
            )

            self.stdout.write(
                "Run the command with --confirm "
                "when you are ready:"
            )

            self.stdout.write(
                "python manage.py seed_demo_data --confirm"
            )

            return

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data generation confirmed."
            )
        )

        self.seed_departments()
        self.seed_employees()
        self.seed_suppliers()
        self.seed_customers()
        self.seed_products()
        self.seed_purchase_orders()
        self.seed_sales_orders()
        self.seed_finance_records()
        self.seed_operating_expenses()
        self.seed_expense_workflow_records()
        self.seed_stock_movements()