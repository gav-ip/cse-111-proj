-- SQL Queries and Data Modification Statements
-- Based on Pokemon Database System UML Diagram
-- Demonstrates diverse query types and modification operations

-- ============================================================================
-- QUERY 1: Search Pokemon (Simple SELECT with WHERE and LIKE)
-- Use Case: End User searching for Pokemon by name
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name,
    h.value AS height,
    w.value AS weight
FROM pokemon p
LEFT JOIN height h ON p.pokemon_id = h.height_id
LEFT JOIN weight w ON p.pokemon_id = w.weight_id
WHERE p.name LIKE '%char%'
ORDER BY p.pokemon_id;

-- ============================================================================
-- QUERY 2: View Pokemon Stats (JOIN with Aggregation)
-- Use Case: End User viewing detailed stats for a specific Pokemon
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    s.name AS stat_name,
    ps.value AS stat_value
FROM pokemon p
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
JOIN stats s ON ps.stat_id = s.stat_id
WHERE p.pokemon_id = 25  -- Pikachu
ORDER BY ps.value DESC;

-- ============================================================================
-- QUERY 3: View Evolution Chain (Self-Referential JOIN)
-- Use Case: End User viewing evolution relationships
-- ============================================================================
SELECT 
    p1.name AS evolves_from,
    p2.name AS evolves_to
FROM evolutions e
JOIN pokemon p1 ON e.from_pokemon_id = p1.pokemon_id
JOIN pokemon p2 ON e.to_pokemon_id = p2.pokemon_id
WHERE p1.pokemon_id = 1  -- Bulbasaur evolution chain
ORDER BY p2.pokemon_id;

-- ============================================================================
-- QUERY 4: Filter Pokemon by Type (Multiple JOINs with GROUP BY)
-- Use Case: End User filtering Pokemon by type
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name,
    GROUP_CONCAT(t.name, ', ') AS types
FROM pokemon p
JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
JOIN types t ON pt.type_id = t.type_id
WHERE t.name IN ('fire', 'flying')
GROUP BY p.pokemon_id, p.name
HAVING COUNT(DISTINCT t.name) >= 1
ORDER BY p.pokemon_id;

-- ============================================================================
-- QUERY 5: View Pokemon Moves (JOIN with COUNT and LIMIT)
-- Use Case: End User viewing moves available to a Pokemon
-- ============================================================================
SELECT 
    p.name AS pokemon_name,
    m.name AS move_name
FROM pokemon p
JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
JOIN moves m ON pm.move_id = m.move_id
WHERE p.pokemon_id = 6  -- Charizard
ORDER BY m.name
LIMIT 20;

-- ============================================================================
-- QUERY 6: Generate Reports - Top Pokemon by Total Stats (Aggregation with Window Function)
-- Use Case: Data Analyst generating statistical reports
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name,
    SUM(ps.value) AS total_stats,
    AVG(ps.value) AS avg_stat_value,
    COUNT(ps.stat_id) AS stat_count,
    RANK() OVER (ORDER BY SUM(ps.value) DESC) AS rank_by_total_stats
FROM pokemon p
JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
GROUP BY p.pokemon_id, p.name
ORDER BY total_stats DESC
LIMIT 10;

-- ============================================================================
-- QUERY 7: Analyze Statistics - Type Distribution Analysis (Subquery and Aggregation)
-- Use Case: Data Analyst analyzing type distribution
-- ============================================================================
SELECT 
    t.name AS type_name,
    COUNT(DISTINCT pt.pokemon_id) AS pokemon_count,
    ROUND(COUNT(DISTINCT pt.pokemon_id) * 100.0 / (SELECT COUNT(*) FROM pokemon), 2) AS percentage
FROM types t
LEFT JOIN pokemon_type pt ON t.type_id = pt.type_id
GROUP BY t.type_id, t.name
ORDER BY pokemon_count DESC;

-- ============================================================================
-- QUERY 8: Query Pokedex Numbers (Complex JOIN with Multiple Tables)
-- Use Case: Data Analyst querying Pokedex information
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name AS pokemon_name,
    d.dex_name,
    COUNT(DISTINCT d.dex_id) AS dex_count
FROM pokemon p
JOIN pokemon_number pn ON p.pokemon_id = pn.pokemon_id
JOIN dex d ON pn.dex_id = d.dex_id
GROUP BY p.pokemon_id, p.name, d.dex_name
ORDER BY p.pokemon_id, d.dex_name;

-- ============================================================================
-- QUERY 9: Analyze Statistics - Pokemon Weight Analysis (Aggregation with CASE)
-- Use Case: Data Analyst analyzing weight distribution
-- ============================================================================
SELECT 
    CASE 
        WHEN w.value < 50 THEN 'Light'
        WHEN w.value < 200 THEN 'Medium'
        WHEN w.value < 500 THEN 'Heavy'
        ELSE 'Very Heavy'
    END AS weight_category,
    COUNT(*) AS pokemon_count,
    AVG(w.value) AS avg_weight,
    MIN(w.value) AS min_weight,
    MAX(w.value) AS max_weight
FROM pokemon p
JOIN weight w ON p.pokemon_id = w.weight_id
GROUP BY weight_category
ORDER BY avg_weight;

