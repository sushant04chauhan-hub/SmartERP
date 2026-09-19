from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from finance.models import Expense

from finance.anomaly_detection import (
    detect_expense_anomalies,
    get_expenses_for_anomaly_detection,
)

class FinanceWorkflowTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="finance_test_user",
            password="test-password-123",
        )

        self.user.profile.role = "FINANCE"
        self.user.profile.save()

        self.client.force_login(self.user)

        self.expense = Expense.objects.create(
            title="Office Supplies",
            category="OFFICE",
            amount=1500,
            expense_date="2026-09-13",
            reference_number="INV-TEST-001",
            description="Test expense",
            created_by=self.user,
        )

    def test_expense_is_pending_when_created(self):

        self.assertEqual(
            self.expense.status,
            "PENDING",
        )

    def test_pending_expense_can_be_approved(self):

        response = self.client.post(
            reverse(
                "expense_approve",
                args=[self.expense.id],
            )
        )

        self.expense.refresh_from_db()

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            self.expense.status,
            "APPROVED",
        )

        self.assertEqual(
            self.expense.reviewed_by,
            self.user,
        )

        self.assertIsNotNone(
            self.expense.reviewed_at
        )

    def test_pending_expense_can_be_rejected(self):
    
        response = self.client.post(
            reverse(
                "expense_reject",
                args=[self.expense.id],
            )
        )
    
        self.expense.refresh_from_db()
    
        self.assertEqual(
            response.status_code,
            302,
        )
    
        self.assertEqual(
            self.expense.status,
            "REJECTED",
        )
    
        self.assertEqual(
            self.expense.reviewed_by,
            self.user,
        )
    
        self.assertIsNotNone(
            self.expense.reviewed_at
        )
    
    
    def test_approved_expense_can_be_marked_paid(self):
    
        self.expense.status = "APPROVED"
        self.expense.reviewed_by = self.user
        self.expense.save()
    
        response = self.client.post(
            reverse(
                "expense_mark_paid",
                args=[self.expense.id],
            ),
            {
                "payment_method": "UPI",
            },
        )
    
        self.expense.refresh_from_db()
    
        self.assertEqual(
            response.status_code,
            302,
        )
    
        self.assertEqual(
            self.expense.status,
            "PAID",
        )
    
        self.assertEqual(
            self.expense.payment_method,
            "UPI",
        )
    
        self.assertIsNotNone(
            self.expense.paid_at
        )

    def test_pending_expense_cannot_be_marked_paid(self):

        response = self.client.post(
            reverse(
                "expense_mark_paid",
                args=[self.expense.id],
            ),
            {
                "payment_method": "UPI",
            },
        )

        self.expense.refresh_from_db()

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            self.expense.status,
            "PENDING",
        )

        self.assertEqual(
            self.expense.payment_method,
            "",
        )

        self.assertIsNone(
            self.expense.paid_at
        )


    def test_non_pending_expense_cannot_be_approved_again(self):

        self.expense.status = "PAID"
        self.expense.payment_method = "UPI"
        self.expense.save()

        response = self.client.post(
            reverse(
                "expense_approve",
                args=[self.expense.id],
            )
        )

        self.expense.refresh_from_db()

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            self.expense.status,
            "PAID",
        )
    def test_approved_expense_cannot_be_edited(self):

        self.expense.status = "APPROVED"
        self.expense.save()

        response = self.client.get(
            reverse(
                "expense_edit",
                args=[self.expense.id],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )


    def test_approved_expense_cannot_be_deleted(self):

        self.expense.status = "APPROVED"
        self.expense.save()

        response = self.client.post(
            reverse(
                "expense_delete",
                args=[self.expense.id],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.assertTrue(
            Expense.objects.filter(
                id=self.expense.id
            ).exists()
        )
    def test_expense_creation_rejects_non_positive_amount(self):
    
        response = self.client.post(
            reverse("expense_create"),
            {
                "title": "Invalid Expense",
                "category": "OFFICE",
                "amount": "-100",
                "expense_date": "2026-09-13",
                "reference_number": "INV-INVALID",
                "description": "Should not be saved",
            },
        )
    
        self.assertEqual(
            response.status_code,
            200,
        )
    
        self.assertFalse(
            Expense.objects.filter(
                title="Invalid Expense"
            ).exists()
        )
    
    
    def test_expense_list_can_filter_by_status(self):
    
        Expense.objects.create(
            title="Paid Travel Expense",
            category="TRAVEL",
            amount=2000,
            expense_date="2026-09-13",
            status="PAID",
            payment_method="UPI",
            created_by=self.user,
        )
    
        response = self.client.get(
            reverse("expense_list"),
            {
                "status": "PAID",
            },
        )
    
        self.assertEqual(
            response.status_code,
            200,
        )
    
        expenses = response.context["expenses"]
    
        self.assertTrue(
            all(
                expense.status == "PAID"
                for expense in expenses
            )
        )
    
    
    def test_expense_list_searches_reference_number(self):
    
        Expense.objects.create(
            title="Internet Bill",
            category="UTILITIES",
            amount=1800,
            expense_date="2026-09-13",
            reference_number="REF-SEARCH-123",
            created_by=self.user,
        )
    
        response = self.client.get(
            reverse("expense_list"),
            {
                "q": "REF-SEARCH-123",
            },
        )
    
        self.assertEqual(
            response.status_code,
            200,
        )
    
        expenses = list(
            response.context["expenses"]
        )
    
        self.assertEqual(
            len(expenses),
            1,
        )
    
        self.assertEqual(
            expenses[0].reference_number,
            "REF-SEARCH-123",
        )

class ExpenseAnomalyDetectionTests(TestCase):

    def create_expense(
        self,
        *,
        title,
        amount,
        category="OFFICE",
        status="PAID",
        reference_number="",
    ):

        return Expense.objects.create(
            title=title,
            category=category,
            amount=amount,
            expense_date="2026-08-15",
            reference_number=reference_number,
            status=status,
            payment_method=(
                "BANK_TRANSFER"
                if status == "PAID"
                else ""
            ),
        )

    def test_rejected_expenses_are_excluded(self):

        self.create_expense(
            title="Normal Expense",
            amount=1000,
        )

        rejected_expense = self.create_expense(
            title="Rejected Expense",
            amount=999999,
            status="REJECTED",
        )

        expenses = (
            get_expenses_for_anomaly_detection()
        )

        self.assertEqual(
            expenses.count(),
            1,
        )

        self.assertFalse(
            expenses.filter(
                id=rejected_expense.id
            ).exists()
        )

    def test_fewer_than_five_expenses_returns_empty_result(self):

        for index in range(4):

            self.create_expense(
                title=f"Small Dataset {index}",
                amount=1000 + index,
                reference_number=f"SMALL-{index}",
            )

        results = detect_expense_anomalies()

        self.assertEqual(
            results,
            [],
        )

    def test_anomaly_result_contains_expected_fields(self):

        for index in range(10):

            self.create_expense(
                title=f"Office Expense {index}",
                amount=1000 + (index * 10),
                reference_number=f"STRUCT-{index}",
            )

        results = detect_expense_anomalies()

        self.assertGreater(
            len(results),
            0,
        )

        expected_fields = {
            "expense_id",
            "title",
            "category",
            "category_label",
            "amount",
            "expense_date",
            "status",
            "is_anomaly",
            "anomaly_score",
        }

        self.assertEqual(
            set(results[0].keys()),
            expected_fields,
        )

    def test_is_anomaly_is_python_boolean(self):

        for index in range(10):

            self.create_expense(
                title=f"Boolean Expense {index}",
                amount=1500 + (index * 25),
                reference_number=f"BOOL-{index}",
            )

        results = detect_expense_anomalies()

        for result in results:

            self.assertIsInstance(
                result["is_anomaly"],
                bool,
            )

    def test_results_are_deterministic(self):

        for index in range(20):

            self.create_expense(
                title=f"Deterministic Expense {index}",
                amount=2000 + (index * 50),
                reference_number=f"DET-{index}",
            )

        first_results = detect_expense_anomalies()
        second_results = detect_expense_anomalies()

        self.assertEqual(
            first_results,
            second_results,
        )

    def test_extreme_expense_is_flagged_as_anomaly(self):

        for index in range(24):

            self.create_expense(
                title=f"Normal Office Expense {index}",
                amount=1000 + (index * 5),
                reference_number=f"NORMAL-{index}",
            )

        extreme_expense = self.create_expense(
            title="Extreme Office Expense",
            amount=1000000,
            reference_number="EXTREME-001",
        )

        results = detect_expense_anomalies()

        extreme_result = next(
            result
            for result in results
            if result["expense_id"]
            == extreme_expense.id
        )

        self.assertTrue(
            extreme_result["is_anomaly"]
        )