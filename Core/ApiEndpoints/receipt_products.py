import sqlite3
from typing import List

from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from Core.ApiEndpoints.receipts import receipts_api
from DB.DAO import SqlLite, get_db

sales_api = APIRouter()


class ReceiptProducts(BaseModel):
    receipt_id: str
    product_id: str
    quantity: int
    price: int
    total: int


class ProductRequest(BaseModel):
    id: str
    quantity: int


class ProductResponse(BaseModel):
    id: str
    quantity: int
    price: int
    total: int


class ReceiptResponse(BaseModel):
    id: str
    status: str
    products: List[ProductResponse]
    total: int


@sales_api.get("")
def get_sales_report(db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    sql = SqlLite()
    rp = sql.receipt_products()
    summ = rp.getSummary(db)
    return JSONResponse(
        status_code=200,
        content={"sales": {"n_receipts": summ[0], "revenue": summ[1]}},
    )


@receipts_api.post("/{receipt_id}/products", response_model=ReceiptResponse)
async def add_product_to_receipt_endpoint(
    receipt_id: str,
    product_request: ProductRequest,
    db: sqlite3.Connection = Depends(get_db),
) -> ReceiptResponse:
    sql = SqlLite()
    rp = sql.receipt_products()
    try:
        rc = sql.receipts().get_by_id(receipt_id, db)
    except ValueError:
        db.close()
        raise HTTPException(
            status_code=404, detail=f"Receipt by id<{receipt_id}> does not exists"
        )
    if rc.status != "open":
        db.close()
        raise HTTPException(
            status_code=404,
            detail=f"Receipt by id<{receipt_id}> is closed",
        )
    try:
        prod = sql.products().get_by_id(product_request.id, db)
    except ValueError:
        db.close()
        raise HTTPException(
            status_code=404,
            detail=f"Product by id <{product_request.id}> does not exists",
        )
    rp.update(
        ReceiptProducts(
            receipt_id=receipt_id,
            product_id=product_request.id,
            quantity=product_request.quantity,
            price=prod.price,
            total=prod.price * product_request.quantity,
        ),
        db,
    )
    res = rp.get_receipt_summery(receipt_id, db)
    db.close()
    return res
