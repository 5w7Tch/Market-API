import sqlite3
from typing import Optional, List
from uuid import uuid4

from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from DB.DAO import SqlLite, get_db

from fastapi import Depends

products_api = APIRouter()


class Product(BaseModel):
    unit_id: str
    name: str
    barcode: str
    price: int


class ProductUpdate(BaseModel):
    price: Optional[int] = None


class ProductResponse(BaseModel):
    id: str
    unit_id: str
    name: str
    barcode: str
    price: int


class ProductGroup(BaseModel):
    products: List[ProductResponse]


@products_api.post("", status_code=201)
def create_product(
    product: Product, db: sqlite3.Connection = Depends(get_db)
) -> JSONResponse:
    sql = SqlLite()
    product_sql = sql.products()

    try:
        product_id = str(uuid4())
        product_sql.add(product, product_id, db)
        return JSONResponse(
            status_code=201,
            content={
                "product": {
                    "id": product_id,
                    "unit_id": product.unit_id,
                    "name": product.name,
                    "barcode": product.barcode,
                    "price": product.price,
                }
            },
        )
    except ValueError:
        raise HTTPException(
            status_code=409,
            detail=f"Product with barcode<{product.barcode}> already exists.",
        )
    finally:
        db.close()


@products_api.get("/{product_id}", status_code=200)
def get_product(
    product_id: str, db: sqlite3.Connection = Depends(get_db)
) -> JSONResponse:
    sql = SqlLite()
    product_sql = sql.products()
    try:
        product = product_sql.get_by_id(product_id, db)
        return JSONResponse(
            content={"product": dict(product)},
        )
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Product with id<{product_id}> does not exist."
        )
    finally:
        db.close()


@products_api.get("")
def list_products(db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    sql = SqlLite()
    product_sql = sql.products()
    products = product_sql.readAll(db)
    db.close()
    return JSONResponse(
        status_code=200,
        content=products.model_dump(),
    )


@products_api.patch("/{product_id}", status_code=200)
def update_product(
    product_id: str, update: ProductUpdate, db: sqlite3.Connection = Depends(get_db)
) -> JSONResponse:
    sql = SqlLite()
    product_sql = sql.products()

    try:
        product_sql.update_price(product_id, update.price, db)
        return JSONResponse(
            content={},
        )
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id<{product_id}> does not exists",
        )
    finally:
        db.close()
