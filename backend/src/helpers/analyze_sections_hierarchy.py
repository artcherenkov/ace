from lxml import etree
import collections
from collections import defaultdict

# Путь к вашему XML файлу
file_path = '../../initial_normative_data/ФЕРм.xml'


# Функция для парсинга XML и вывода атрибутов секций с отступами
def parse_and_print_sections(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()

    def recursive_print(element, level=0):
        if element.tag == 'Section':
            type_attr = element.attrib.get('Type', 'Unknown')
            code_attr = element.attrib.get('Code', 'Unknown')
            indent = '  ' * level

            if type_attr == 'Таблица':
                # Увеличиваем счетчик таблиц
                table_count[0] += 1
                last_table_code[0] = code_attr
            else:
                # Если есть собранные таблицы, выводим их
                if table_count[0] > 0:
                    print(f"{last_indent[0]}Таблица {last_table_code[0]} (collapsed {table_count[0]} tables)")
                    table_count[0] = 0
                print(f"{indent}{type_attr} {code_attr}")
            last_indent[0] = indent

        for child in element:
            recursive_print(child, level + 1)

        if element == root and table_count[0] > 0:
            # Выводим оставшиеся таблицы
            print(f"{last_indent[0]}Таблица {last_table_code[0]} (collapsed {table_count[0]})")
            table_count[0] = 0

    table_count = [0]
    last_table_code = [None]
    last_indent = ['']
    recursive_print(root)


# Функция для парсинга XML и сбора статистики
def parse_and_collect_statistics(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()

    # Структура для хранения статистики
    statistics = collections.defaultdict(lambda: collections.defaultdict(int))

    def recursive_collect(element, level=0):
        if element.tag == 'Section':
            type_attr = element.attrib.get('Type', 'Unknown')
            statistics[level][type_attr] += 1

        for child in element:
            recursive_collect(child, level + 1)

    recursive_collect(root)
    return statistics


# Функция для парсинга XML и сбора уникальных цепочек с их количеством
def parse_and_collect_chains(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()

    # Словарь для хранения уникальных цепочек и их количества
    chain_counts = defaultdict(int)

    def recursive_collect(element, current_chain):
        if element.tag == 'Section':
            type_attr = element.attrib.get('Type', 'Unknown')
            current_chain.append(type_attr)

            # Если цепочка начинается со "Сборника" и заканчивается "Таблицей", увеличиваем счетчик
            if current_chain[0] == 'Сборник' and type_attr == 'Таблица':
                chain_counts[tuple(current_chain)] += 1

        for child in element:
            recursive_collect(child, current_chain[:])

    recursive_collect(root, [])
    return chain_counts


# Парсинг и вывод секций
parse_and_print_sections(file_path)

# Сбор статистики
statistics = parse_and_collect_statistics(file_path)
for level, types in sorted(statistics.items()):
    print(f"Level {level}:")
    for type_attr, count in sorted(types.items()):
        print(f"  Type: {type_attr}, Count: {count}")

# Сбор уникальных цепочек с их количеством
chain_counts = parse_and_collect_chains(file_path)
print("Unique chains with counts:")
for chain, count in sorted(chain_counts.items()):
    print(f"{' -> '.join(chain)}: {count}")
