import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []

    def recursive_parse(element, parent_path=""):
        current_path = f"{parent_path}/{element.tag}" if parent_path else element.tag
        data.append({
            "Tag": element.tag,
            "Attributes": element.attrib,
            "Text": element.text.strip() if element.text else "",
            "Path": current_path
        })
        for child in element:
            recursive_parse(child, current_path)

    recursive_parse(root)
    return data


def analyze_structure(data):
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_rows', 100)
    df = pd.DataFrame(data)
    print(df.head(100))  # Вывод первых 20 строк для проверки

    # Подсчет количества различных тегов
    tag_counts = df['Tag'].value_counts()
    print("\nTag Counts:\n", tag_counts)

    # Подсчет уникальных путей
    path_counts = df['Path'].value_counts()
    print("\nPath Counts:\n", path_counts)

    # Подсчет уникальных атрибутов для каждого тега
    attribute_counts = df.groupby('Tag')['Attributes'].apply(lambda x: x.map(str).value_counts())
    print("\nAttribute Counts:\n", attribute_counts)

    # Примеры атрибутов для каждого тега
    for tag in df['Tag'].unique():
        print(f"\nExamples of attributes for tag '{tag}':")
        examples = df[df['Tag'] == tag]['Attributes'].head(30).to_dict()
        for index, attrs in examples.items():
            print(f" - Example: {attrs}")

    # Детальное изучение каждого тега и его атрибутов
    detailed_attributes = defaultdict(dict)
    for tag in df['Tag'].unique():
        tag_df = df[df['Tag'] == tag]
        all_attributes = tag_df['Attributes'].apply(pd.Series).fillna('').astype(str)
        for column in all_attributes.columns:
            unique_values = all_attributes[column].unique()
            detailed_attributes[tag][column] = unique_values

    for tag, attributes in detailed_attributes.items():
        print(f"\nDetailed attributes for tag '{tag}':")
        for attr, values in attributes.items():
            print(f" - Attribute '{attr}' has {len(values)} unique values")
            if len(values) <= 100:
                print(f"   Values: {values}")


def main():
    file_path = '../../initial_normative_data/ФЕР.xml'  # Укажите путь к вашему XML файлу
    data = parse_xml(file_path)
    analyze_structure(data)


if __name__ == '__main__':
    main()
