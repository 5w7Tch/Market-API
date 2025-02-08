import sqlite3
from dataclasses import dataclass

from Core.ApiEndpoints.units import Unit, UnitGroup, UnitResponse


@dataclass
class UnitsSqliteRepository:
    def create(self, connection: sqlite3.Connection) -> None:
        connection.execute("""CREATE TABLE IF NOT EXISTS units (
                            id TEXT PRIMARY KEY,
                            name TEXT UNIQUE NOT NULL
                        );""")
        connection.commit()
        # connection.close()

    def readAll(self, connection: sqlite3.Connection) -> UnitGroup:
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM units;")
            all_rows = cursor.fetchall()
            result = UnitGroup(units=[])

            for row in all_rows:
                result.units.append(UnitResponse(id=row["id"], name=row["name"]))
            return result
        finally:
            cursor.close()
            # connection.close()

    def get_by_id(self, id: str, connection: sqlite3.Connection) -> Unit:
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM units WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"No unit with id {id}")
            return Unit(name=row["name"])
        finally:
            cursor.close()
            # connection.close()

    def add(self, unit: Unit, id: str, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM units WHERE name = ?;", (unit.name,))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"Unit with name '{unit.name}' already exists.")

            cursor.execute(
                "INSERT INTO units(id, name) VALUES (?, ?);", (id, unit.name)
            )
            connection.commit()

        finally:
            cursor.close()
            # connection.close()
