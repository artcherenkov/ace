import xml.etree.ElementTree as ET
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, Text, Date, Time, Table
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Настройки базы данных
DATABASE_URL = "postgresql://root:root@localhost:5432/construction_estimating"

# Создание базы данных и сессии
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Ассоциативная таблица для связи Work и Item
work_item_link = Table('work_item', Base.metadata,
                       Column('work_id', Integer, ForeignKey('work.id'), primary_key=True),
                       Column('item_id', Integer, ForeignKey('item.id'), primary_key=True)
                       )


# Определение моделей
class BaseModel(Base):
    __tablename__ = "base"
    id = Column(Integer, primary_key=True)
    price_level = Column(String)
    creation_date = Column(Date)
    creation_time = Column(Time)
    program_name = Column(String)
    base_name = Column(String)
    base_type = Column(String)
    decree = Column(Text)
    resource_categories = relationship("ResourceCategory", back_populates="base")
    sections = relationship("Section", back_populates="base")


class ResourceCategory(Base):
    __tablename__ = "resource_category"
    id = Column(Integer, primary_key=True)
    type = Column(String)
    code_prefix = Column(String)
    base_id = Column(Integer, ForeignKey("base.id"))
    base = relationship("BaseModel", back_populates="resource_categories")
    sections = relationship("Section", back_populates="resource_category")


class Section(Base):
    __tablename__ = "section"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    type = Column(String)
    code = Column(String)
    parent_section_id = Column(Integer, ForeignKey("section.id"), nullable=True)
    base_id = Column(Integer, ForeignKey("base.id"))
    resource_category_id = Column(Integer, ForeignKey("resource_category.id"), nullable=True)
    base = relationship("BaseModel", back_populates="sections")
    resource_category = relationship("ResourceCategory", back_populates="sections")
    children = relationship("Section", backref="parent", remote_side=[id])
    name_groups = relationship("NameGroup", back_populates="section")


class NameGroup(Base):
    __tablename__ = "name_group"
    id = Column(Integer, primary_key=True)
    begin_name = Column(Text)
    section_id = Column(Integer, ForeignKey("section.id"))
    section = relationship("Section", back_populates="name_groups")
    works = relationship("Work", back_populates="name_group")


class Work(Base):
    __tablename__ = "work"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    end_name = Column(Text)
    measure_unit = Column(String)
    name_group_id = Column(Integer, ForeignKey("name_group.id"))
    name_group = relationship("NameGroup", back_populates="works")
    nr = Column(String)
    sp = Column(String)
    prices = relationship("Price", back_populates="work")
    items = relationship("Item", secondary=work_item_link, back_populates="works")
    resources = relationship("WorkResource", back_populates="work")


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    text = Column(Text, unique=True)
    works = relationship("Work", secondary=work_item_link, back_populates="items")


class WorkResource(Base):
    __tablename__ = "work_resource"
    id = Column(Integer, primary_key=True)
    work_id = Column(Integer, ForeignKey("work.id"))
    resource_id = Column(Integer, ForeignKey("resource.id"), nullable=True)
    abstract_resource_id = Column(Integer, ForeignKey("abstract_resource.id"), nullable=True)
    service_resource_id = Column(Integer, ForeignKey("service_resource.id"), nullable=True)
    quantity = Column(String)
    measure_unit = Column(String)
    work = relationship("Work", back_populates="resources")


class Resource(Base):
    __tablename__ = "resource"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    end_name = Column(Text)
    measure_unit = Column(String)


class AbstractResource(Base):
    __tablename__ = "abstract_resource"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(Text)
    measure_unit = Column(String)


class ServiceResource(Base):
    __tablename__ = "service_resource"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    category = Column(String)
    name = Column(Text)
    measure_unit = Column(String)
    type = Column(String)


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    cost = Column(Numeric)
    salary_mach = Column(Numeric)
    salary = Column(Numeric)
    machines = Column(Numeric)
    materials = Column(Numeric)
    work_id = Column(Integer, ForeignKey("work.id"))
    work = relationship("Work", back_populates="prices")
    corrections = relationship("Correction", back_populates="price")


class Correction(Base):
    __tablename__ = "correction"
    id = Column(Integer, primary_key=True)
    coeff = Column(Numeric)
    from_field = Column(String)
    to_field = Column(String)
    price_id = Column(Integer, ForeignKey("price.id"))
    price = relationship("Price", back_populates="corrections")


