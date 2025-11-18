-- SQL Queries and Data Modification Statements
-- Based on Pokemon Database System UML Diagram

-- ============================================================================
-- QUERY 1: Search Pokemon by Name (Use Case: Search Pokemon)
-- Simple SELECT with LIKE pattern matching
-- ============================================================================
SELECT pokemon_id, name
FROM pokemon
WHERE name LIKE '%char%'
ORDER BY name;


-- ============================================================================
-- QUERY 2: View Pokemon Stats with Complete Information (Use Case: View Pokemon Stats)
-- Multiple JOINs to get comprehensive Pokemon information
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name AS pokemon_name,
    h.value AS height,
    w.value AS weight,
    s.name AS stat_name,
    ps.value AS stat_value
FROM pokemon p
LEFT JOIN height h ON p.pokemon_id = h.height_id
LEFT JOIN weight w ON p.pokemon_id = w.weight_id
LEFT JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
LEFT JOIN stats s ON ps.stat_id = s.stat_id
WHERE p.pokemon_id < 10
ORDER BY p.pokemon_id, s.stat_id;


-- ============================================================================
-- QUERY 3: View Evolution Chain (Use Case: View Evolution Chain)
-- Recursive CTE to trace complete evolution paths
-- ============================================================================
WITH RECURSIVE evolution_chain AS (
    -- Base case: Pokemon that are not evolved from anything (first stage)
    SELECT 
        p.pokemon_id,
        p.name,
        p.pokemon_id AS chain_start,
        1 AS evolution_level,
        CAST(p.name AS TEXT) AS evolution_path
    FROM pokemon p
    WHERE NOT EXISTS (
        SELECT 1 FROM evolutions e WHERE e.to_pokemon_id = p.pokemon_id
    )
    
    UNION ALL
    
    -- Recursive case: Follow evolution chain
    SELECT 
        p.pokemon_id,
        p.name,
        ec.chain_start,
        ec.evolution_level + 1,
        CAST(ec.evolution_path || ' -> ' || p.name AS TEXT)
    FROM evolutions e
    JOIN pokemon p ON e.to_pokemon_id = p.pokemon_id
    JOIN evolution_chain ec ON e.from_pokemon_id = ec.pokemon_id
    WHERE ec.evolution_level < 10  -- Prevent infinite loops
)
SELECT 
    chain_start,
    pokemon_id,
    name,
    evolution_level,
    evolution_path
FROM evolution_chain
ORDER BY chain_start, evolution_level;


-- ============================================================================
-- QUERY 4: View Pokemon Moves with Type Information (Use Case: View Pokemon Moves)
-- Complex JOIN showing Pokemon, their types, and moves
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    GROUP_CONCAT(DISTINCT t.name, ', ') AS types,
    COUNT(DISTINCT pm.move_id) AS total_moves,
    GROUP_CONCAT(m.name, ', ') AS sample_moves
FROM pokemon p
INNER JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
INNER JOIN types t ON pt.type_id = t.type_id
LEFT JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
LEFT JOIN moves m ON pm.move_id = m.move_id
GROUP BY p.pokemon_id, p.name
HAVING total_moves > 0
LIMIT 20;


-- ============================================================================
-- QUERY 5: Filter Pokemon by Type (Use Case: Filter Pokemon by Type)
-- Subquery to find all Pokemon of a specific type
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name AS pokemon_name,
    t.name AS type_name
FROM pokemon p
INNER JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
INNER JOIN types t ON pt.type_id = t.type_id
WHERE t.name IN ('fire', 'water', 'grass')
ORDER BY t.name, p.name;


-- ============================================================================
-- QUERY 6: Analyze Statistics - Average Stats by Type (Use Case: Analyze Statistics)
-- Aggregation with GROUP BY to analyze Pokemon stats by type
-- ============================================================================
SELECT 
    t.name AS type_name,
    s.name AS stat_name,
    COUNT(DISTINCT p.pokemon_id) AS pokemon_count,
    ROUND(AVG(ps.value), 2) AS avg_stat_value,
    MIN(ps.value) AS min_stat_value,
    MAX(ps.value) AS max_stat_value
FROM types t
INNER JOIN pokemon_type pt ON t.type_id = pt.type_id
INNER JOIN pokemon p ON pt.pokemon_id = p.pokemon_id
INNER JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
INNER JOIN stats s ON ps.stat_id = s.stat_id
GROUP BY t.type_id, t.name, s.stat_id, s.name
HAVING pokemon_count >= 5
ORDER BY t.name, s.name;