-- ============================================================================
-- QUERY 10: Find Pokemon with Most Moves (Subquery with EXISTS)
-- Use Case: End User finding Pokemon with extensive move sets
-- ============================================================================
SELECT 
    p.pokemon_id,
    p.name,
    COUNT(pm.move_id) AS move_count
FROM pokemon p
JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
WHERE EXISTS (
    SELECT 1 
    FROM pokemon_stat ps 
    WHERE ps.pokemon_id = p.pokemon_id 
    AND ps.value > 100
)
GROUP BY p.pokemon_id, p.name
HAVING COUNT(pm.move_id) > 50
ORDER BY move_count DESC
LIMIT 10;

-- ============================================================================
-- DATA MODIFICATION STATEMENTS
-- ============================================================================

-- ============================================================================
-- MODIFICATION 1: INSERT - Add a new Pokemon (Administrator operation)
-- Use Case: Administrator updating database with new Pokemon
-- ============================================================================
INSERT OR REPLACE INTO pokemon (pokemon_id, name)
VALUES (10000, 'custom-pokemon');

INSERT OR REPLACE INTO height (height_id, value)
VALUES (10000, 10);

INSERT OR REPLACE INTO weight (weight_id, value)
VALUES (10000, 50);

-- ============================================================================
-- MODIFICATION 2: INSERT - Add Pokemon-Type relationship
-- Use Case: Administrator updating Pokemon type associations
-- ============================================================================
INSERT OR IGNORE INTO pokemon_type (pokemon_id, type_id)
SELECT 10000, type_id 
FROM types 
WHERE name = 'normal';

-- ============================================================================
-- MODIFICATION 3: UPDATE - Modify Pokemon name (Administrator operation)
-- Use Case: Administrator correcting Pokemon data
-- ============================================================================
UPDATE pokemon
SET name = UPPER(name)
WHERE pokemon_id = 10000;

-- ============================================================================
-- MODIFICATION 4: UPDATE - Update stat values for a Pokemon
-- Use Case: Administrator updating Pokemon statistics
-- ============================================================================
UPDATE pokemon_stat
SET value = value + 10
WHERE pokemon_id = 25  -- Pikachu
  AND stat_id IN (
      SELECT stat_id 
      FROM stats 
      WHERE name IN ('attack', 'special-attack')
  );

-- ============================================================================
-- MODIFICATION 5: UPDATE - Bulk update using subquery
-- Use Case: Administrator performing bulk corrections
-- ============================================================================
UPDATE weight
SET value = value * 10  -- Convert from decimeters to centimeters
WHERE weight_id IN (
    SELECT p.pokemon_id
    FROM pokemon p
    WHERE p.name LIKE 'pikachu%'
);

-- ============================================================================
-- MODIFICATION 6: DELETE - Remove Pokemon moves (Administrator operation)
-- Use Case: Administrator cleaning up invalid move associations
-- ============================================================================
DELETE FROM pokemon_move
WHERE pokemon_id = 10000
  AND move_id NOT IN (
      SELECT move_id 
      FROM moves 
      WHERE name LIKE '%punch%' OR name LIKE '%kick%'
  );

-- ============================================================================
-- MODIFICATION 7: DELETE - Remove evolution relationship
-- Use Case: Administrator correcting evolution chain data
-- ============================================================================
DELETE FROM evolutions
WHERE from_pokemon_id = 10000 
   OR to_pokemon_id = 10000;

-- ============================================================================
-- MODIFICATION 8: DELETE with Subquery - Remove orphaned Pokemon
-- Use Case: Administrator cleaning up incomplete Pokemon entries
-- ============================================================================
DELETE FROM pokemon
WHERE pokemon_id = 10000
  AND NOT EXISTS (
      SELECT 1 FROM pokemon_type WHERE pokemon_id = pokemon.pokemon_id
  )
  AND NOT EXISTS (
      SELECT 1 FROM pokemon_stat WHERE pokemon_id = pokemon.pokemon_id
  );

-- ============================================================================
-- MODIFICATION 9: INSERT with SELECT - Bulk insert Pokemon from another source
-- Use Case: Administrator loading data from external source
-- ============================================================================
-- Example: Insert Pokemon that don't exist yet (using a subquery pattern)
-- Note: This is a template - actual implementation would depend on source data
INSERT INTO pokemon (pokemon_id, name)
SELECT 10001, 'another-custom-pokemon'
WHERE NOT EXISTS (
    SELECT 1 FROM pokemon WHERE pokemon_id = 10001
);

-- ============================================================================
-- MODIFICATION 10: UPDATE with CASE - Conditional bulk update
-- Use Case: Administrator performing conditional data corrections
-- ============================================================================
UPDATE pokemon_stat
SET value = CASE
    WHEN value < 50 THEN value + 5
    WHEN value BETWEEN 50 AND 100 THEN value + 10
    ELSE value + 15
END
WHERE pokemon_id IN (
    SELECT pokemon_id 
    FROM pokemon 
    WHERE name LIKE 'pikachu%'
)
AND stat_id = (
    SELECT stat_id 
    FROM stats 
    WHERE name = 'speed'
);