# Создание таблиц
Base.metadata.create_all(engine)

# Список для хранения ошибок
errors = []


# Функция для парсинга и миграции данных из XML в PostgreSQL
def migrate_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    base = BaseModel(
        price_level=root.attrib.get('PriceLevel'),
        creation_date=root.attrib.get('CreationDate'),
        creation_time=root.attrib.get('CreationTime'),
        program_name=root.attrib.get('ProgramName'),
        base_name=root.attrib.get('BaseName'),
        base_type=root.attrib.get('BaseType'),
        decree=root.find('Decrees').find('Decree').attrib.get('Name')
    )
    session.add(base)
    session.commit()

    print(f"Base model added with ID: {base.id}")

    resource_directory = root.find('ResourcesDirectory')
    for resource_category_data in resource_directory.findall('ResourceCategory'):
        resource_category = ResourceCategory(
            type=resource_category_data.get('Type'),
            code_prefix=resource_category_data.get('CodePrefix'),
            base_id=base.id
        )
        session.add(resource_category)
        session.commit()

        print(f"ResourceCategory added with ID: {resource_category.id}")

        for section_data in resource_category_data.findall('Section'):
            section = parse_section(section_data, resource_category.id, base.id, None)
            session.add(section)
            session.commit()


def parse_section(section_data, resource_category_id, base_id, parent_section_id):
    section = Section(
        name=section_data.get('Name'),
        type=section_data.get('Type'),
        code=section_data.get('Code'),
        parent_section_id=parent_section_id,
        base_id=base_id,
        resource_category_id=resource_category_id
    )
    session.add(section)
    session.commit()

    print(f"Section added with ID: {section.id}")

    for subsection_data in section_data.findall('Section'):
        subsection = parse_section(subsection_data, resource_category_id, base_id, section.id)
        session.add(subsection)

    for name_group_data in section_data.findall('NameGroup'):
        name_group = NameGroup(
            begin_name=name_group_data.get('BeginName'),
            section_id=section.id
        )
        session.add(name_group)
        session.commit()

        print(f"NameGroup added with ID: {name_group.id}")

        for work_data in name_group_data.findall('Work'):
            work = parse_work(work_data, name_group.id)
            session.add(work)
            session.commit()

    return section