-- ============================================================================
-- QUERY 7: Generate Reports - Pokemon with Above Average Stats (Use Case: Generate Reports)
-- Complex query with subqueries comparing individual stats to averages
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    s.name AS stat_name,
    ps.value AS stat_value,
    (SELECT ROUND(AVG(value), 2) FROM pokemon_stat WHERE stat_id = ps.stat_id) AS avg_for_stat,
    ps.value - (SELECT AVG(value) FROM pokemon_stat WHERE stat_id = ps.stat_id) AS difference_from_avg
FROM pokemon p
INNER JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
INNER JOIN stats s ON ps.stat_id = s.stat_id
WHERE ps.value > (SELECT AVG(value) FROM pokemon_stat WHERE stat_id = ps.stat_id)
ORDER BY difference_from_avg DESC
LIMIT 25;


-- ============================================================================
-- QUERY 8: Query Pokedex Numbers (Use Case: Query Pokedex Numbers)
-- Show Pokemon entries across different Pokedexes
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    d.dex_name AS pokedex_name,
    COUNT(*) AS entry_count
FROM pokemon p
INNER JOIN pokemon_number pn ON p.pokemon_id = pn.pokemon_id
INNER JOIN dex d ON pn.dex_id = d.dex_id
GROUP BY p.pokemon_id, p.name, d.dex_id, d.dex_name
ORDER BY p.name, d.dex_name;

-- ============================================================================
-- QUERY 9: Pokemon with the Most Moves (Top 10)
-- Shows which Pokemon learn the highest number of moves.
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    COUNT(pm.move_id) AS total_moves
FROM pokemon p
LEFT JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
GROUP BY p.pokemon_id, p.name
ORDER BY total_moves DESC
LIMIT 10;


-- ============================================================================
-- QUERY 10: Dual-Typed Pokemon
-- Lists Pokemon that have more than one type.
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name,
    COUNT(pt.type_id) AS type_count
FROM pokemon p
JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
GROUP BY p.pokemon_id, p.name
HAVING type_count > 1
ORDER BY type_count DESC, p.name;


-- ============================================================================
-- QUERY 11: Pokemon That Learn a Specific Move (e.g., "tackle")
-- Shows all Pokemon that can learn a given move.
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name AS pokemon_name,
    m.name AS move_name
FROM pokemon p
JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
JOIN moves m ON pm.move_id = m.move_id
WHERE LOWER(m.name) = 'tackle'
ORDER BY p.name;


-- ============================================================================
-- QUERY 12: Highest Base Stat per Pokemon
-- Displays the highest stat (value + name) for each Pokemon.
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    s.name AS highest_stat_name,
    ps.value AS highest_stat_value
FROM pokemon p
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
JOIN stats s ON ps.stat_id = s.stat_id
WHERE ps.value = (
    SELECT MAX(ps2.value)
    FROM pokemon_stat ps2
    WHERE ps2.pokemon_id = p.pokemon_id
)
ORDER BY highest_stat_value DESC
LIMIT 20;


-- ============================================================================
-- QUERY 13: Lightest and Heaviest Pokemon
-- Lists the lightest and heaviest Pokemon based on recorded weights.
-- ============================================================================
-- Lightest 10
SELECT 
    p.name,
    w.value AS weight
FROM pokemon p
JOIN weight w ON p.pokemon_id = w.weight_id
ORDER BY w.value ASC
LIMIT 10;

-- Heaviest 10
SELECT 
    p.name,
    w.value AS weight
FROM pokemon p
JOIN weight w ON p.pokemon_id = w.weight_id
ORDER BY w.value DESC
LIMIT 10;


-- ============================================================================
-- QUERY 14: Pokemon with All Stats Above a Threshold (e.g., > 80)
-- Finds Pokemon whose entire stat set is above a defined threshold.
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name
FROM pokemon p
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
GROUP BY p.pokemon_id, p.name
HAVING MIN(ps.value) > 80
ORDER BY p.name;


-- ============================================================================
-- QUERY 15: Pokemon with Types, Highest Stat, and Move Count (Complex)
-- Multi-table join showing Pokemon types, best stat, and total moves.
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    GROUP_CONCAT(DISTINCT t.name) AS types,
    s.name AS highest_stat_name,
    MAX(ps.value) AS highest_stat_value,
    COUNT(DISTINCT pm.move_id) AS total_moves
FROM pokemon p
JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
JOIN types t ON pt.type_id = t.type_id
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
JOIN stats s ON ps.stat_id = s.stat_id
LEFT JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
GROUP BY p.pokemon_id
ORDER BY highest_stat_value DESC
LIMIT 20;


-- ============================================================================
-- QUERY 16: Pokemon in Multiple Pokedexes with Types and Avg Stats (Complex)
-- 6-table join combining dex entries, types, and stat averages.
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    GROUP_CONCAT(DISTINCT d.dex_name) AS dexes,
    GROUP_CONCAT(DISTINCT t.name) AS types,
    ROUND(AVG(ps.value), 2) AS avg_stat
