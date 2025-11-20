"""
Pokemon Database Queries
All SQL queries and modifications for the Pokemon database system.
Based on queries.sql
"""

from typing import Dict

# Define all queries with descriptions
QUERIES: Dict[int, Dict[str, str]] = {
    1: {
        'name': 'Search Pokemon by Name',
        'description': 'Simple SELECT with LIKE pattern matching (prompts for search term)',
        'query': """
            SELECT pokemon_id, name
            FROM pokemon
            WHERE name LIKE ?
            ORDER BY name;
        """,
        'input_params': [
            {
                'name': 'search_term',
                'prompt': 'Enter Pokemon name to search for (use % for wildcards, e.g., "char%" or "%char%"): ',
                'type': 'like',
                'default': '%'
            }
        ]
    },
    2: {
        'name': 'View Pokemon Stats with Complete Information',
        'description': 'Multiple JOINs to get comprehensive Pokemon information',
        'query': """
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
            WHERE p.pokemon_id < ?
            ORDER BY p.pokemon_id, s.stat_id;
        """,
        'input_params': [
            {
                'name': 'max_id',
                'prompt': 'Enter maximum Pokemon ID to display (default: 10): ',
                'type': 'int',
                'default': 10
            }
        ]
    },
    3: {
        'name': 'View Evolution Chain',
        'description': 'Recursive CTE to trace complete evolution paths',
        'query': """
            WITH RECURSIVE evolution_chain AS (
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
                
                SELECT 
                    p.pokemon_id,
                    p.name,
                    ec.chain_start,
                    ec.evolution_level + 1,
                    CAST(ec.evolution_path || ' -> ' || p.name AS TEXT)
                FROM evolutions e
                JOIN pokemon p ON e.to_pokemon_id = p.pokemon_id
                JOIN evolution_chain ec ON e.from_pokemon_id = ec.pokemon_id
                WHERE ec.evolution_level < 10
            )
            SELECT 
                chain_start,
                pokemon_id,
                name,
                evolution_level,
                evolution_path
            FROM evolution_chain
            ORDER BY chain_start, evolution_level;
        """
    },
    4: {
        'name': 'View Pokemon Moves with Type Information',
        'description': 'Complex JOIN showing Pokemon, their types, and moves',
        'query': """
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
        """
    },
    5: {
        'name': 'Filter Pokemon by Type',
        'description': 'Subquery to find all Pokemon of a specific type',
        'query': """
            SELECT 
                p.pokemon_id,
                p.name AS pokemon_name,
                t.name AS type_name
            FROM pokemon p
            INNER JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
            INNER JOIN types t ON pt.type_id = t.type_id
            WHERE t.name IN ({})
            ORDER BY t.name, p.name;
        """,
        'input_params': [
            {
                'name': 'types',
                'prompt': 'Enter type names (comma-separated, e.g., "fire,water,grass"): ',
                'type': 'in',
                'default': 'fire,water,grass'
            }
        ]
    },
    6: {
        'name': 'Analyze Statistics - Average Stats by Type',
        'description': 'Aggregation with GROUP BY to analyze Pokemon stats by type',
        'query': """
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
        """
    },
    7: {
        'name': 'Generate Reports - Pokemon with Above Average Stats',
        'description': 'Complex query with subqueries comparing individual stats to averages',
        'query': """
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
        """
    },
    8: {
        'name': 'Query Pokedex Numbers',
        'description': 'Show Pokemon entries across different Pokedexes',
        'query': """
            SELECT 
                p.name AS pokemon_name,
                d.dex_name AS pokedex_name,
                COUNT(*) AS entry_count
            FROM pokemon p
            INNER JOIN pokemon_number pn ON p.pokemon_id = pn.pokemon_id
            INNER JOIN dex d ON pn.dex_id = d.dex_id
            GROUP BY p.pokemon_id, p.name, d.dex_id, d.dex_name
            ORDER BY p.name, d.dex_name;
        """
    },
    9: {
        'name': 'Pokemon with the Most Moves (Top 10)',
        'description': 'Shows which Pokemon learn the highest number of moves',
        'query': """
            SELECT 
                p.name AS pokemon_name,
                COUNT(pm.move_id) AS total_moves
            FROM pokemon p
            LEFT JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
            GROUP BY p.pokemon_id, p.name
            ORDER BY total_moves DESC
            LIMIT 10;
        """
    },
    10: {
        'name': 'Dual-Typed Pokemon',
        'description': 'Lists Pokemon that have more than one type',
        'query': """
            SELECT 
                p.pokemon_id,
                p.name,
                COUNT(pt.type_id) AS type_count
            FROM pokemon p
            JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
            GROUP BY p.pokemon_id, p.name
            HAVING type_count > 1
            ORDER BY type_count DESC, p.name;
        """
    },
    11: {
        'name': 'Pokemon That Learn a Specific Move (e.g., "tackle")',
        'description': 'Shows all Pokemon that can learn a given move (use "-" for spaces e.g quick attack -> quick-attack)',
        'query': """
            SELECT 
                p.pokemon_id,
                p.name AS pokemon_name,
                m.name AS move_name
            FROM pokemon p
            JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
            JOIN moves m ON pm.move_id = m.move_id
            WHERE LOWER(m.name) = ?
            ORDER BY p.name;
        """,
        'input_params': [
            {
                'name': 'move_name',
                'prompt': 'Enter move name (case-insensitive, e.g., "tackle"): ',
                'type': 'str',
                'default': 'tackle'
            }
        ]
    },
    12: {
        'name': 'Highest Base Stat per Pokemon',
        'description': 'Displays the highest stat (value + name) for each Pokemon',
        'query': """
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
        """
    },
    13: {
        'name': 'Lightest and Heaviest Pokemon',
        'description': 'Lists the lightest and heaviest Pokemon based on recorded weights',
        'query': """
            SELECT 
                p.name,
                w.value AS weight
            FROM pokemon p
            JOIN weight w ON p.pokemon_id = w.weight_id
            ORDER BY w.value ASC
            LIMIT 10;
        """,
        'query2': """
            SELECT 
                p.name,
                w.value AS weight
            FROM pokemon p
            JOIN weight w ON p.pokemon_id = w.weight_id
            ORDER BY w.value DESC
            LIMIT 10;
        """
    },
    14: {
        'name': 'Pokemon with All Stats Above a Threshold (e.g., > 80)',
        'description': 'Finds Pokemon whose entire stat set is above a defined threshold',
        'query': """
            SELECT 
                p.pokemon_id,
                p.name
            FROM pokemon p
            JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
            GROUP BY p.pokemon_id, p.name
            HAVING MIN(ps.value) > ?
            ORDER BY p.name;
        """,
        'input_params': [
            {
                'name': 'threshold',
                'prompt': 'Enter minimum stat threshold (default: 80): ',
                'type': 'int',
                'default': 80
            }
        ]
    },
    15: {
        'name': 'Pokemon with Types, Highest Stat, and Move Count (Complex)',
        'description': 'Multi-table join showing Pokemon types, best stat, and total moves',
        'query': """
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
        """
    },
    16: {
        'name': 'Pokemon in Multiple Pokedexes with Types and Avg Stats (Complex)',
        'description': '6-table join combining dex entries, types, and stat averages',
        'query': """
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
        """
    },
    17: {
        'name': 'Full Evolution Chain with Types (Recursive CTE)',
        'description': 'Expands evolution paths and annotates each stage with its type(s)',
        'query': """
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
        """
    },
    18: {
        'name': 'Above-Average Stats for All Stats + Height + Weight (Complex)',
        'description': 'Multi-table join filtering Pokemon with above-average stats for every stat',
        'query': """
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
        """
    },
    19: {
        'name': 'Pokemon with Most Diverse Movepool by Type',
        'description': 'Shows Pokemon that can learn moves of different types (versatility analysis)',
        'query': """
            SELECT 
                p.name AS pokemon_name,
                GROUP_CONCAT(DISTINCT t.name) AS pokemon_types,
                COUNT(DISTINCT m.move_id) AS total_moves,
                COUNT(DISTINCT mt.type_id) AS move_type_diversity
            FROM pokemon p
            JOIN pokemon_move pm ON p.pokemon_id = pm.pokemon_id
            JOIN moves m ON pm.move_id = m.move_id
            JOIN move_type mt ON m.move_id = mt.move_id
            JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
            JOIN types t ON pt.type_id = t.type_id
            GROUP BY p.pokemon_id, p.name
            HAVING move_type_diversity >= ?
            ORDER BY move_type_diversity DESC, total_moves DESC
            LIMIT 15;
        """,
        'input_params': [
            {
                'name': 'min_diversity',
                'prompt': 'Enter minimum move type diversity threshold (default: 5): ',
                'type': 'int',
                'default': 5
            }
        ]
    },
    20: {
        'name': 'Pokemon Stat Distribution Analysis',
        'description': 'Categorizes Pokemon based on their stat totals into tiers',
        'query': """
            SELECT 
                CASE 
                    WHEN total_stats >= 600 THEN 'Legendary Tier'
                    WHEN total_stats >= 530 THEN 'Pseudo-Legendary Tier'
                    WHEN total_stats >= 480 THEN 'High Tier'
                    WHEN total_stats >= 400 THEN 'Mid Tier'
                    ELSE 'Low Tier'
                END AS stat_tier,
                COUNT(*) AS pokemon_count,
                ROUND(AVG(total_stats), 2) AS avg_total,
                MIN(total_stats) AS min_total,
                MAX(total_stats) AS max_total
            FROM (
                SELECT 
                    p.pokemon_id,
                    p.name,
                    SUM(ps.value) AS total_stats
                FROM pokemon p
                JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
                GROUP BY p.pokemon_id, p.name
            ) AS pokemon_totals
            GROUP BY stat_tier
            ORDER BY min_total DESC;
        """
    },
    21: {
        'name': 'Type Effectiveness Coverage',
        'description': 'Analyzes which Pokemon types are most represented across all Pokemon',
        'query': """
            SELECT 
                t.name AS type_name,
                COUNT(DISTINCT p.pokemon_id) AS pokemon_with_type,
                ROUND(COUNT(DISTINCT p.pokemon_id) * 100.0 / (SELECT COUNT(*) FROM pokemon), 2) AS percentage_of_total,
                ROUND(AVG(h.value), 2) AS avg_height,
                ROUND(AVG(w.value), 2) AS avg_weight
            FROM types t
            JOIN pokemon_type pt ON t.type_id = pt.type_id
            JOIN pokemon p ON pt.pokemon_id = p.pokemon_id
            LEFT JOIN height h ON p.pokemon_id = h.height_id
            LEFT JOIN weight w ON p.pokemon_id = w.weight_id
            GROUP BY t.type_id, t.name
            ORDER BY pokemon_with_type DESC;
        """
    },
    22: {
        'name': 'Pokemon with Balanced Stats',
        'description': 'Finds Pokemon where all stats are within 20 points of each other (well-rounded)',
        'query': """
            SELECT 
                p.pokemon_id,
                p.name AS pokemon_name,
                MIN(ps.value) AS lowest_stat,
                MAX(ps.value) AS highest_stat,
                MAX(ps.value) - MIN(ps.value) AS stat_range,
                ROUND(AVG(ps.value), 2) AS avg_stat
            FROM pokemon p
            JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
            GROUP BY p.pokemon_id, p.name
            HAVING stat_range <= ?
            ORDER BY avg_stat DESC
            LIMIT 20;
        """,
        'input_params': [
            {
                'name': 'max_range',
                'prompt': 'Enter maximum stat range threshold (default: 20): ',
                'type': 'int',
                'default': 20
            }
        ]
    },
    23: {
        'name': 'Evolution Chains with Stat Growth Analysis',
        'description': 'Compares stats between evolution stages to show growth patterns',
        'query': """
            SELECT 
                p1.name AS base_pokemon,
                p2.name AS evolved_pokemon,
                s.name AS stat_name,
                ps1.value AS base_stat_value,
                ps2.value AS evolved_stat_value,
                ps2.value - ps1.value AS stat_increase,
                ROUND((ps2.value - ps1.value) * 100.0 / ps1.value, 2) AS percent_increase
            FROM evolutions e
            JOIN pokemon p1 ON e.from_pokemon_id = p1.pokemon_id
            JOIN pokemon p2 ON e.to_pokemon_id = p2.pokemon_id
            JOIN pokemon_stat ps1 ON p1.pokemon_id = ps1.pokemon_id
            JOIN pokemon_stat ps2 ON p2.pokemon_id = ps2.pokemon_id AND ps1.stat_id = ps2.stat_id
            JOIN stats s ON ps1.stat_id = s.stat_id
            WHERE ps2.value > ps1.value
            ORDER BY percent_increase DESC
            LIMIT 30;
        """
    },
    24: {
        'name': 'Rare Type Combinations',
        'description': 'Identifies unique or rare type combinations among Pokemon',
        'query': """
            SELECT 
                GROUP_CONCAT(t.name, '/') AS type_combination,
                COUNT(DISTINCT p.pokemon_id) AS pokemon_count,
                GROUP_CONCAT(DISTINCT p.name) AS pokemon_names
            FROM pokemon p
            JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
            JOIN types t ON pt.type_id = t.type_id
            GROUP BY p.pokemon_id
            HAVING pokemon_count <= 3
            ORDER BY pokemon_count ASC, type_combination;
        """
    },
    25: {
        'name': 'Pokemon Size Categories by Type',
        'description': 'Analyzes physical size patterns across different Pokemon types',
        'query': """
            SELECT 
                t.name AS type_name,
                COUNT(DISTINCT p.pokemon_id) AS pokemon_count,
                ROUND(AVG(h.value), 2) AS avg_height,
                ROUND(AVG(w.value), 2) AS avg_weight,
                ROUND(AVG(w.value) / AVG(h.value), 2) AS weight_to_height_ratio,
                MAX(w.value) AS heaviest,
                MIN(h.value) AS shortest
            FROM types t
            JOIN pokemon_type pt ON t.type_id = pt.type_id
            JOIN pokemon p ON pt.pokemon_id = p.pokemon_id
            JOIN height h ON p.pokemon_id = h.height_id
            JOIN weight w ON p.pokemon_id = w.weight_id
            GROUP BY t.type_id, t.name
            HAVING pokemon_count >= 10
            ORDER BY weight_to_height_ratio DESC;
        """
    },
    26: {
        'name': 'Move Learning Patterns by Evolution Stage',
        'description': 'Analyzes how move availability changes through evolution chains',
        'query': """
            WITH evolution_stages AS (
                SELECT 
                    p.pokemon_id,
                    p.name,
                    CASE 
                        WHEN p.pokemon_id NOT IN (SELECT to_pokemon_id FROM evolutions) 
                            AND p.pokemon_id IN (SELECT from_pokemon_id FROM evolutions) 
                        THEN 'Base'
                        WHEN p.pokemon_id IN (SELECT to_pokemon_id FROM evolutions) 
                            AND p.pokemon_id IN (SELECT from_pokemon_id FROM evolutions) 
                        THEN 'Mid'
                        WHEN p.pokemon_id IN (SELECT to_pokemon_id FROM evolutions) 
                        THEN 'Final'
                        ELSE 'Single'
                    END AS stage
                FROM pokemon p
            )
            SELECT 
                es.stage,
                COUNT(DISTINCT es.pokemon_id) AS pokemon_in_stage,
                ROUND(AVG(move_counts.move_count), 2) AS avg_moves_per_pokemon,
                MAX(move_counts.move_count) AS max_moves
            FROM evolution_stages es
            LEFT JOIN (
                SELECT pokemon_id, COUNT(move_id) AS move_count
                FROM pokemon_move
                GROUP BY pokemon_id
            ) AS move_counts ON es.pokemon_id = move_counts.pokemon_id
            GROUP BY es.stage
            ORDER BY 
                CASE es.stage 
                    WHEN 'Single' THEN 1
                    WHEN 'Base' THEN 2
                    WHEN 'Mid' THEN 3
                    WHEN 'Final' THEN 4
                END;
        """
    },
    27: {
        'name': 'Stat Specialists vs Generalists',
        'description': 'Identifies Pokemon with one dominant stat vs balanced distributions',
        'query': """
            SELECT 
                p.name AS pokemon_name,
                GROUP_CONCAT(DISTINCT t.name) AS types,
                MAX(ps.value) AS highest_stat,
                ROUND(AVG(ps.value), 2) AS avg_stat,
                MAX(ps.value) - AVG(ps.value) AS specialization_score,
                CASE 
                    WHEN MAX(ps.value) - AVG(ps.value) > 50 THEN 'Specialist'
                    WHEN MAX(ps.value) - AVG(ps.value) < 20 THEN 'Generalist'
                    ELSE 'Balanced'
                END AS pokemon_archetype
            FROM pokemon p
            JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
            JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
            JOIN types t ON pt.type_id = t.type_id
            GROUP BY p.pokemon_id, p.name
            HAVING COUNT(ps.stat_id) >= 6
            ORDER BY specialization_score DESC
            LIMIT 25;
        """
    },
    28: {
        'name': 'Cross-Pokedex Appearances with Regional Variants',
        'description': 'Shows Pokemon that appear in multiple regional Pokedexes',
        'query': """
            SELECT 
                p.name AS pokemon_name,
                COUNT(DISTINCT pn.dex_id) AS pokedex_appearances,
                GROUP_CONCAT(DISTINCT d.dex_name ORDER BY d.dex_name) AS appears_in,
                ROUND(AVG(ps.value), 2) AS avg_stat,
                GROUP_CONCAT(DISTINCT t.name) AS types
            FROM pokemon p
            JOIN pokemon_number pn ON p.pokemon_id = pn.pokemon_id
            JOIN dex d ON pn.dex_id = d.dex_id
            JOIN pokemon_stat ps ON p.pokemon_id = ps.pokemon_id
            JOIN pokemon_type pt ON p.pokemon_id = pt.pokemon_id
            JOIN types t ON pt.type_id = t.type_id
            GROUP BY p.pokemon_id, p.name
            HAVING pokedex_appearances >= 3
            ORDER BY pokedex_appearances DESC, avg_stat DESC;
        """
    },
}

