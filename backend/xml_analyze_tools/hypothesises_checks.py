import xml.etree.ElementTree as ET
from collections import defaultdict

# Пути к файлам XML
file_paths = [
    '../../initial_normative_data/ФЕР.xml',
    '../../initial_normative_data/ФЕРм.xml',
    '../../initial_normative_data/ФЕРмр.xml',
    '../../initial_normative_data/ФЕРп.xml',
    '../../initial_normative_data/ФЕРр.xml'
]

# Флаги для включения/выключения проверок гипотез
CHECK_MULTIPLE_NAMEGROUPS = False
CHECK_UNIQUE_NAMEGROUPS_COUNTS = True
CHECK_MULTIPLE_NRSP = False
CHECK_NESTED_WORK = False
CHECK_UNIQUE_ATTRIBUTES_ABSTRACT = False
CHECK_UNIQUE_ATTRIBUTES_SERVICE = False
CHECK_SINGLE_PRICE = False
CHECK_WORK_HAS_PRICES = False
CHECK_SINGLE_CORRECTION = False


def parse_xml(file_path):
    """Парсит XML-файл и возвращает его корневой элемент."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


def count_sections_with_multiple_namegroups(root):
    """Считает количество секций с несколькими группами имен."""
    count = 0
    for section in root.findall(".//Section"):
        name_groups = section.findall("NameGroup")
        if len(name_groups) > 1:
            count += 1
    print(f"Sections with multiple NameGroups: {count}")
    return count


def count_unique_namegroup_counts(root):
    """Считает уникальные количества групп имен в секциях с Type="Таблица"."""
    namegroup_counts = defaultdict(int)
    for section in root.findall(".//Section"):
        if section.attrib.get("Type") == "Таблица":
            name_groups = section.findall("NameGroup")
            namegroup_counts[len(name_groups)] += 1
    print("Unique NameGroup counts in sections with Type='Таблица':")
    for count, occurrences in sorted(namegroup_counts.items(), key=lambda item: item[0]):
        print(f" - {count} NameGroup(s): {occurrences} section(s)")
    return namegroup_counts


def count_work_with_multiple_nrsp(root):
    """Считает количество работ с более чем одним элементом NrSp."""
    count = 0
    for work in root.findall(".//Work"):
        nrsp_elements = work.findall("NrSp")
        if len(nrsp_elements) != 1:
            count += 1
    print(f"Works with multiple NrSp elements: {count}")
    return count


def count_work_with_nested_work(root):
    """Считает количество работ, содержащих вложенные работы."""
    count = 0
    for work in root.findall(".//Work"):
        nested_works = work.findall(".//Work")
        if len(nested_works) > 1:  # Проверяем > 1, так как findall(".//Work") включает текущий элемент <Work>
            count += 1
    print(f"Works with nested Works: {count}")
    return count


def find_unique_attribute_combinations(root, tag):
    """Находит уникальные сочетания атрибутов для заданного тега."""
    attribute_combinations = set()
    for element in root.findall(f".//{tag}"):
        attribute_combination = tuple(element.attrib.keys())
        attribute_combinations.add(attribute_combination)
    print(f"Unique attribute combinations for tag {tag}:")
    for combination in attribute_combinations:
        print(combination)
    return attribute_combinations


def count_prices_with_multiple_price(root):
    """Считает количество записей с более чем одной ценой."""
    count = 0
    for prices in root.findall(".//Prices"):
        price_elements = prices.findall("Price")
        if len(price_elements) != 1:
            count += 1
    print(f"Prices with multiple Price elements: {count}")
    return count


def find_work_without_prices(root):
    """Находит работы без указания цен."""
    work_without_prices = []
    for work in root.findall(".//Work"):
        prices_elements = work.findall("Prices")
        if len(prices_elements) == 0:
            work_without_prices.append(work.attrib.get('Code', 'Unknown'))
    print(f"Works without Prices ({len(work_without_prices)}):")
    for code in work_without_prices:
        print(f" - {code}")
    return work_without_prices


def count_prices_with_multiple_or_no_correction(root):
    """Считает количество цен с более чем одной корректировкой или без корректировок."""
    count = 0
    for price in root.findall(".//Price"):
        correction_elements = price.findall("Correction")
        if len(correction_elements) > 1:
            count += 1
    print(f"Prices with multiple or no Correction elements: {count}")
    return count


def check_hypotheses_for_file(file_path):
    """Проверяет гипотезы для заданного файла и выводит результаты."""
    root = parse_xml(file_path)
    print(f"Результаты проверки для файла: {file_path.split('/')[-1]}")

    if CHECK_MULTIPLE_NAMEGROUPS:
        count_sections_with_multiple_namegroups(root)
    if CHECK_UNIQUE_NAMEGROUPS_COUNTS:
        count_unique_namegroup_counts(root)
    if CHECK_MULTIPLE_NRSP:
        count_work_with_multiple_nrsp(root)
    if CHECK_NESTED_WORK:
        count_work_with_nested_work(root)
    if CHECK_UNIQUE_ATTRIBUTES_ABSTRACT:
        find_unique_attribute_combinations(root, "AbstractResource")
    if CHECK_UNIQUE_ATTRIBUTES_SERVICE:
        find_unique_attribute_combinations(root, "ServiceResource")
    if CHECK_SINGLE_PRICE:
        count_prices_with_multiple_price(root)
    if CHECK_WORK_HAS_PRICES:
        find_work_without_prices(root)
    if CHECK_SINGLE_CORRECTION:
        count_prices_with_multiple_or_no_correction(root)
    print("-" * 50)


def main(file_paths):
    """Основная функция, вызывающая проверки для каждого файла."""
    for file_path in file_paths:
        check_hypotheses_for_file(file_path)


if __name__ == "__main__":
    main(file_paths)
