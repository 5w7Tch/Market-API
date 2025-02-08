import sqlite3
import unittest
from unittest.mock import MagicMock
from Core.ApiEndpoints.receipts import Receipt
from DB.DAOClasses.receipts_DAO import ReceiptsSqliteRepository


class TestReceiptsSqliteRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = MagicMock(sqlite3.Connection)
        self.repo = ReceiptsSqliteRepository()

    def test_create(self) -> None:
        self.connection.execute = MagicMock()
        self.repo.create(self.connection)

        self.connection.execute.assert_called_once()

    def test_update(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor
        cursor.rowcount = 1

        receipt = Receipt(status="closed")
        self.repo.update(receipt, "1", self.connection)

        cursor.execute.assert_called_with(
            "UPDATE receipts SET status = ? WHERE id = ?", (receipt.status, "1")
        )

        mock_cursor = self.connection.cursor.return_value
        mock_cursor.fetchone.return_value = None
        with self.assertRaises(ValueError):
            self.repo.update(receipt, "1", self.connection)

    def test_add(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor
        self.connection.cursor.execute = MagicMock()
        self.repo.add("1", self.connection)
        cursor.close.assert_called_once()

    def test_get_by_id(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor
        cursor.fetchone.return_value = {"id": "1", "status": "open"}

        result = self.repo.get_by_id("1", self.connection)
        self.assertIsInstance(result, Receipt)
        self.assertEqual(result.status, "open")

    def test_delete(self) -> None:
        cursor = MagicMock()
        self.connection.cursor.return_value = cursor
        cursor.rowcount = 1

        try:
            self.repo.delete("1", self.connection)
        except ValueError:
            self.fail("Unexpected ValueError")
        mock_cursor = self.connection.cursor.return_value
        mock_cursor.fetchone.return_value = None

        with self.assertRaises(ValueError) as context:
            self.repo.delete("4", self.connection)
        self.assertIn("does not exists", str(context.exception))
