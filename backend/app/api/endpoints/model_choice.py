from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import ModelChoiceCreate, ModelChoiceOut, ModelChoiceUpdate
from app.models import ModelChoice, User
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ModelChoiceOut)
def create_model_choices(mc: ModelChoiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_mc = db.query(ModelChoice).filter(ModelChoice.name == mc.name).first()
    if db_mc:
        raise HTTPException(status_code=400, detail="Model choice already exists")
    new_mc = ModelChoice(**mc.dict())
    db.add(new_mc)
    db.commit()
    db.refresh(new_mc)
    return new_mc

@router.get("/", response_model=list[ModelChoiceOut])
def read_model_choices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ModelChoice).order_by(ModelChoice.name.asc()).offset(skip).limit(limit).all()


@router.get("/{modelchoice_id}", response_model=ModelChoiceOut)
def read_model_choice(modelchoice_id: int, db: Session = Depends(get_db)):
    mc = db.query(ModelChoice).filter(ModelChoice.id == modelchoice_id).first()
    if not mc:
        raise HTTPException(status_code=404, detail="Model choice not found")
    return mc


@router.put("/{modelchoice_id}", response_model=ModelChoiceOut)
def update_model_choices(modelchoice_id: int, updates: ModelChoiceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_mc = db.query(ModelChoice).filter(ModelChoice.name == updates.name).first()
    if db_mc:
        raise HTTPException(status_code=400, detail="Model choice already exists")
    mc = db.query(ModelChoice).filter(ModelChoice.id == modelchoice_id).first()
    if not mc:
        raise HTTPException(status_code=404, detail="Model choice not found")

    for key, value in updates.dict().items():
        setattr(mc, key, value)

    db.commit()
    db.refresh(mc)
    return mc
