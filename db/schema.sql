-- Schema generated from diagrams/ER_diagram.drawio
-- SQL dialect: PostgreSQL-compatible

-- Core entities
CREATE TABLE pokemon (
    pokemon_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE types (
    type_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE stats (
    stat_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE moves (
    move_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE dex (
    dex_id INTEGER PRIMARY KEY,
    dex_name VARCHAR(100) NOT NULL
);

-- 1:1 entities (modeled with shared PK referencing pokemon)
CREATE TABLE height (
    height_id INTEGER PRIMARY KEY,
    value INTEGER NOT NULL,
    CONSTRAINT height_pokemon_fk FOREIGN KEY (height_id) REFERENCES pokemon(pokemon_id)
);

CREATE TABLE weight (
    weight_id INTEGER PRIMARY KEY,
    value INTEGER NOT NULL,
    CONSTRAINT weight_pokemon_fk FOREIGN KEY (weight_id) REFERENCES pokemon(pokemon_id)
);

-- Junction tables / relationships
CREATE TABLE pokemon_type (
    pokemon_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, type_id),
    CONSTRAINT pokemon_type_pokemon_fk FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
    CONSTRAINT pokemon_type_type_fk FOREIGN KEY (type_id) REFERENCES types(type_id)
);

CREATE TABLE pokemon_stat (
    pokemon_id INTEGER NOT NULL,
    stat_id INTEGER NOT NULL,
    value INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, stat_id),
    CONSTRAINT pokemon_stat_pokemon_fk FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
    CONSTRAINT pokemon_stat_stat_fk FOREIGN KEY (stat_id) REFERENCES stats(stat_id)
);

CREATE TABLE pokemon_move (
    pokemon_id INTEGER NOT NULL,
    move_id INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, move_id),
    CONSTRAINT pokemon_move_pokemon_fk FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
    CONSTRAINT pokemon_move_move_fk FOREIGN KEY (move_id) REFERENCES moves(move_id)
);

CREATE TABLE pokemon_number (
    pokemon_id INTEGER NOT NULL,
    dex_id INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, dex_id),
    CONSTRAINT pokemon_number_pokemon_fk FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
    CONSTRAINT pokemon_number_dex_fk FOREIGN KEY (dex_id) REFERENCES dex(dex_id)
);

-- Evolutions: self-referential relationship between pokemon
CREATE TABLE evolutions (
    from_pokemon_id INTEGER NOT NULL,
    to_pokemon_id INTEGER NOT NULL,
    PRIMARY KEY (from_pokemon_id, to_pokemon_id),
    CONSTRAINT evolutions_from_fk FOREIGN KEY (from_pokemon_id) REFERENCES pokemon(pokemon_id),
    CONSTRAINT evolutions_to_fk FOREIGN KEY (to_pokemon_id) REFERENCES pokemon(pokemon_id)
);

-- Optional indexes (FKs are indexed by PKs, composite PKs cover joins)

