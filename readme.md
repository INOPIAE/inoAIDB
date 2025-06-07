# inoAIDB



## Settings

### Test

$env:APP_ENV = "test"
python -m pytest --cov=app --cov-report=term-missing

### Production

$env:APP_ENV="default"
uvicorn app.main:app --reload
