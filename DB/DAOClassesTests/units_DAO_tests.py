import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from Core.ApiEndpoints.units import Unit, UnitGroup
from DB.DAOClasses.units_DAO import UnitsSqliteRepository


class TestUnitsSqliteRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = MagicMock(spec=sqlite3.Connection)
        self.repo = UnitsSqliteRepository()

    def test_create(self) -> None:
        self.repo.create(self.connection)
        self.connection.execute.assert_called_with("""CREATE TABLE IF NOT EXISTS units (
                            id TEXT PRIMARY KEY,
                            name TEXT UNIQUE NOT NULL
                        );""")
        self.connection.commit.assert_called()

    @patch("sqlite3.connect")
    def test_readAll(self, mock_connect: MagicMock) -> None:
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            {"id": "1", "name": "Unit A"},
            {"id": "2", "name": "Unit B"},
        ]

        result = self.repo.readAll(mock_conn)

        self.assertIsInstance(result, UnitGroup)
        self.assertEqual(len(result.units), 2)
        self.assertEqual(result.units[0].id, "1")
        self.assertEqual(result.units[0].name, "Unit A")

        mock_cursor.close.assert_called()

    @patch("sqlite3.connect")
    def test_get_by_id(self, mock_connect: MagicMock) -> None:
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = {"name": "Unit A"}

        unit = self.repo.get_by_id("1", mock_conn)
        self.assertIsInstance(unit, Unit)
        self.assertEqual(unit.name, "Unit A")

        mock_cursor.close.assert_called()

    def test_add(self) -> None:
        mock_cursor = self.connection.cursor.return_value
        mock_cursor.fetchone.side_effect = [(0,), None]

        unit = Unit(name="New Unit")
        self.repo.add(unit, "1", self.connection)

        mock_cursor.execute.assert_any_call(
            "SELECT COUNT(*) FROM units WHERE name = ?;", (unit.name,)
        )
        mock_cursor.execute.assert_any_call(
            "INSERT INTO units(id, name) VALUES (?, ?);", ("1", unit.name)
        )
        self.connection.commit.assert_called()

    def test_add_existing_unit(self) -> None:
        mock_cursor = self.connection.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)

        unit = Unit(name="Existing Unit")
        with self.assertRaises(ValueError):
            self.repo.add(unit, "2", self.connection)

    def test_get_by_id_not_found(self) -> None:
        mock_cursor = self.connection.cursor.return_value
        mock_cursor.fetchone.return_value = None

        with self.assertRaises(Exception) as context:
            self.repo.get_by_id("99", self.connection)
        self.assertEqual(str(context.exception), "No unit with id 99")

        mock_cursor.close.assert_called()
