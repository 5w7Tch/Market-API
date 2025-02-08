from __future__ import annotations
import sqlite3
from dataclasses import dataclass

import Core.ApiEndpoints.products as cp


@dataclass
class ProductsSqliteRepository:
    def create(self, connection: sqlite3.Connection) -> None:
        connection.execute("""CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            unit_id TEXT,
            name TEXT NOT NULL,
            barcode TEXT UNIQUE NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (unit_id) REFERENCES units(id)
        );""")
        connection.commit()
        # connection.close()

    def readAll(self, connection: sqlite3.Connection) -> cp.ProductGroup:
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM products;")
            rows = cursor.fetchall()
            products = [cp.ProductResponse(**row) for row in rows]
            return cp.ProductGroup(products=products)
        finally:
            cursor.close()
            # connection.close()

    def get_by_id(self, id: str, connection: sqlite3.Connection) -> cp.ProductResponse:
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Product with id {id} does not exists")
            print(row)
            return cp.ProductResponse(
                id=row["id"],
                unit_id=row["unit_id"],
                name=row["name"],
                barcode=row["barcode"],
                price=row["price"],
            )
        finally:
            cursor.close()
            # connection.close()

    def add(self, product: cp.Product, id: str, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT * FROM products WHERE barcode = ?;", (product.barcode,)
            )
            if cursor.fetchone() is not None:
                raise ValueError(
                    f"Product with barcode '{product.barcode}' already exists."
                )

            cursor.execute(
                """
                INSERT INTO products(id, unit_id, name, barcode, price)
                VALUES (?, ?, ?, ?, ?);
                """,
                (id, product.unit_id, product.name, product.barcode, product.price),
            )

            connection.commit()

        finally:
            cursor.close()
            # connection.close()

    def update_price(self, id: str, price: int, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()

        try:
            cursor.execute("UPDATE products SET price = ? WHERE id = ?", (price, id))
            if cursor.rowcount == 0:
                raise ValueError(f"Product with id<{id}> does not exist.")
        finally:
            connection.commit()
            cursor.close()
            # connection.close()
