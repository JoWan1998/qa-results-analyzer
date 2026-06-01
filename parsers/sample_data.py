# parsers/sample_data.py

import pandas as pd
import numpy as np


def generate_sample_jmeter(n: int = 200) -> pd.DataFrame:
    np.random.seed(42)

    endpoints = {
        "POST /auth/login": {
            "avg_ms": 320, "std": 80,
            "responses": ["200", "200", "200", "401", "500"],
            "bytes_range": (800, 2000),
        },
        "GET /dashboard": {
            "avg_ms": 850, "std": 200,
            "responses": ["200", "200", "200", "200", "503"],
            "bytes_range": (15000, 80000),
        },
        "GET /api/users": {
            "avg_ms": 210, "std": 60,
            "responses": ["200", "200", "200", "404", "500"],
            "bytes_range": (2000, 10000),
        },
        "POST /api/orders": {
            "avg_ms": 540, "std": 150,
            "responses": ["201", "201", "201", "400", "500"],
            "bytes_range": (500, 1500),
        },
        "GET /products/search": {
            "avg_ms": 430, "std": 120,
            "responses": ["200", "200", "200", "200", "504"],
            "bytes_range": (5000, 30000),
        },
        "PUT /api/profile": {
            "avg_ms": 280, "std": 70,
            "responses": ["200", "200", "200", "422", "500"],
            "bytes_range": (300, 900),
        },
        "DELETE /api/cart/{id}": {
            "avg_ms": 190, "std": 50,
            "responses": ["204", "204", "204", "404", "500"],
            "bytes_range": (100, 400),
        },
    }

    records = []
    labels = list(endpoints.keys())
    assigned = np.random.choice(labels, n)
    timestamps = pd.date_range("2024-06-01 09:00", periods=n, freq="3s")

    for i, label in enumerate(assigned):
        cfg = endpoints[label]
        elapsed = max(50, int(np.random.normal(cfg["avg_ms"], cfg["std"])))
        response = np.random.choice(cfg["responses"])
        success = response in ("200", "201", "204")
        records.append({
            "label":      label,
            "success":    success,
            "elapsed_ms": elapsed,
            "bytes":      int(np.random.randint(*cfg["bytes_range"])),
            "response":   response,
            "timestamp":  int(timestamps[i].timestamp() * 1000),
            "thread":     f"ThreadGroup-{np.random.randint(1, 6)}-{np.random.randint(1, 11)}",
        })

    return pd.DataFrame(records)


def generate_sample_playwright(n: int = 80) -> pd.DataFrame:
    np.random.seed(77)

    suites = {
        "auth.spec.ts": [
            "should login with valid credentials",
            "should show error on invalid password",
            "should redirect to dashboard after login",
            "should logout successfully",
            "should block login after 5 failed attempts",
        ],
        "checkout.spec.ts": [
            "should add product to cart",
            "should remove product from cart",
            "should complete checkout with valid card",
            "should reject expired credit card",
            "should apply discount coupon",
        ],
        "search.spec.ts": [
            "should return results for valid keyword",
            "should show empty state for unknown keyword",
            "should filter results by category",
            "should sort results by price ascending",
        ],
        "profile.spec.ts": [
            "should update username successfully",
            "should reject duplicate email",
            "should upload profile picture",
            "should delete account with confirmation",
        ],
    }

    error_messages = [
        "Timeout 30000ms exceeded waiting for selector '#submit-btn'",
        "expect(received).toBe(expected) — Expected: '/dashboard', Received: '/login'",
        "Element is not visible: button[data-testid='confirm']",
        "Navigation timeout exceeded: 30000ms",
        "expect(page).toHaveURL — Expected URL pattern not matched",
    ]

    all_cases = [
        (spec, title)
        for spec, titles in suites.items()
        for title in titles
    ]
    repeated = (all_cases * (n // len(all_cases) + 1))[:n]

    statuses = np.random.choice(
        ["passed", "failed", "skipped"],
        n,
        p=[0.85, 0.12, 0.03]
    )

    records = []
    for (spec, title), status in zip(repeated, statuses):
        records.append({
            "label":      f"{spec} > {title}",
            "success":    status == "passed",
            "elapsed_ms": int(np.random.randint(200, 8000)),
            "status":     status,
            "file":       spec,
            "error":      np.random.choice(error_messages) if status == "failed" else "",
        })

    return pd.DataFrame(records)


def generate_sample_selenium(n: int = 60) -> pd.DataFrame:
    np.random.seed(99)

    suites = {
        "tests.auth.test_login": [
            "test_login_valid_credentials",
            "test_login_invalid_password",
            "test_login_empty_fields",
            "test_login_forgot_password_link",
        ],
        "tests.checkout.test_cart": [
            "test_add_item_to_cart",
            "test_remove_item_from_cart",
            "test_checkout_with_valid_card",
            "test_checkout_with_expired_card",
        ],
        "tests.search.test_filters": [
            "test_search_by_keyword",
            "test_filter_by_category",
            "test_filter_by_price_range",
            "test_search_no_results",
        ],
        "tests.profile.test_update": [
            "test_update_username",
            "test_update_email_valid",
            "test_update_email_duplicate",
            "test_upload_profile_picture",
        ],
    }

    error_messages = [
        "AssertionError: Expected URL '/dashboard' but got '/login'",
        "TimeoutException: Element #submit-btn not found after 10s",
        "NoSuchElementException: Unable to locate element: input[name='email']",
        "AssertionError: Expected text 'Welcome' not present in page",
        "WebDriverException: Session timed out",
    ]

    all_cases = [
        (classname, method)
        for classname, methods in suites.items()
        for method in methods
    ]
    repeated = (all_cases * (n // len(all_cases) + 1))[:n]

    statuses = np.random.choice(
        ["passed", "failed", "skipped"],
        n,
        p=[0.82, 0.13, 0.05]
    )

    records = []
    for (classname, method), status in zip(repeated, statuses):
        records.append({
            "label":      f"{classname} > {method}",
            "success":    status == "passed",
            "elapsed_ms": int(np.random.randint(300, 12000)),
            "status":     status,
            "file":       classname,
            "error":      np.random.choice(error_messages) if status == "failed" else "",
        })

    return pd.DataFrame(records)