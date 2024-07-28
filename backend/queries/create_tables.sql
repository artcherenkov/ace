-- Создание таблицы base с новым полем decree
CREATE TABLE base
(
    id            SERIAL PRIMARY KEY,
    price_level   VARCHAR(30),
    creation_date DATE,
    creation_time TIME,
    program_name  VARCHAR(50),
    base_name     VARCHAR(100),
    base_type     VARCHAR(50),
    decree        TEXT -- Новое поле decree
);

-- Удаление таблиц decree и decrees
-- Таблицы больше не нужны, так как мы добавили поле decree в таблицу base

-- Создание таблицы resource_category с заменой resources_directory_id на base_id
CREATE TABLE resource_category
(
    id          SERIAL PRIMARY KEY,
    type        VARCHAR(50),
    code_prefix VARCHAR(10),
    base_id     INTEGER REFERENCES base (id)
);

-- Создание таблицы section с заменой resource_category_id на base_id
CREATE TABLE section
(
    id                SERIAL PRIMARY KEY,
    name              TEXT,
    type              VARCHAR(30),
    code              VARCHAR(30),
    parent_section_id INTEGER REFERENCES section (id),
    base_id           INTEGER REFERENCES base (id)
);

-- Создание таблицы name_group
CREATE TABLE name_group
(
    id         SERIAL PRIMARY KEY,
    begin_name TEXT,
    section_id INTEGER REFERENCES section (id)
);

-- Создание таблицы work с добавлением полей nr и sp и удалением parent_work_id
CREATE TABLE work
(
    id            SERIAL PRIMARY KEY,
    code          VARCHAR(50),
    end_name      TEXT,
    measure_unit  VARCHAR(100),
    name_group_id INTEGER REFERENCES name_group (id),
    nr            VARCHAR(50), -- Новое поле nr
    sp            VARCHAR(50)  -- Новое поле sp
);

-- Создание таблицы item для хранения уникальных действий
CREATE TABLE item
(
    id   SERIAL PRIMARY KEY,
    text TEXT UNIQUE
);

-- Создание таблицы work_item для связывания work и item
CREATE TABLE work_item
(
    id      SERIAL PRIMARY KEY,
    work_id INTEGER REFERENCES work (id),
    item_id INTEGER REFERENCES item (id)
);

-- Создание таблицы resource
CREATE TABLE resource
(
    id           SERIAL PRIMARY KEY,
    code         VARCHAR(50) UNIQUE,
    end_name     TEXT,
    measure_unit VARCHAR(100)
);

-- Создание таблицы abstract_resource
CREATE TABLE abstract_resource
(
    id           SERIAL PRIMARY KEY,
    code         VARCHAR(50) UNIQUE,
    name         TEXT,
    measure_unit VARCHAR(100)
);

-- Создание таблицы service_resource
CREATE TABLE service_resource
(
    id           SERIAL PRIMARY KEY,
    code         VARCHAR(50) UNIQUE,
    category     VARCHAR(50),
    name         TEXT,
    measure_unit VARCHAR(100),
    type         VARCHAR(30)
);


-- Создание таблицы work_resource для связывания work и ресурсов
CREATE TABLE work_resource
(
    id                   SERIAL PRIMARY KEY,
    work_id              INTEGER REFERENCES work (id),
    resource_id          INTEGER REFERENCES resource (id),
    abstract_resource_id INTEGER REFERENCES abstract_resource (id),
    service_resource_id  INTEGER REFERENCES service_resource (id),
    quantity             VARCHAR(30),
    measure_unit         VARCHAR(100)
);

-- Создание таблицы price с заменой prices_id на work_id
CREATE TABLE price
(
    id          SERIAL PRIMARY KEY,
    cost        NUMERIC,
    salary_mach NUMERIC,
    salary      NUMERIC,
    machines    NUMERIC,
    materials   NUMERIC,
    work_id     INTEGER REFERENCES work (id)
);

-- Создание таблицы correction
CREATE TABLE correction
(
    id         SERIAL PRIMARY KEY,
    coeff      NUMERIC,
    from_field VARCHAR(30),
    to_field   VARCHAR(30),
    price_id   INTEGER REFERENCES price (id)
);
