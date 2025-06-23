from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.schemas import LanguageModelOut, LanguageModelCreate, LanguageModelUpdate
from app.models import LanguageModel, User
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[LanguageModelOut])
def read_language_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(LanguageModel).order_by(LanguageModel.name.asc()).offset(skip).limit(limit).all()

@router.get("/{language_model_id}", response_model=LanguageModelOut)
def read_language_model(language_model_id: int, db: Session = Depends(get_db)):
    lm = db.query(LanguageModel).filter(LanguageModel.id == language_model_id).first()
    if not lm:
        raise HTTPException(status_code=404, detail="Language model not found")
    return lm

@router.post("/", response_model=LanguageModelOut, status_code=status.HTTP_201_CREATED)
def create_language_model(languagemodel: LanguageModelCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_languagemodel = db.query(LanguageModel).filter(LanguageModel.name == languagemodel.name).first()
    if db_languagemodel:
        raise HTTPException(status_code=400, detail="Language model already exists")
    lm = LanguageModel(**languagemodel.dict())
    db.add(lm)
    db.commit()
    db.refresh(lm)
    return lm

@router.put("/{language_model_id}", response_model=LanguageModelOut)
def update_language_model(language_model_id: int, data: LanguageModelUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_languagemodel = db.query(LanguageModel).filter(LanguageModel.name == data.name).first()
    if db_languagemodel:
        raise HTTPException(status_code=400, detail="Language model already exists")
    lm = db.query(LanguageModel).filter(LanguageModel.id == language_model_id).first()
    if not lm:
        raise HTTPException(status_code=404, detail="Language model not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(lm, field, value)
    db.commit()
    db.refresh(lm)
    return lm
