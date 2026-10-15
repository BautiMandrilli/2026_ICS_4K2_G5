from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parents[1] / "plantillas")


@router.get("/", response_class=HTMLResponse)
def mostrar_compra(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="compra.html",
		context={},
	)
