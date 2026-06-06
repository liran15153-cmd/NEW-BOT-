from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["tester"])

_TESTER_INDEX_PATH = Path(__file__).resolve().parents[1] / "tester" / "index.html"


@router.get("/tester", include_in_schema=False)
def get_tester() -> FileResponse:
    return FileResponse(_TESTER_INDEX_PATH, media_type="text/html")


@router.get("/tester/", include_in_schema=False)
def get_tester_with_slash() -> FileResponse:
    return get_tester()


