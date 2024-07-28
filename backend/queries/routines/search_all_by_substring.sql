create function search_all_by_substring(query text)
    returns TABLE
            (
                id                integer,
                name              text,
                type              text,
                code              text,
                parent_section_id integer
            )
    language plpgsql
as
$$
/* Выполняет поиск в таблице section и связанных с ней таблицах (name_group, work, item), и возвращает иерархию найденных секций. Поиск осуществляется по переданному текстовому запросу query.
Функция рекурсивно строит иерархию секций, возвращая уникальные результаты.

Параметры:
- query (TEXT): текстовый запрос для поиска.

Результат:
- Таблица с колонками: id, name, type, code, parent_section_id.
 */
BEGIN
    RETURN QUERY
        WITH RECURSIVE section_hierarchy AS (
            -- Основной поиск в таблице section
            SELECT s.id, s.name::TEXT, s.type::TEXT, s.code::TEXT, s.parent_section_id
            FROM section s
            WHERE s.name ILIKE '%' || query || '%'

            UNION

            -- Поиск в таблице name_group
            SELECT s.id, s.name::TEXT, s.type::TEXT, s.code::TEXT, s.parent_section_id
            FROM section s
                     JOIN name_group ng ON ng.section_id = s.id
            WHERE ng.begin_name ILIKE '%' || query || '%'

            UNION

            -- Поиск в таблице work
            SELECT s.id, s.name::TEXT, s.type::TEXT, s.code::TEXT, s.parent_section_id
            FROM section s
                     JOIN name_group ng ON ng.section_id = s.id
                     JOIN work w ON w.name_group_id = ng.id
            WHERE w.end_name ILIKE '%' || query || '%'

            UNION

            -- Поиск в таблице item
            SELECT s.id, s.name::TEXT, s.type::TEXT, s.code::TEXT, s.parent_section_id
            FROM section s
                     JOIN name_group ng ON ng.section_id = s.id
                     JOIN work w ON w.name_group_id = ng.id
                     JOIN work_item wi ON wi.work_id = w.id
                     JOIN item i ON i.id = wi.item_id
            WHERE i.text ILIKE '%' || query || '%'

            UNION

            -- Рекурсивный запрос для получения полной иерархии
            SELECT s.id, s.name::TEXT, s.type::TEXT, s.code::TEXT, s.parent_section_id
            FROM section s
                     JOIN section_hierarchy sh ON s.id = sh.parent_section_id)
        SELECT DISTINCT *
        FROM section_hierarchy
        ORDER BY id;
END;
$$;

alter function search_all_by_substring(text) owner to root;
