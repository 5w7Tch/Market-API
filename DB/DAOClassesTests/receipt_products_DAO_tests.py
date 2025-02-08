import unittest
from unittest.mock import MagicMock
import sqlite3

from Core.ApiEndpoints.receipt_products import ReceiptProducts, ReceiptResponse
from DB.DAOClasses.receipt_products_DAO import ReceiptsProductsSqliteRepository


class TestReceiptsProductsSqliteRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = MagicMock(sqlite3.Connection)
        self.repo = ReceiptsProductsSqliteRepository()

    def test_create(self) -> None:
        self.repo.create(self.connection)

        self.connection.execute.assert_called_once()
        self.connection.commit.assert_called_once()

    def test_getSummary(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor

        cursor.fetchall.return_value = [
            {"total_sum": 500},
            {"total_sum": 150},
        ]

        count, price_sum = self.repo.getSummary(self.connection)

        self.assertEqual(count, 2)
        self.assertEqual(price_sum, 650)

        cursor.execute.assert_called_once()

    def test_update(self) -> None:
        rp = ReceiptProducts(
            receipt_id="1", product_id="101", quantity=2, price=100, total=200
        )

        self.repo.update(rp, self.connection)

        self.connection.execute.assert_called_once()

        self.connection.commit.assert_called_once()

    def test_get_receipt_summery(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor

        cursor.fetchone.return_value = ("closed",)

        cursor.fetchall.return_value = [
            {"product_id": "101", "quantity": 2, "price": 100, "total": 200},
            {"product_id": "102", "quantity": 1, "price": 50, "total": 50},
        ]

        result = self.repo.get_receipt_summery("1", self.connection)

        self.assertIsInstance(result, ReceiptResponse)
        self.assertEqual(result.status, "closed")
        self.assertEqual(result.total, 250)
        self.assertEqual(len(result.products), 2)

        cursor.fetchall.assert_called_once()
        cursor.fetchone.return_value = None

        with self.assertRaises(ValueError) as context:
            self.repo.get_receipt_summery("1", self.connection)
        self.assertTrue("does not exists" in str(context.exception))

    def test_delete_receipt(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor

        cursor.fetchone.return_value = None

        with self.assertRaises(ValueError) as context:
            self.repo.delete_receipt("1", self.connection)
        self.assertTrue("does not exists" in str(context.exception))

        self.connection.commit.assert_called_once()

    def test_delete_receipt_success(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor

        cursor.fetchone.return_value = (1,)

        self.repo.delete_receipt("1", self.connection)

        cursor.execute.assert_called_once()
        self.connection.commit.assert_called_once()