def parse_work(work_data, name_group_id):
    nr_sp_data = work_data.find('NrSp')
    nr = None
    sp = None
    if nr_sp_data is not None:
        reason_item = nr_sp_data.find('ReasonItem')
        if reason_item is not None:
            nr = reason_item.get('Nr')
            sp = reason_item.get('Sp')

    work = Work(
        code=work_data.get('Code'),
        end_name=work_data.get('EndName'),
        measure_unit=work_data.get('MeasureUnit'),
        name_group_id=name_group_id,
        nr=nr,
        sp=sp
    )
    session.add(work)
    session.commit()

    print(f"Work added with ID: {work.id}, Nr: {work.nr}, Sp: {work.sp}")

    for item_data in work_data.find('Content').findall('Item'):
        try:
            item = session.query(Item).filter_by(text=item_data.get('Text')).first()
            if not item:
                item = Item(text=item_data.get('Text'))
                session.add(item)
                session.commit()
                print(f"Item added with ID: {item.id}")

            if item not in work.items:
                work.items.append(item)
                session.commit()
            else:
                raise Exception(f"Duplicate item {item_data.get('Text')} for work {work_data.get('Code')}")
        except Exception as e:
            error_message = f"Error adding item {item_data.get('Text')} to work {work_data.get('Code')}: {e}"
            errors.append(error_message)
            print(f"\033[91m{error_message}\033[0m")  # Вывод ошибки красным цветом

    for resource_data in work_data.find('Resources').findall('Resource'):
        try:
            resource = session.query(Resource).filter_by(code=resource_data.get('Code')).first()
            if not resource:
                resource = Resource(
                    code=resource_data.get('Code'),
                    end_name=resource_data.get('EndName'),
                    measure_unit=resource_data.get('MeasureUnit')
                )
                session.add(resource)
                session.commit()
                print(f"Resource added with ID: {resource.id}")

            existing_work_resource = session.query(WorkResource).filter_by(work_id=work.id,
                                                                           resource_id=resource.id).first()
            if existing_work_resource:
                raise Exception(f"Duplicate resource {resource_data.get('Code')} for work {work_data.get('Code')}")

            work_resource = WorkResource(
                work_id=work.id,
                resource_id=resource.id,
                quantity=resource_data.get('Quantity'),
                measure_unit=resource_data.get('MeasureUnit')
            )
            session.add(work_resource)
            session.commit()
        except Exception as e:
            error_message = f"Error adding resource {resource_data.get('Code')} to work {work_data.get('Code')}: {e}"
            errors.append(error_message)
            print(f"\033[91m{error_message}\033[0m")  # Вывод ошибки красным цветом

    for abstract_resource_data in work_data.find('Resources').findall('AbstractResource'):
        try:
            abstract_resource = session.query(AbstractResource).filter_by(
                code=abstract_resource_data.get('Code')).first()
            if not abstract_resource:
                abstract_resource = AbstractResource(
                    code=abstract_resource_data.get('Code'),
                    name=abstract_resource_data.get('Name'),
                    measure_unit=abstract_resource_data.get('MeasureUnit')
                )
                session.add(abstract_resource)
                session.commit()
                print(f"AbstractResource added with ID: {abstract_resource.id}")

            existing_work_resource = session.query(WorkResource).filter_by(work_id=work.id,
                                                                           abstract_resource_id=abstract_resource.id).first()
            if existing_work_resource:
                raise Exception(
                    f"Duplicate abstract resource {abstract_resource_data.get('Code')} for work {work_data.get('Code')}")

            work_resource = WorkResource(
                work_id=work.id,
                abstract_resource_id=abstract_resource.id,
                quantity=abstract_resource_data.get('Quantity'),
                measure_unit=abstract_resource_data.get('MeasureUnit')
            )
            session.add(work_resource)
            session.commit()
        except Exception as e:
            error_message = f"Error adding abstract resource {abstract_resource_data.get('Code')} to work {work_data.get('Code')}: {e}"
            errors.append(error_message)
            print(f"\033[91m{error_message}\033[0m")  # Вывод ошибки красным цветом

    for service_resource_data in work_data.find('Resources').findall('ServiceResource'):
        try:
            service_resource = session.query(ServiceResource).filter_by(code=service_resource_data.get('Code')).first()
            if not service_resource:
                service_resource = ServiceResource(
                    code=service_resource_data.get('Code'),
                    category=service_resource_data.get('Category'),
                    name=service_resource_data.get('Name'),
                    measure_unit=service_resource_data.get('MeasureUnit'),
                    type=service_resource_data.get('Type')
                )
                session.add(service_resource)
                session.commit()
                print(f"ServiceResource added with ID: {service_resource.id}")

            existing_work_resource = session.query(WorkResource).filter_by(work_id=work.id,
                                                                           service_resource_id=service_resource.id).first()
            if existing_work_resource:
                raise Exception(
                    f"Duplicate service resource {service_resource_data.get('Code')} for work {work_data.get('Code')}")

            work_resource = WorkResource(
                work_id=work.id,
                service_resource_id=service_resource.id,
                quantity=service_resource_data.get('Quantity'),
                measure_unit=service_resource_data.get('MeasureUnit')
            )
            session.add(work_resource)
            session.commit()
        except Exception as e:
            error_message = f"Error adding service resource {service_resource_data.get('Code')} to work {work_data.get('Code')}: {e}"
            errors.append(error_message)
            print(f"\033[91m{error_message}\033[0m")  # Вывод ошибки красным цветом

    for price_data in work_data.find('Prices').findall('Price'):
        price = Price(
            cost=price_data.get('Cost'),
            salary_mach=price_data.get('SalaryMach'),
            salary=price_data.get('Salary'),
            machines=price_data.get('Machines'),
            materials=price_data.get('Materials'),
            work_id=work.id
        )
        session.add(price)
        session.commit()

        print(f"Price added with ID: {price.id}")

        for correction_data in price_data.findall('Correction'):
            correction = Correction(
                coeff=correction_data.get('Coeff'),
                from_field=correction_data.get('From'),
                to_field=correction_data.get('To'),
                price_id=price.id
            )
            session.add(correction)
            session.commit()

            print(f"Correction added with ID: {correction.id}")

    return work


# Запуск миграции
migrate_data('../initial_normative_data/ФЕР.xml')

# Вывод всех ошибок после завершения миграции
if errors:
    print("\033[91mErrors occurred during data migration:\033[0m")
    for error in errors:
        print(f"\033[91m{error}\033[0m")
else:
    print("Data migration completed without errors.")
