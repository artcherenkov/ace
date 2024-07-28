from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from .database import Database
from .dal import SectionDAL
from .services import SectionService
from .models import Section, NameGroup, Work, WorkDetail

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize dependencies
db = Database()
section_dal = SectionDAL(db)
section_service = SectionService(section_dal)


# API Endpoints
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_model=List[Section])
def search_sections(query: str):
    try:
        return section_service.get_sections(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/children", response_model=List[Section])
def get_children(parent_id: int):
    try:
        return section_service.get_children(parent_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/root-sections", response_model=List[Section])
def get_root_sections():
    try:
        return section_service.get_root_sections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/section/{section_id}/namegroups", response_model=List[NameGroup])
def get_section_namegroups(section_id: int):
    try:
        return section_service.get_namegroups(section_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namegroup/{namegroup_id}/works", response_model=List[Work])
def get_namegroup_works(namegroup_id: int):
    try:
        return section_service.get_works(namegroup_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/work/{work_id}", response_model=WorkDetail)
def get_work_data(work_id: int):
    try:
        return section_service.get_work_detail(work_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
