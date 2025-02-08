import sqlite3
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from DB.DAO import SqlLite, get_db


class Receipt(BaseModel):
    status: str


receipts_api = APIRouter()


@receipts_api.post("", status_code=201)
def create_receipt(db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    sql = SqlLite()
    receipt = sql.receipts()
    receipt_id = str(uuid4())
    receipt.add(receipt_id, db)
    db.close()
    return JSONResponse(
        status_code=201,
        content={
            "receipt": {"id": receipt_id, "status": "open", "products": [], "total": 0}
        },
    )


@receipts_api.patch("/{receipt_id}", status_code=200)
def close_receipt(
    receipt_id: str, update: Receipt, db: sqlite3.Connection = Depends(get_db)
) -> JSONResponse:
    sql = SqlLite()
    receipt = sql.receipts()
    try:
        receipt.update(update, receipt_id, db)
        return JSONResponse(status_code=200, content={})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        db.close()


@receipts_api.get("/{receipt_id}")
def get_receipt(
    receipt_id: str, db: sqlite3.Connection = Depends(get_db)
) -> dict[str, Any]:
    sql = SqlLite()
    rp = sql.receipt_products()
    try:
        res = rp.get_receipt_summery(receipt_id, db)
        return res.model_dump()
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Receipt with id<{receipt_id}> does not exists.",
        )
    finally:
        db.close()


@receipts_api.delete("/{receipt_id}")
def delete_receipt(
    receipt_id: str, db: sqlite3.Connection = Depends(get_db)
) -> JSONResponse:
    sql = SqlLite()
    receipt = sql.receipts()
    try:
        receipt.delete(receipt_id, db)
        return JSONResponse(status_code=200, content={})
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    finally:
        db.close()
