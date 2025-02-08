import sqlite3
import unittest
from unittest.mock import MagicMock

from Core.ApiEndpoints.products import Product, ProductGroup, ProductResponse
from DB.DAOClasses.products_DAO import ProductsSqliteRepository


class TestProductsSqliteRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = ProductsSqliteRepository()
        self.connection = MagicMock(spec=sqlite3.Connection)
        self.cursor = MagicMock()
        self.connection.cursor.return_value = self.cursor

    def test_create(self) -> None:
        self.repo.create(self.connection)
        self.connection.execute.assert_called_once()
        self.connection.commit.assert_called_once()

    def test_readAll(self) -> None:
        self.cursor.fetchall.return_value = [
            {
                "id": "1",
                "unit_id": "10",
                "name": "ProductA",
                "barcode": "12345",
                "price": 100,
            },
            {
                "id": "2",
                "unit_id": "11",
                "name": "ProductB",
                "barcode": "67890",
                "price": 200,
            },
        ]

        result = self.repo.readAll(self.connection)
        self.assertIsInstance(result, ProductGroup)
        self.assertEqual(len(result.products), 2)
        self.cursor.close.assert_called_once()

    def test_get_by_id_existing(self) -> None:
        self.cursor.fetchone.return_value = {
            "id": "1",
            "unit_id": "10",
            "name": "ProductA",
            "barcode": "12345",
            "price": 100,
        }
        result = self.repo.get_by_id("1", self.connection)
        self.assertIsInstance(result, ProductResponse)
        self.assertEqual(result.id, "1")
        self.cursor.close.assert_called_once()

    def test_get_by_id_not_found(self) -> None:
        self.cursor.fetchone.return_value = None
        with self.assertRaises(Exception) as context:
            self.repo.get_by_id("99", self.connection)
        self.assertTrue("does not exists" in str(context.exception))

    def test_add_product(self) -> None:
        product = Product(unit_id="10", name="ProductA", barcode="12345", price=100)
        self.cursor.fetchone.return_value = None
        self.repo.add(product, "1", self.connection)
        self.cursor.execute.assert_called()
        self.connection.commit.assert_called_once()

    def test_add_product_duplicate_barcode(self) -> None:
        product = Product(unit_id="10", name="ProductA", barcode="12345", price=100)
        self.cursor.fetchone.return_value = [1]
        with self.assertRaises(ValueError):
            self.repo.add(product, "1", self.connection)

    def test_update_price_existing(self) -> None:
        self.cursor.rowcount = 1
        self.repo.update_price("1", 150, self.connection)
        self.cursor.execute.assert_called_once_with(
            "UPDATE products SET price = ? WHERE id = ?", (150, "1")
        )
        self.connection.commit.assert_called_once()

    def test_update_price_non_existing(self) -> None:
        self.cursor.rowcount = 0
        with self.assertRaises(ValueError):
            self.repo.update_price("99", 200, self.connection)
