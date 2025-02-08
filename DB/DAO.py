from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from DB.DAOClasses.receipt_products_DAO import ReceiptsProductsSqliteRepository
    from DB.DAOClasses.products_DAO import ProductsSqliteRepository
    from DB.DAOClasses.receipts_DAO import ReceiptsSqliteRepository
    from DB.DAOClasses.units_DAO import UnitsSqliteRepository


def get_receipt_products_repository() -> ReceiptsProductsSqliteRepository:
    from DB.DAOClasses.receipt_products_DAO import ReceiptsProductsSqliteRepository

    return ReceiptsProductsSqliteRepository()


def get_products_repository() -> ProductsSqliteRepository:
    from DB.DAOClasses.products_DAO import ProductsSqliteRepository

    return ProductsSqliteRepository()


def get_receipts_repository() -> ReceiptsSqliteRepository:
    from DB.DAOClasses.receipts_DAO import ReceiptsSqliteRepository

    return ReceiptsSqliteRepository()


def get_units_repository() -> UnitsSqliteRepository:
    from DB.DAOClasses.units_DAO import UnitsSqliteRepository

    return UnitsSqliteRepository()


def get_db() -> sqlite3.Connection:
    if os.environ.get("ENV") == "testing":
        return get_test_db_connection()
    db = get_db_connection()
    return db


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect("pos.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_test_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect("pos_test.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def clear() -> None:
    con = get_test_db_connection()
    con.cursor().execute(""" 
                            DROP TABLE IF EXISTS receipt_products;
                            """)
    con.cursor().execute(""" 
                                DROP TABLE IF EXISTS products;
                                """)
    con.cursor().execute(""" 
                                    DROP TABLE IF EXISTS receipts;
                                    """)
    con.cursor().execute(""" 
                                    DROP TABLE IF EXISTS units;
                                    """)
    con.commit()
    con.close()


@dataclass
class SqlLite:
    def units(self) -> UnitsSqliteRepository:
        return get_units_repository()

    def products(self) -> ProductsSqliteRepository:
        return get_products_repository()

    def receipts(self) -> ReceiptsSqliteRepository:
        return get_receipts_repository()

    def receipt_products(self) -> ReceiptsProductsSqliteRepository:
        return get_receipt_products_repository()
