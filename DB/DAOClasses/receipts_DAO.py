import sqlite3
from dataclasses import dataclass
from Core.ApiEndpoints.receipts import Receipt


@dataclass
class ReceiptsSqliteRepository:
    def create(self, connection: sqlite3.Connection) -> None:
        connection.execute("""CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL
        );""")
        connection.commit()
        # connection.close()

    def update(self, receipt: Receipt, id: str, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()
        print(id)
        cursor.execute("SELECT * FROM receipts WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"Receipt with id<{id}> does not exists")
        if row["status"] == "closed":
            raise ValueError(f"Receipt with id<{id}> is closed")
        cursor.execute(
            "UPDATE receipts SET status = ? WHERE id = ?", (receipt.status, id)
        )
        connection.commit()
        cursor.close()

    def add(self, gvn_id: str, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()
        cursor.execute(
            """
                INSERT INTO receipts(id, status)
                VALUES (?, ?);
            """,
            (gvn_id, "open"),
        )

        connection.commit()
        cursor.close()

    def get_by_id(self, gvn_id: str, connection: sqlite3.Connection) -> Receipt:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM receipts WHERE id = ?", (gvn_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Receipt with id<{gvn_id}> does not exists")
            return Receipt(status=row["status"])
        finally:
            cursor.close()

    def delete(self, gvn_id: str, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()

        try:
            cursor.execute("select * FROM receipts WHERE id = ?", (gvn_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Receipt with id<{gvn_id}> does not exists")
            if row["status"] == "closed":
                raise ValueError(f"Receipt with id<{gvn_id}> is closed")

            cursor.execute(
                "DELETE FROM receipt_products WHERE receipt_id = ?", (gvn_id,)
            )
            connection.cursor().execute("DELETE FROM receipts WHERE id = ?", (gvn_id,))

        finally:
            connection.commit()
            cursor.close()