FROM pokemon p
JOIN pokemon_number pn ON p.pokemon_id = pn.pokemon_id
JOIN dex d ON pn.dex_id = d.dex_id
JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
JOIN types t ON pt.type_id = t.type_id
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
GROUP BY p.pokemon_id
HAVING COUNT(DISTINCT pn.dex_id) > 1
ORDER BY avg_stat DESC;


-- ============================================================================
-- QUERY 17: Full Evolution Chain with Types (Recursive CTE)
-- Expands evolution paths and annotates each stage with its type(s).
-- ============================================================================
WITH RECURSIVE evo_chain AS (
    SELECT 
        p.pokemon_id,
        p.name,
        CAST(p.name AS TEXT) AS path
    FROM pokemon p
    WHERE p.pokemon_id NOT IN (
        SELECT to_pokemon_id FROM evolutions
    )

    UNION ALL

    SELECT 
        p2.pokemon_id,
        p2.name,
        ec.path || ' -> ' || p2.name
    FROM evo_chain ec
    JOIN evolutions e ON ec.pokemon_id = e.from_pokemon_id
    JOIN pokemon p2 ON p2.pokemon_id = e.to_pokemon_id
)
SELECT 
    ec.path,
    GROUP_CONCAT(DISTINCT t.name) AS types
FROM evo_chain ec
JOIN pokemon_type pt ON ec.pokemon_id = pt.pokemon_id
JOIN types t ON pt.type_id = t.type_id
GROUP BY ec.path
ORDER BY LENGTH(ec.path) DESC;


-- ============================================================================
-- QUERY 18: Above-Average Stats for All Stats + Height + Weight (Complex)
-- Multi-table join filtering Pokemon with above-average stats for every stat.
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    GROUP_CONCAT(DISTINCT t.name) AS types,
    h.value AS height,
    w.value AS weight
FROM pokemon p
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
JOIN stats s ON ps.stat_id = s.stat_id
JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
JOIN types t ON pt.type_id = t.type_id
JOIN height h ON p.pokemon_id = h.height_id
JOIN weight w ON p.pokemon_id = w.weight_id
GROUP BY p.pokemon_id
HAVING MIN(ps.value) > (
    SELECT AVG(ps2.value)
    FROM pokemon_stat ps2
    WHERE ps2.stat_id = ps.stat_id
)
ORDER BY p.name;


-- ============================================================================
-- MODIFICATION 1: INSERT - Load New Pokemon Data (Use Case: Load Data from PokeAPI)
-- Insert a new Pokemon with associated type and stats
-- ============================================================================
-- Insert new Pokemon
INSERT INTO pokemon (pokemon_id, name) 
VALUES (10001, 'TestMon');

-- Insert height and weight
INSERT INTO height (height_id, value) 
VALUES (10001, 15);

INSERT INTO weight (weight_id, value) 
VALUES (10001, 250);

-- Insert Pokemon type (assuming type_id 1 exists - e.g., 'normal')
INSERT INTO pokemon_type (pokemon_id, type_id) 
VALUES (10001, 1);

-- Insert Pokemon stats (assuming stat_ids 1-6 exist for HP, Attack, Defense, etc.)
INSERT INTO pokemon_stat (pokemon_id, stat_id, value) 
VALUES 
    (10001, 1, 100),
    (10001, 2, 85),
    (10001, 3, 75);


-- ============================================================================
-- MODIFICATION 2: UPDATE - Update Pokemon Stats (Use Case: Update Database)
-- Bulk update to balance Pokemon stats
-- ============================================================================
UPDATE pokemon_stat
SET value = value + 10
WHERE pokemon_id IN (
    SELECT pokemon_id 
    FROM pokemon_stat 
    GROUP BY pokemon_id 
    HAVING AVG(value) < 50
)
AND stat_id = 1;  -- Update HP (assuming stat_id 1 is HP)


-- ============================================================================
-- MODIFICATION 3: DELETE - Remove Test/Temporary Data (Use Case: Update Database)
-- Clean up test data and orphaned records
-- ============================================================================
-- Delete Pokemon moves for Pokemon that no longer exist or test data
DELETE FROM pokemon_move
WHERE pokemon_id > 10000;

-- Delete the test Pokemon we inserted earlier
DELETE FROM pokemon_stat WHERE pokemon_id = 10001;
DELETE FROM pokemon_type WHERE pokemon_id = 10001;
DELETE FROM height WHERE height_id = 10001;
DELETE FROM weight WHERE weight_id = 10001;
DELETE FROM pokemon WHERE pokemon_id = 10001;
