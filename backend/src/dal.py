from fastapi import HTTPException

from .database import Database


class SectionDAL:
    def __init__(self, db: Database):
        self.db = db

    def fetch_sections(self, substring: str):
        query = """SELECT * FROM search_all_by_substring(%s)"""
        return self._execute_query(query, (substring,))

    def fetch_children(self, parent_id: int):
        query = """SELECT id, name, type, code, parent_section_id FROM section WHERE parent_section_id = %s ORDER BY 
        id"""
        return self._execute_query(query, (parent_id,))

    def fetch_root_sections(self):
        query = """SELECT id, name, type, code, parent_section_id FROM section WHERE parent_section_id IS NULL ORDER 
        BY id"""
        return self._execute_query(query)

    def fetch_namegroups(self, section_id: int):
        query = """SELECT id, begin_name FROM name_group WHERE section_id = %s ORDER BY id"""
        return self._execute_query(query, (section_id,))

    def fetch_works(self, namegroup_id: int):
        query = """SELECT id, code, end_name, measure_unit FROM work WHERE name_group_id = %s ORDER BY id"""
        return self._execute_query(query, (namegroup_id,))

    def fetch_work_data(self, work_id: int):
        work_query = """SELECT id, code, end_name, measure_unit, nr, sp FROM work WHERE id = %s"""
        items_query = """SELECT i.id, i.text FROM item i JOIN work_item wi ON i.id = wi.item_id WHERE wi.work_id = %s"""
        resources_query = """
            SELECT wr.resource_id, wr.abstract_resource_id, wr.service_resource_id, wr.quantity, wr.measure_unit,
                   r.code as resource_code, r.end_name as resource_end_name,
                   ar.code as abstract_resource_code, ar.name as abstract_resource_name,
                   sr.code as service_resource_code, sr.name as service_resource_name
            FROM work_resource wr
            LEFT JOIN resource r ON wr.resource_id = r.id
            LEFT JOIN abstract_resource ar ON wr.abstract_resource_id = ar.id
            LEFT JOIN service_resource sr ON wr.service_resource_id = sr.id
            WHERE wr.work_id = %s
        """
        work_row = self._execute_query(work_query, (work_id,), fetch_one=True)
        if not work_row:
            raise HTTPException(status_code=404, detail="Work not found")

        items_rows = self._execute_query(items_query, (work_id,))
        resources_rows = self._execute_query(resources_query, (work_id,))

        return work_row, items_rows, resources_rows

    def _execute_query(self, query: str, params: tuple = (), fetch_one: bool = False):
        with self.db.conn.cursor() as cur:
            cur.execute(query, params)
            if fetch_one:
                return cur.fetchone()
            return cur.fetchall()
