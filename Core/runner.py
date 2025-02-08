import os

from dotenv import load_dotenv
from fastapi import FastAPI

from Core.ApiEndpoints.products import products_api
from Core.ApiEndpoints.receipt_products import sales_api
from Core.ApiEndpoints.receipts import receipts_api
from Core.ApiEndpoints.units import units_api
from DB.DAO import SqlLite, get_db_connection, get_test_db_connection


def set_up_rotes(api: FastAPI) -> None:
    api.include_router(products_api, prefix="/products", tags=["Products"])
    api.include_router(sales_api, prefix="/sales", tags=["Sales"])
    api.include_router(receipts_api, prefix="/receipts", tags=["Receipts"])
    api.include_router(units_api, prefix="/units", tags=["Units"])


def setup() -> FastAPI:
    load_dotenv()
    api = FastAPI()

    api.state.infra = SqlLite()
    os.environ.setdefault("ENV", "app")

    SqlLite().receipt_products().create(get_db_connection())
    SqlLite().receipts().create(get_db_connection())
    SqlLite().products().create(get_db_connection())
    SqlLite().units().create(get_db_connection())

    set_up_rotes(api)

    return api


def test_setup() -> FastAPI:
    load_dotenv()
    api = FastAPI()

    api.state.infra = SqlLite()
    os.environ.setdefault("ENV", "testing")

    SqlLite().receipt_products().create(get_test_db_connection())
    SqlLite().receipts().create(get_test_db_connection())
    SqlLite().products().create(get_test_db_connection())
    SqlLite().units().create(get_test_db_connection())

    set_up_rotes(api)

    return api
