from .dal import SectionDAL
from .models import Section, NameGroup, Work, WorkDetail, Item, WorkResourceData


class SectionService:
    def __init__(self, section_dal: SectionDAL):
        self.section_dal = section_dal

    def get_sections(self, substring: str):
        rows = self.section_dal.fetch_sections(substring)
        return self._build_hierarchy(rows)

    def get_children(self, parent_id: int):
        rows = self.section_dal.fetch_children(parent_id)
        sections = self._map_sections(rows)
        for section in sections:
            section['name'] = self._to_sentence_case(section['name'])
        return sections

    def get_root_sections(self):
        rows = self.section_dal.fetch_root_sections()
        return self._map_sections(rows)

    def get_namegroups(self, section_id: int):
        rows = self.section_dal.fetch_namegroups(section_id)
        return [NameGroup(id=row[0], begin_name=row[1]) for row in rows]

    def get_works(self, namegroup_id: int):
        rows = self.section_dal.fetch_works(namegroup_id)
        return [Work(id=row[0], code=row[1], end_name=row[2], measure_unit=row[3]) for row in rows]

    def get_work_detail(self, work_id: int):
        work_row, items_rows, resources_rows = self.section_dal.fetch_work_data(work_id)
        items = [Item(id=row[0], text=row[1]) for row in items_rows]
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

    def _map_sections(self, rows):
        return [
            {
                'id': row[0],
                'name': self._to_sentence_case(row[1]),
                'type': row[2],
                'code': row[3],
                'parent_section_id': row[4],
                'children': []
            }
            for row in rows
        ]

    def _build_hierarchy(self, rows):
        sections = {row[0]: {'id': row[0], 'name': self._to_sentence_case(row[1]), 'type': row[2], 'code': row[3],
                             'parent_section_id': row[4], 'children': []} for row in rows}
        root = []
        for section in sorted(sections.values(), key=lambda x: x['id']):
            parent_id = section['parent_section_id']
            if parent_id is None:
                root.append(section)
            else:
                sections[parent_id]['children'].append(section)
        return root

    @staticmethod
    def _to_sentence_case(text: str) -> str:
        if not text:
            return text
        return text[0].upper() + text[1:].lower() if len(text) > 1 else text.upper()
