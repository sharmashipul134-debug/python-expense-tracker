import os
import tempfile
import unittest

# Configure a temporary database before importing the application.
_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["EXPENSE_TRACKER_DB"] = _db_path

from app import app, init_db  # noqa: E402


class ExpenseTrackerTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        init_db()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PennyWise", response.data)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_add_expense(self):
        response = self.client.post("/add", data={
            "title": "Test groceries",
            "amount": "250",
            "kind": "expense",
            "category": "Food",
            "transaction_date": "2026-10-11",
            "notes": "Unit test",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test groceries", response.data)
        self.assertIn(b"250.00", response.data)

    def test_reject_invalid_amount(self):
        response = self.client.post("/add", data={
            "title": "Bad transaction",
            "amount": "-5",
            "kind": "expense",
            "category": "Food",
            "transaction_date": "2026-10-11",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please check", response.data)


if __name__ == "__main__":
    unittest.main()