# Modification queries (require confirmation)
MODIFICATIONS: Dict[int, Dict[str, str]] = {
    29: {
        'name': 'INSERT - Load New Pokemon Data',
        'description': 'Insert a new Pokemon with associated type and stats',
        'query': """
            INSERT INTO pokemon (pokemon_id, name) 
            VALUES (?, ?);
            
            INSERT INTO height (height_id, value) 
            VALUES (?, ?);
            
            INSERT INTO weight (weight_id, value) 
            VALUES (?, ?);
            
            INSERT INTO pokemon_type (pokemon_id, type_id) 
            VALUES (?, ?);
            
            INSERT INTO pokemon_stat (pokemon_id, stat_id, value) 
            VALUES 
                (?, ?, ?),
                (?, ?, ?),
                (?, ?, ?);
        """,
        'input_params': [
            {
                'name': 'pokemon_id',
                'prompt': 'Enter Pokemon ID (must be unique, e.g., 10001): ',
                'type': 'int',
                'default': ''
            },
            {
                'name': 'pokemon_name',
                'prompt': 'Enter Pokemon name: ',
                'type': 'str',
                'default': ''
            },
            {
                'name': 'height',
                'prompt': 'Enter height value: ',
                'type': 'int',
                'default': ''
            },
            {
                'name': 'weight',
                'prompt': 'Enter weight value: ',
                'type': 'int',
                'default': ''
            },
            {
                'name': 'type_id',
                'prompt': 'Enter type ID (e.g., 1 for normal): ',
                'type': 'int',
                'default': ''
            },
            {
                'name': 'stat1_id',
                'prompt': 'Enter first stat ID (e.g., 1 for HP): ',
                'type': 'int',
                'default': '1'
            },
            {
                'name': 'stat1_value',
                'prompt': 'Enter first stat value: ',
                'type': 'int',
                'default': ''
            },
            {
                'name': 'stat2_id',
                'prompt': 'Enter second stat ID (e.g., 2 for Attack): ',
                'type': 'int',
                'default': '2'
            },
            {
                'name': 'stat2_value',
                'prompt': 'Enter second stat value: ',
                'type': 'int',
                'default': ''
            },
            {
                'name': 'stat3_id',
                'prompt': 'Enter third stat ID (e.g., 3 for Defense): ',
                'type': 'int',
                'default': '3'
            },
            {
                'name': 'stat3_value',
                'prompt': 'Enter third stat value: ',
                'type': 'int',
                'default': ''
            }
        ]
    },
    30: {
        'name': 'UPDATE - Update Pokemon Stats',
        'description': 'Bulk update to balance Pokemon stats',
        'query': """
            UPDATE pokemon_stat
            SET value = value + ?
            WHERE pokemon_id IN (
                SELECT pokemon_id 
                FROM pokemon_stat 
                GROUP BY pokemon_id 
                HAVING AVG(value) < ?
            )
            AND stat_id = ?;
        """,
        'input_params': [
            {
                'name': 'stat_increase',
                'prompt': 'Enter stat increase amount (default: 10): ',
                'type': 'int',
                'default': '10'
            },
            {
                'name': 'avg_threshold',
                'prompt': 'Enter average stat threshold - only Pokemon below this will be updated (default: 50): ',
                'type': 'int',
                'default': '50'
            },
            {
                'name': 'stat_id',
                'prompt': 'Enter stat ID to update (e.g., 1 for HP, default: 1): ',
                'type': 'int',
                'default': '1'
            }
        ]
    },
    31: {
        'name': 'DELETE - Remove Test/Temporary Data',
        'description': 'Clean up test data and orphaned records',
        'query': """
            DELETE FROM pokemon_move
            WHERE pokemon_id > ?;
            
            DELETE FROM pokemon_stat WHERE pokemon_id = ?;
            DELETE FROM pokemon_type WHERE pokemon_id = ?;
            DELETE FROM height WHERE height_id = ?;
            DELETE FROM weight WHERE weight_id = ?;
            DELETE FROM pokemon WHERE pokemon_id = ?;
        """,
        'input_params': [
            {
                'name': 'min_pokemon_id',
                'prompt': 'Enter minimum Pokemon ID to delete moves for (Pokemon IDs above this, default: 10000): ',
                'type': 'int',
                'default': '10000'
            },
            {
                'name': 'pokemon_id',
                'prompt': 'Enter Pokemon ID to delete completely (default: 10001): ',
                'type': 'int',
                'default': '10001'
            }
        ]
    },
}

