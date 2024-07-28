import os

import psycopg2

from dotenv import load_dotenv

load_dotenv()


def fetch_sections(substring):
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
    cur = conn.cursor()

    query = """
    WITH RECURSIVE section_hierarchy AS (
        SELECT
            id,
            name,
            type,
            code,
            parent_section_id
        FROM
            section
        WHERE
            name ILIKE %s

        UNION

        SELECT
            s.id,
            s.name,
            s.type,
            s.code,
            s.parent_section_id
        FROM
            section s
            JOIN section_hierarchy sh ON s.id = sh.parent_section_id
    )
    SELECT DISTINCT * FROM section_hierarchy order by section_hierarchy.id;
    """

    cur.execute(query, (f'%{substring}%',))
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
    for section in sections.values():
        parent_id = section['parent_section_id']
        if parent_id is None:
            root.append(section)
        else:
            sections[parent_id]['children'].append(section)

    return root


def print_hierarchy(sections, level=0):
    for section in sections:
        print('  ' * level + f"Type: {section['type']}, Code: {section['code']}, Name: {section['name']}")
        print_hierarchy(section['children'], level + 1)


def main():
    substring = ""  # Введите подстроку для поиска
    rows = fetch_sections(substring)
    hierarchy = build_hierarchy(rows)
    print_hierarchy(hierarchy)


if __name__ == "__main__":
    main()
