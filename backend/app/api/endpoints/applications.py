from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.schemas import ApplicationOut, ApplicationWithManufacturerOut, CreateApplication
from app.models import Application, Manufacturer, User, LanguageModel, ModelChoice
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ApplicationOut)
def create_application(application: CreateApplication, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_application = db.query(Application).filter(Application.name == application.name).first()
    if db_application:
        raise HTTPException(status_code=400, detail="Application already exists")
    manufacturer = db.query(Manufacturer).filter_by(id=application.manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manufacturer not found"
        )
    lm = db.query(LanguageModel).filter_by(id=application.languagemodel_id).first()
    if not lm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Language model not found"
        )
    mc = db.query(ModelChoice).filter_by(id=application.modelchoice_id).first()
    if not mc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model choice not found"
        )

    db_application = Application(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("/", response_model=List[ApplicationOut])
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.name.asc()).all()

@router.get("/with-manufacturer", response_model=List[ApplicationWithManufacturerOut])
def get_active_applications_with_manufacturer(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Application.id,
            Application.name,
            Application.description,
            Application.is_active,
            Application.manufacturer_id,
            Manufacturer.name.label("manufacturer_name"),
            Application.languagemodel_id,
            LanguageModel.name.label("languagemodel_name"),
            Application.modelchoice_id,
            ModelChoice.name.label("modelchoice_name"),
        )
        .join(Manufacturer, Application.manufacturer_id == Manufacturer.id)
        .join(LanguageModel, Application.languagemodel_id == LanguageModel.id)
        .join(ModelChoice, Application.modelchoice_id == ModelChoice.id)
        .filter(Application.is_active == True)
        .order_by(Application.name.asc())
        .all()
    )

    result = [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "is_active": r.is_active,
            "manufacturer_id": r.manufacturer_id,
            "manufacturer_name": r.manufacturer_name,
            "languagemodel_name": r.languagemodel_name,
            "modelchoice_name": r.modelchoice_name,
        }
        for r in rows
    ]
    return result


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    updated_data: CreateApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter_by(id=application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    manufacturer = db.query(Manufacturer).filter_by(id=updated_data.manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=400, detail="Manufacturer not found")
    lm = db.query(LanguageModel).filter_by(id=updated_data.languagemodel_id).first()
    if not lm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Language model not found"
        )
    mc = db.query(ModelChoice).filter_by(id=updated_data.modelchoice_id).first()
    if not mc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model choice not found"
        )

    for field, value in updated_data.dict().items():
        setattr(app, field, value)

    db.commit()
    db.refresh(app)
    return app


@router.get("/by-manufacturer/{manufacturer_id}", response_model=List[ApplicationOut])
def get_applications_by_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter_by(id=manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manufacturer not found"
        )
    applications = db.query(Application).filter_by(manufacturer_id=manufacturer_id).all()
    return applications
