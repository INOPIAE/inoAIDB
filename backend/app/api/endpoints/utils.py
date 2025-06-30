from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

DOCS_DIR = Path(__file__).parent.parent.parent.parent.parent / "frontend" / "public" / "hdocs"

@router.get("/page-exists")
async def page_exists(file: str = Query(...)):
    # Sicherheit: Pfad-Traversal verhindern
    if ".." in file or file.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file name")

    file_path = DOCS_DIR / file

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return JSONResponse(content={"exists": True})
