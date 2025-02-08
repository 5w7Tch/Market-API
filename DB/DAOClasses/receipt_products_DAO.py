import sqlite3
from dataclasses import dataclass

from Core.ApiEndpoints.receipt_products import (
    ReceiptProducts,
    ReceiptResponse,
    ProductResponse,
)


@dataclass
class ReceiptsProductsSqliteRepository:
    def create(self, connection: sqlite3.Connection) -> None:
        connection.execute("""CREATE TABLE IF NOT EXISTS receipt_products (
            receipt_id TEXT,
            product_id TEXT,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL,
            total INTEGER NOT NULL,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );""")
        connection.commit()
        # connection.close()

    def getSummary(self, connection: sqlite3.Connection) -> tuple[int, int]:
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT rp.receipt_id ,count(rp.receipt_id) AS n_receipts, SUM(rp.total) AS total_sum
                FROM receipt_products rp
                where rp.receipt_id in (select id from receipts where status = 'closed')
                GROUP BY rp.receipt_id
                """
            )

            result = cursor.fetchall()
            price_sum = 0
            count = 0
            for r in result:
                price_sum += r["total_sum"]
                count += 1
            return count, price_sum

        finally:
            cursor.close()

    def update(self, rp: ReceiptProducts, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
                INSERT INTO receipt_products(receipt_id, product_id, quantity, price, total)
                VALUES (?, ?, ?, ?, ?);
            """,
            (rp.receipt_id, rp.product_id, rp.quantity, rp.price, rp.total),
        )
        connection.commit()

    def get_receipt_summery(
        self, given_receipt_id: str, connection: sqlite3.Connection
    ) -> ReceiptResponse:
        cursor = connection.cursor()
        res = ReceiptResponse(id=given_receipt_id, status="open", products=[], total=0)
        try:
            cursor.execute(
                """select status from receipts where id = ?""", (given_receipt_id,)
            )
            result = cursor.fetchone()
            if result is not None:
                res.status = result[0]
            else:
                raise ValueError(f"Receipt with id {given_receipt_id} does not exists")
            cursor.execute(
                """select * from receipt_products where receipt_id = ?""",
                (given_receipt_id,),
            )
            result = cursor.fetchall()
            for r in result:
                res.total += r["total"]
                res.products.append(
                    ProductResponse(
                        id=r["product_id"],
                        quantity=r["quantity"],
                        price=r["price"],
                        total=r["total"],
                    )
                )
            return res
        finally:
            cursor.close()
            # connection.close()

    def delete_receipt(
        self, given_receipt_id: str, connection: sqlite3.Connection
    ) -> None:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM receipt_products WHERE receipt_id = ?", (given_receipt_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Receipt with id {given_receipt_id} does not exists")
        finally:
            connection.commit()
            cursor.close()
