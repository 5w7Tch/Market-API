import sqlite3
from typing import List
from uuid import uuid4

from fastapi import HTTPException, APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from DB.DAO import SqlLite, get_db

units_api = APIRouter()


class Unit(BaseModel):
    name: str


class UnitResponse(BaseModel):
    id: str
    name: str


class UnitGroup(BaseModel):
    units: List[UnitResponse]


@units_api.post("")
def create_unit(unit: Unit, db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    sql = SqlLite()
    units_sql = sql.units()
    try:
        unit_id = str(uuid4())
        units_sql.add(
            unit,
            unit_id,
            db,
        )
        return JSONResponse(
            status_code=201, content={"unit": {"id": unit_id, "name": unit.name}}
        )
    except ValueError:
        raise HTTPException(
            status_code=409, detail=f"Unit with name<{unit.name}> already exists."
        )
    finally:
        db.close()


@units_api.get("/{unit_id}")
def get_unit(unit_id: str, db: sqlite3.Connection = Depends(get_db)) -> JSONResponse:
    sql = SqlLite()
    units_sql = sql.units()
    try:
        unit = units_sql.get_by_id(unit_id, db)
        return JSONResponse(
            status_code=200, content={"unit": {"id": unit_id, "name": unit.name}}
        )
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Unit with id<{unit_id}> does not exist."
        )
    finally:
        db.close()


@units_api.get("")
def list_units(db: sqlite3.Connection = Depends(get_db)) -> UnitGroup:
    res = SqlLite().units().readAll(db)
    db.close()
    return res
