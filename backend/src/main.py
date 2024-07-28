from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")


class Section(BaseModel):
    id: int
    name: str
    type: str
    code: str
    parent_section_id: Optional[int]
    children: List['Section'] = []

    class Config:
        orm_mode = True


class Work(BaseModel):
    id: int
    code: str
    end_name: str
    measure_unit: str

    class Config:
        orm_mode = True


class NameGroup(BaseModel):
    id: int
    begin_name: str

    class Config:
        orm_mode = True


# Database connection
def get_db_connection():
    try:
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")

        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise


def fetch_sections(substring):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """SELECT * FROM search_all_by_substring(%s)"""

    cur.execute(query, (substring,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def fetch_children(parent_id):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """SELECT id, name, type, code, parent_section_id FROM section WHERE parent_section_id = %s ORDER BY id"""

    cur.execute(query, (parent_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def fetch_root_sections():
    conn = get_db_connection()
    cur = conn.cursor()

    query = """SELECT id, name, type, code, parent_section_id FROM section WHERE parent_section_id IS NULL ORDER BY id"""

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def fetch_namegroups(section_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """SELECT ng.id, ng.begin_name
               FROM name_group ng
               WHERE ng.section_id = %s ORDER BY ng.id"""
    cur.execute(query, (section_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def fetch_works(namegroup_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """SELECT w.id, w.code, w.end_name, w.measure_unit
               FROM work w
               WHERE w.name_group_id = %s ORDER BY w.id"""
    cur.execute(query, (namegroup_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def build_hierarchy(rows):
    sections = {}
    for row in rows:
        sections[row[0]] = {
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'code': row[3],
            'parent_section_id': row[4],
            'children': []
        }

    root = []
    for section in sorted(sections.values(), key=lambda x: x['id']):
        parent_id = section['parent_section_id']
        if parent_id is None:
            root.append(section)
        else:
            sections[parent_id]['children'].append(section)

    return root


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_model=List[Section])
def search_sections(query: str):
    try:
        rows = fetch_sections(query)
        hierarchy = build_hierarchy(rows)
        return hierarchy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/children", response_model=List[Section])
def get_children(parent_id: int):
    try:
        rows = fetch_children(parent_id)
        sections = [
            {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'code': row[3],
                'parent_section_id': row[4],
                'children': []
            }
            for row in rows
        ]
        return sections
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/root-sections", response_model=List[Section])
def get_root_sections():
    try:
        rows = fetch_root_sections()
        sections = [
            {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'code': row[3],
                'parent_section_id': row[4],
                'children': []
            }
            for row in rows
        ]
        return sections
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/section/{section_id}/namegroups", response_model=List[NameGroup])
def get_section_namegroups(section_id: int):
    try:
        rows = fetch_namegroups(section_id)
        namegroups = [
            NameGroup(id=row[0], begin_name=row[1])
            for row in rows
        ]
        return namegroups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namegroup/{namegroup_id}/works", response_model=List[Work])
def get_namegroup_works(namegroup_id: int):
    try:
        rows = fetch_works(namegroup_id)
        works = [
            Work(id=row[0], code=row[1], end_name=row[2], measure_unit=row[3])
            for row in rows
        ]
        return works
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class Item(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True


class WorkResourceData(BaseModel):
    resource_id: Optional[int]
    abstract_resource_id: Optional[int]
    service_resource_id: Optional[int]
    quantity: str
    measure_unit: Optional[str]
    resource_code: Optional[str]
    resource_end_name: Optional[str]
    abstract_resource_code: Optional[str]
    abstract_resource_name: Optional[str]
    service_resource_code: Optional[str]
    service_resource_name: Optional[str]

    class Config:
        orm_mode = True


class WorkDetail(BaseModel):
    id: int
    code: str
    end_name: str
    measure_unit: Optional[str]
    nr: Optional[str]
    sp: Optional[str]
    items: List[Item]
    resources: List[WorkResourceData]

    class Config:
        orm_mode = True


@app.get("/work/{work_id}", response_model=WorkDetail)
def get_work_data(work_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        work_query = """SELECT id, code, end_name, measure_unit, nr, sp FROM work WHERE id = %s"""
        cur.execute(work_query, (work_id,))
        work_row = cur.fetchone()

        if not work_row:
            raise HTTPException(status_code=404, detail="Work not found")

        items_query = """
        SELECT i.id, i.text
        FROM item i
        JOIN work_item wi ON i.id = wi.item_id
        WHERE wi.work_id = %s
        """
        cur.execute(items_query, (work_id,))
        items_rows = cur.fetchall()
        items = [Item(id=row[0], text=row[1]) for row in items_rows]

        resources_query = """
        SELECT 
            wr.resource_id, wr.abstract_resource_id, wr.service_resource_id, wr.quantity, wr.measure_unit,
            r.code as resource_code, r.end_name as resource_end_name,
            ar.code as abstract_resource_code, ar.name as abstract_resource_name,
            sr.code as service_resource_code, sr.name as service_resource_name
        FROM work_resource wr
        LEFT JOIN resource r ON wr.resource_id = r.id
        LEFT JOIN abstract_resource ar ON wr.abstract_resource_id = ar.id
        LEFT JOIN service_resource sr ON wr.service_resource_id = sr.id
        WHERE wr.work_id = %s
        """
        cur.execute(resources_query, (work_id,))
        resources_rows = cur.fetchall()
        resources = [
            WorkResourceData(
                resource_id=row[0],
                abstract_resource_id=row[1],
                service_resource_id=row[2],
                quantity=row[3],
                measure_unit=row[4],
                resource_code=row[5],
                resource_end_name=row[6],
                abstract_resource_code=row[7],
                abstract_resource_name=row[8],
                service_resource_code=row[9],
                service_resource_name=row[10]
            )
            for row in resources_rows
        ]

        cur.close()
        conn.close()

        return WorkDetail(
            id=work_row[0],
            code=work_row[1],
            end_name=work_row[2],
            measure_unit=work_row[3],
            nr=work_row[4],
            sp=work_row[5],
            items=items,
            resources=resources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
