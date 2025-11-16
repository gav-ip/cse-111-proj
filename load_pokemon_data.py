#!/usr/bin/env python3
"""
Load Pokemon data from PokeAPI into SQLite database.
Fetches all Pokemon data and populates the database according to the schema.
"""

import sqlite3
import requests
import time
import sys
from typing import Dict, List, Optional, Tuple

# Database file
DB_FILE = 'tpch.sqlite'

# PokeAPI base URL
BASE_URL = 'https://pokeapi.co/api/v2'

# Rate limiting: PokeAPI recommends ~100 requests/minute
# We'll use 0.6 seconds between requests to be safe
REQUEST_DELAY = 0.6


def get_pokemon_count(max_retries: int = 3) -> int:
    """Get the total number of Pokemon available from PokeAPI.
    
    Args:
        max_retries: Maximum number of retry attempts
        
    Returns:
        Total count of Pokemon available
        
    Raises:
        Exception: If unable to fetch count after retries
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(f'{BASE_URL}/pokemon/?limit=1', timeout=10)
            response.raise_for_status()
            data = response.json()
            count = data.get('count')
            if count is not None:
                return count
            else:
                raise ValueError("Count field not found in API response")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Error getting Pokemon count (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Failed to get Pokemon count after {max_retries} attempts: {e}")
        except (KeyError, ValueError) as e:
            raise Exception(f"Invalid API response format: {e}")
    
    raise Exception("Failed to get Pokemon count")


def fetch_pokemon_data(pokemon_id: int) -> Optional[Dict]:
    """Fetch Pokemon data from PokeAPI."""
    try:
        response = requests.get(f'{BASE_URL}/pokemon/{pokemon_id}/')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        print(f"Error fetching Pokemon {pokemon_id}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching Pokemon {pokemon_id}: {e}")
        return None


def fetch_species_data(pokemon_id: int) -> Optional[Dict]:
    """Fetch Pokemon species data from PokeAPI."""
    try:
        response = requests.get(f'{BASE_URL}/pokemon-species/{pokemon_id}/')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        print(f"Error fetching species {pokemon_id}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching species {pokemon_id}: {e}")
        return None


def extract_pokemon_id_from_url(url: str) -> int:
    """Extract Pokemon ID from PokeAPI URL."""
    # URL format: https://pokeapi.co/api/v2/pokemon/1/
    parts = url.rstrip('/').split('/')
    return int(parts[-1])


def insert_pokemon(cursor: sqlite3.Cursor, pokemon_id: int, name: str):
    """Insert Pokemon into database."""
    cursor.execute('INSERT OR IGNORE INTO pokemon (pokemon_id, name) VALUES (?, ?)',
                   (pokemon_id, name))


def insert_type(cursor: sqlite3.Cursor, type_id: int, name: str):
    """Insert type into database."""
    cursor.execute('INSERT OR IGNORE INTO types (type_id, name) VALUES (?, ?)',
                   (type_id, name))


def insert_stat(cursor: sqlite3.Cursor, stat_id: int, name: str):
    """Insert stat into database."""
    cursor.execute('INSERT OR IGNORE INTO stats (stat_id, name) VALUES (?, ?)',
                   (stat_id, name))


def insert_move(cursor: sqlite3.Cursor, move_id: int, name: str):
    """Insert move into database."""
    cursor.execute('INSERT OR IGNORE INTO moves (move_id, name) VALUES (?, ?)',
                   (move_id, name))


def insert_dex(cursor: sqlite3.Cursor, dex_id: int, dex_name: str):
    """Insert dex into database."""
    cursor.execute('INSERT OR IGNORE INTO dex (dex_id, dex_name) VALUES (?, ?)',
                   (dex_id, dex_name))


def insert_height(cursor: sqlite3.Cursor, pokemon_id: int, height: int):
    """Insert height into database."""
    cursor.execute('INSERT OR IGNORE INTO height (height_id, value) VALUES (?, ?)',
                   (pokemon_id, height))


def insert_weight(cursor: sqlite3.Cursor, pokemon_id: int, weight: int):
    """Insert weight into database."""
    cursor.execute('INSERT OR IGNORE INTO weight (weight_id, value) VALUES (?, ?)',
                   (pokemon_id, weight))


def insert_pokemon_type(cursor: sqlite3.Cursor, pokemon_id: int, type_id: int):
    """Insert pokemon-type relationship."""
    cursor.execute('INSERT OR IGNORE INTO pokemon_type (pokemon_id, type_id) VALUES (?, ?)',
                   (pokemon_id, type_id))


def insert_pokemon_stat(cursor: sqlite3.Cursor, pokemon_id: int, stat_id: int, value: int):
    """Insert pokemon-stat relationship with value."""
    cursor.execute('INSERT OR IGNORE INTO pokemon_stat (pokemon_id, stat_id, value) VALUES (?, ?, ?)',
                   (pokemon_id, stat_id, value))


def insert_pokemon_move(cursor: sqlite3.Cursor, pokemon_id: int, move_id: int):
    """Insert pokemon-move relationship."""
    cursor.execute('INSERT OR IGNORE INTO pokemon_move (pokemon_id, move_id) VALUES (?, ?)',
                   (pokemon_id, move_id))


def insert_pokemon_number(cursor: sqlite3.Cursor, pokemon_id: int, dex_id: int):
    """Insert pokemon-dex relationship."""
    cursor.execute('INSERT OR IGNORE INTO pokemon_number (pokemon_id, dex_id) VALUES (?, ?)',
                   (pokemon_id, dex_id))


def insert_evolution(cursor: sqlite3.Cursor, from_pokemon_id: int, to_pokemon_id: int):
    """Insert evolution relationship. Only inserts if both Pokemon exist."""
    # Check if both Pokemon exist
    cursor.execute('SELECT COUNT(*) FROM pokemon WHERE pokemon_id IN (?, ?)', 
                   (from_pokemon_id, to_pokemon_id))
    count = cursor.fetchone()[0]
    if count == 2:  # Both Pokemon exist
        cursor.execute('INSERT OR IGNORE INTO evolutions (from_pokemon_id, to_pokemon_id) VALUES (?, ?)',
                       (from_pokemon_id, to_pokemon_id))


def bulk_insert(cursor: sqlite3.Cursor):
    """Optimize SQLite settings for faster bulk inserts.
    
    Disables safety features that slow down bulk operations:
    - synchronous: OFF - Don't wait for disk writes (faster, but less safe)
    - journal_mode: MEMORY - Use in-memory journal (faster)
    - cache_size: 10000 - Increase cache size (pages)
    - temp_store: MEMORY - Store temp tables in memory
    
    WARNING: These settings reduce data safety. Only use during bulk loading.
    """
    print("Optimizing SQLite settings for bulk inserts...")
    cursor.execute('PRAGMA synchronous = OFF')
    cursor.execute('PRAGMA journal_mode = MEMORY')
    cursor.execute('PRAGMA cache_size = 10000')
    cursor.execute('PRAGMA temp_store = MEMORY')
    print("SQLite optimizations enabled")


def restore_sqlite_settings(cursor: sqlite3.Cursor):
    """Restore SQLite safety settings after bulk loading.
    
    Re-enables safety features:
    - synchronous: NORMAL - Normal disk synchronization
    - journal_mode: DELETE - Standard journal mode
    - cache_size: -2000 - Default cache size (2MB)
    - temp_store: DEFAULT - Default temp storage
    """
    print("Restoring SQLite safety settings...")
    cursor.execute('PRAGMA synchronous = NORMAL')
    cursor.execute('PRAGMA journal_mode = DELETE')
    cursor.execute('PRAGMA cache_size = -2000')  # Default: 2MB
    cursor.execute('PRAGMA temp_store = DEFAULT')
    print("SQLite safety settings restored")


def get_loaded_pokemon_ids(cursor: sqlite3.Cursor) -> set:
    """Get set of Pokemon IDs that are already loaded in the database."""
    cursor.execute('SELECT pokemon_id FROM pokemon')
    return {row[0] for row in cursor.fetchall()}


def collect_evolution_chain(chain: Dict, parent_id: Optional[int] = None, evolutions: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
    """Recursively collect evolution chain relationships."""
    if evolutions is None:
        evolutions = []
    
    species_url = chain['species']['url']
    pokemon_id = extract_pokemon_id_from_url(species_url.replace('pokemon-species', 'pokemon'))
    
    # Collect evolution if there's a parent
    if parent_id is not None:
        evolutions.append((parent_id, pokemon_id))
    
    # Process evolves_to
    for evolution in chain.get('evolves_to', []):
        collect_evolution_chain(evolution, pokemon_id, evolutions)
    
    return evolutions


def process_pokemon(cursor: sqlite3.Cursor, pokemon_id: int):
    """Process a single Pokemon and insert all related data. Returns evolution relationships."""
    # Fetch Pokemon data
    pokemon_data = fetch_pokemon_data(pokemon_id)
    if not pokemon_data:
        return None
    
    # Fetch species data for dex numbers and evolution chain
    species_data = fetch_species_data(pokemon_id)
    
    # Insert Pokemon
    pokemon_name = pokemon_data['name']
    insert_pokemon(cursor, pokemon_id, pokemon_name)
    
    # Insert height and weight
    height = pokemon_data.get('height', 0)
    weight = pokemon_data.get('weight', 0)
    insert_height(cursor, pokemon_id, height)
    insert_weight(cursor, pokemon_id, weight)
    
    # Insert types
    for type_info in pokemon_data.get('types', []):
        type_data = type_info['type']
        type_id = extract_pokemon_id_from_url(type_data['url'])
        type_name = type_data['name']
        insert_type(cursor, type_id, type_name)
        insert_pokemon_type(cursor, pokemon_id, type_id)
    
    # Insert stats
    for stat_info in pokemon_data.get('stats', []):
        stat_data = stat_info['stat']
        stat_id = extract_pokemon_id_from_url(stat_data['url'])
        stat_name = stat_data['name']
        stat_value = stat_info.get('base_stat', 0)
        insert_stat(cursor, stat_id, stat_name)
        insert_pokemon_stat(cursor, pokemon_id, stat_id, stat_value)
    
    # Insert moves
    for move_info in pokemon_data.get('moves', []):
        move_data = move_info['move']
        move_id = extract_pokemon_id_from_url(move_data['url'])
        move_name = move_data['name']
        insert_move(cursor, move_id, move_name)
        insert_pokemon_move(cursor, pokemon_id, move_id)
    
    # Insert dex numbers from species data
    evolutions = []
    if species_data:
        for entry in species_data.get('pokedex_numbers', []):
            dex_data = entry['pokedex']
            dex_id = extract_pokemon_id_from_url(dex_data['url'])
            dex_name = dex_data['name']
            entry_number = entry.get('entry_number', dex_id)
            insert_dex(cursor, dex_id, dex_name)
            insert_pokemon_number(cursor, pokemon_id, dex_id)
        
        # Collect evolution chain relationships (don't insert yet)
        evolution_chain_url = species_data.get('evolution_chain', {}).get('url')
        if evolution_chain_url:
            try:
                evolution_response = requests.get(evolution_chain_url)
                evolution_response.raise_for_status()
                evolution_data = evolution_response.json()
                chain = evolution_data.get('chain', {})
                if chain:
                    evolutions = collect_evolution_chain(chain)
            except Exception as e:
                print(f"Error collecting evolution chain for Pokemon {pokemon_id}: {e}")
    
    return evolutions


def main():
    """Main function to load all Pokemon data."""
    print("Starting Pokemon data loading...")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Optimize SQLite for bulk inserts
    bulk_insert(cursor)
    
    try:
        # Get already loaded Pokemon IDs
        loaded_pokemon = get_loaded_pokemon_ids(cursor)
        already_loaded_count = len(loaded_pokemon)
        
        if already_loaded_count > 0:
            print(f"Found {already_loaded_count} Pokemon already loaded in database")
            print("Resuming from where we left off...")
        else:
            print("Starting fresh load...")
        
        # Get total Pokemon count
        total_pokemon = get_pokemon_count()
        print(f"Total Pokemon to process: {total_pokemon}")
        
        # Process each Pokemon
        success_count = 0
        skipped_count = 0
        fail_count = 0
        all_evolutions = []
        
        for pokemon_id in range(1, total_pokemon + 1):
            # Skip if already loaded
            if pokemon_id in loaded_pokemon:
                skipped_count += 1
                print(f"Skipping Pokemon {pokemon_id}/{total_pokemon} (already loaded)...", end='\r')
                continue
            
            print(f"Processing Pokemon {pokemon_id}/{total_pokemon}...", end='\r')
            
            evolutions = process_pokemon(cursor, pokemon_id)
            if evolutions is not None:
                success_count += 1
                # Collect evolution relationships
                if evolutions:
                    all_evolutions.extend(evolutions)
            else:
                fail_count += 1
            
            # Commit every 10 Pokemon
            if pokemon_id % 10 == 0:
                conn.commit()
            
            # Rate limiting (only for API calls, not for skipped Pokemon)
            time.sleep(REQUEST_DELAY)
        
        # Insert all evolution relationships after all Pokemon are loaded (deduplicate)
        unique_evolutions = list(set(all_evolutions))
        print(f"\nInserting {len(unique_evolutions)} evolution relationships...")
        for from_id, to_id in unique_evolutions:
            insert_evolution(cursor, from_id, to_id)
        
        # Final commit
        conn.commit()
        
        print(f"\n\nCompleted!")
        print(f"Successfully loaded: {success_count} Pokemon")
        print(f"Skipped (already loaded): {skipped_count} Pokemon")
        print(f"Failed: {fail_count} Pokemon")
        
        # Verify data
        cursor.execute('SELECT COUNT(*) FROM pokemon')
        pokemon_count = cursor.fetchone()[0]
        print(f"\nTotal Pokemon in database: {pokemon_count}")
        
    finally:
        # Always restore SQLite safety settings, even if an error occurred
        restore_sqlite_settings(cursor)
        # Final commit to ensure settings are persisted
        conn.commit()
        cursor.close()
        conn.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)

