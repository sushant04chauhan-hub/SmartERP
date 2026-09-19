from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Product, StockMovement
from .services import apply_stock_movement
from .reorder_recommendations import (
    get_all_reorder_recommendations,
    get_reorder_recommendation,
)
from unittest.mock import patch


class InventoryServiceTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="inventory_test_user",
            password="test-password-123",
        )

        self.product = Product.objects.create(
            product_code="TEST-P001",
            name="Test Product",
            category="Testing",
            description="Product used for automated tests",
            quantity=10,
            purchase_price=100,
            selling_price=150,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

    def test_adjustment_in_increases_stock(self):

        product, movement = apply_stock_movement(
            product=self.product,
            movement_type="ADJUSTMENT_IN",
            quantity=5,
            user=self.user,
            reference="TEST-IN",
            note="Automated test",
        )

        product.refresh_from_db()

        self.assertEqual(
            product.quantity,
            15,
        )

        self.assertEqual(
            movement.movement_type,
            "ADJUSTMENT_IN",
        )

        self.assertEqual(
            movement.quantity,
            5,
        )

        self.assertEqual(
            movement.reference,
            "TEST-IN",
        )

        self.assertEqual(
            movement.created_by,
            self.user,
        )

    def test_adjustment_out_decreases_stock(self):

        product, movement = apply_stock_movement(
            product=self.product,
            movement_type="ADJUSTMENT_OUT",
            quantity=4,
            user=self.user,
            reference="TEST-OUT",
            note="Automated test",
        )

        product.refresh_from_db()

        self.assertEqual(
            product.quantity,
            6,
        )

        self.assertEqual(
            movement.movement_type,
            "ADJUSTMENT_OUT",
        )

    def test_insufficient_stock_is_rejected(self):

        with self.assertRaises(ValidationError):

            apply_stock_movement(
                product=self.product,
                movement_type="ADJUSTMENT_OUT",
                quantity=100,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            StockMovement.objects.count(),
            0,
        )

    def test_zero_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            apply_stock_movement(
                product=self.product,
                movement_type="ADJUSTMENT_IN",
                quantity=0,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.quantity,
            10,
        )

        self.assertEqual(
            StockMovement.objects.count(),
            0,
        )

class ReorderRecommendationTests(TestCase):

    def setUp(self):

        self.product = Product.objects.create(
            product_code="REORDER-P001",
            name="Reorder Test Product",
            category="Testing",
            quantity=10,
            purchase_price=100,
            selling_price=150,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

    def forecast_result(
        self,
        predicted_demand,
        method="Linear Regression",
    ):

        return {
            "product_code": self.product.product_code,
            "product_name": self.product.name,
            "forecast_month": "2026-09-01",
            "predicted_demand": predicted_demand,
            "method": method,
            "historical_months": 12,
        }

    @patch(
        "inventory.reorder_recommendations."
        "forecast_product_demand"
    )
    def test_no_action_when_projected_stock_is_above_reorder_level(
        self,
        mock_forecast,
    ):

        mock_forecast.return_value = (
            self.forecast_result(2)
        )

        recommendation = (
            get_reorder_recommendation(
                self.product
            )
        )

        self.assertEqual(
            recommendation["projected_stock"],
            8,
        )

        self.assertEqual(
            recommendation["action"],
            "NO_ACTION",
        )

        self.assertEqual(
            recommendation["urgency"],
            "NONE",
        )

        self.assertEqual(
            recommendation["recommended_quantity"],
            0,
        )

    @patch(
        "inventory.reorder_recommendations."
        "forecast_product_demand"
    )
    def test_medium_reorder_recommendation(
        self,
        mock_forecast,
    ):

        self.product.quantity = 8
        self.product.save()

        mock_forecast.return_value = (
            self.forecast_result(4)
        )

        recommendation = (
            get_reorder_recommendation(
                self.product
            )
        )

        self.assertEqual(
            recommendation["projected_stock"],
            4,
        )

        self.assertEqual(
            recommendation["action"],
            "REORDER",
        )

        self.assertEqual(
            recommendation["urgency"],
            "MEDIUM",
        )

        self.assertEqual(
            recommendation["recommended_quantity"],
            3,
        )

    @patch(
        "inventory.reorder_recommendations."
        "forecast_product_demand"
    )
    def test_high_reorder_recommendation(
        self,
        mock_forecast,
    ):

        self.product.quantity = 6
        self.product.save()

        mock_forecast.return_value = (
            self.forecast_result(4)
        )

        recommendation = (
            get_reorder_recommendation(
                self.product
            )
        )

        self.assertEqual(
            recommendation["projected_stock"],
            2,
        )

        self.assertEqual(
            recommendation["urgency"],
            "HIGH",
        )

        self.assertEqual(
            recommendation["recommended_quantity"],
            5,
        )

    @patch(
        "inventory.reorder_recommendations."
        "forecast_product_demand"
    )
    def test_critical_reorder_recommendation(
        self,
        mock_forecast,
    ):

        self.product.quantity = 3
        self.product.save()

        mock_forecast.return_value = (
            self.forecast_result(4)
        )

        recommendation = (
            get_reorder_recommendation(
                self.product
            )
        )

        self.assertEqual(
            recommendation["projected_stock"],
            -1,
        )

        self.assertEqual(
            recommendation["urgency"],
            "CRITICAL",
        )

        self.assertEqual(
            recommendation["recommended_quantity"],
            8,
        )

    @patch(
        "inventory.reorder_recommendations."
        "forecast_product_demand"
    )
    def test_forecast_information_is_included(
        self,
        mock_forecast,
    ):

        mock_forecast.return_value = (
            self.forecast_result(
                2,
                method="Historical average fallback",
            )
        )

        recommendation = (
            get_reorder_recommendation(
                self.product
            )
        )

        self.assertEqual(
            recommendation["predicted_demand"],
            2,
        )

        self.assertEqual(
            recommendation["forecast_month"],
            "2026-09-01",
        )

        self.assertEqual(
            recommendation["forecast_method"],
            "Historical average fallback",
        )

    @patch(
        "inventory.reorder_recommendations."
        "forecast_product_demand"
    )
    def test_recommendations_are_sorted_by_urgency(
        self,
        mock_forecast,
    ):

        critical_product = Product.objects.create(
            product_code="REORDER-CRITICAL",
            name="Critical Product",
            category="Testing",
            quantity=2,
            purchase_price=100,
            selling_price=150,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        high_product = Product.objects.create(
            product_code="REORDER-HIGH",
            name="High Product",
            category="Testing",
            quantity=5,
            purchase_price=100,
            selling_price=150,
            reorder_level=5,
            safety_stock=2,
            unit="PCS",
        )

        def forecast_for_product(product):

            demand_by_code = {
                "REORDER-P001": 0,
                "REORDER-CRITICAL": 5,
                "REORDER-HIGH": 4,
            }

            return {
                "product_code": product.product_code,
                "product_name": product.name,
                "forecast_month": "2026-09-01",
                "predicted_demand": (
                    demand_by_code[
                        product.product_code
                    ]
                ),
                "method": "Linear Regression",
                "historical_months": 12,
            }

        mock_forecast.side_effect = (
            forecast_for_product
        )

        recommendations = (
            get_all_reorder_recommendations()
        )

        self.assertEqual(
            recommendations[0]["product_code"],
            critical_product.product_code,
        )

        self.assertEqual(
            recommendations[0]["urgency"],
            "CRITICAL",
        )

        self.assertEqual(
            recommendations[1]["product_code"],
            high_product.product_code,
        )

        self.assertEqual(
            recommendations[1]["urgency"],
            "HIGH",
        )

        self.assertEqual(
            recommendations[-1]["urgency"],
            "NONE",
        )