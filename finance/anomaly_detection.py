import math
from collections import defaultdict
from statistics import median

import numpy as np
from sklearn.ensemble import IsolationForest

from finance.models import Expense


def get_expenses_for_anomaly_detection():

    return (
        Expense.objects
        .exclude(status="REJECTED")
        .order_by(
            "expense_date",
            "id",
        )
    )


def build_expense_features(expenses):

    expenses = list(expenses)

    if not expenses:
        return [], np.empty((0, 2))

    amounts_by_category = defaultdict(list)

    for expense in expenses:
        amounts_by_category[
            expense.category
        ].append(
            float(expense.amount)
        )

    category_medians = {
        category: median(amounts)
        for category, amounts
        in amounts_by_category.items()
    }

    features = []

    for expense in expenses:

        amount = float(expense.amount)

        category_median = category_medians[
            expense.category
        ]

        if category_median > 0:
            category_ratio = (
                amount / category_median
            )
        else:
            category_ratio = 1.0

        features.append(
            [
                math.log1p(amount),
                category_ratio,
            ]
        )

    return expenses, np.array(
        features,
        dtype=float,
    )


def detect_expense_anomalies():

    queryset = get_expenses_for_anomaly_detection()

    expenses, features = build_expense_features(
        queryset
    )

    if len(expenses) < 5:
        return []

    model = IsolationForest(
        contamination=0.08,
        random_state=42,
    )

    predictions = model.fit_predict(
        features
    )

    scores = model.decision_function(
        features
    )

    results = []

    for expense, prediction, score in zip(
        expenses,
        predictions,
        scores,
    ):

        results.append(
            {
                "expense_id": expense.id,
                "title": expense.title,
                "category": expense.category,
                "category_label": (
                    expense.get_category_display()
                ),
                "amount": float(expense.amount),
                "expense_date": expense.expense_date,
                "status": expense.status,
                "is_anomaly": bool(prediction == -1),
                "anomaly_score": round(
                    float(score),
                    4,
                ),
            }
        )

    return sorted(
        results,
        key=lambda item: (
            not item["is_anomaly"],
            item["anomaly_score"],
        ),
    )