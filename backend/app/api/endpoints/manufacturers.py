from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.database import SessionLocal
from app.schemas import ManufacturerOut, ManufacturerCreate, ManufacturerUpdate
from app.models import Manufacturer, User
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ManufacturerOut)
def create_manufacturer(manufacturer: ManufacturerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_manufacturer = db.query(Manufacturer).filter(Manufacturer.name == manufacturer.name).first()
    if db_manufacturer:
        raise HTTPException(status_code=400, detail="Manufacturer already exists")
    new_manufacturer = Manufacturer(**manufacturer.model_dump())
    db.add(new_manufacturer)
    db.commit()
    db.refresh(new_manufacturer)
    return new_manufacturer

@router.get("/", response_model=list[ManufacturerOut])
def read_manufacturers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Manufacturer).order_by(Manufacturer.name.asc()).offset(skip).limit(limit).all()

def search_manufacturers_by_similarity(db: Session, query: str, threshold: float = 0.3, limit: int = 20) -> List[Manufacturer]:
    sql = text("""
        SELECT * FROM manufacturers
        WHERE similarity(name, :query) > :threshold
        ORDER BY similarity(name, :query) DESC
        LIMIT :limit
    """)
    return db.execute(sql, {"query": query, "threshold": threshold, "limit": limit}).fetchall()

@router.get("/search", response_model=list[ManufacturerOut])
def search_manufacturers(
    q: str = Query(..., min_length=2, description="Suchbegriff"),
    db: Session = Depends(get_db)
):
    results = search_manufacturers_by_similarity(db, query=q)
    return results


@router.get("/{manufacturer_id}", response_model=ManufacturerOut)
def read_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer


@router.put("/{manufacturer_id}", response_model=ManufacturerOut)
def update_manufacturer(manufacturer_id: int, updates: ManufacturerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    for key, value in updates.model_dump().items():
        setattr(manufacturer, key, value)

    db.commit()
    db.refresh(manufacturer)
    return manufacturer


""" @router.delete("/{manufacturer_id}")
def delete_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.id == manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")

    db.delete(manufacturer)
    db.commit()
    return {"detail": "Manufacturer deleted"} """
