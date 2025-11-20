#!/usr/bin/env python3
"""
Pokemon Database Query Runner
Allows users to execute queries interactively
"""

import sqlite3
from typing import List, Tuple
from queries import QUERIES, MODIFICATIONS


# Database connection
DB_PATH = 'db/tpch.sqlite'


def print_menu():
    """Print the main menu"""
    print("\n" + "="*70)
    print("POKEMON DATABASE QUERY RUNNER")
    print("="*70)
    print("\nSELECT QUERIES:")
    for q_num in sorted(QUERIES.keys()):
        q = QUERIES[q_num]
        print(f"  {q_num:2d}. {q['name']}")
        print(f"      {q['description']}")
    
    print("\nMODIFICATION QUERIES (require confirmation):")
    for m_num in sorted(MODIFICATIONS.keys()):
        m = MODIFICATIONS[m_num]
        print(f"  {m_num:2d}. {m['name']}")
        print(f"      {m['description']}")
    
    print("\n  0. Exit")
    print("="*70)

def format_results(cursor, results: List[Tuple]) -> str:
    """Format query results for display"""
    if not results:
        return "No results found."
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    # Calculate column widths
    col_widths = [len(str(col)) for col in columns]
    for row in results:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)) if val else 0)
    
    # Build header
    header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
    separator = "-" * len(header)
    
    # Build rows
    rows = []
    for row in results:
        rows.append(" | ".join(str(val).ljust(col_widths[i]) if val is not None else "NULL".ljust(col_widths[i]) 
                              for i, val in enumerate(row)))
    
    return f"{header}\n{separator}\n" + "\n".join(rows)


def execute_query(query_num: int, is_modification: bool = False) -> bool:
    """Execute a query and display results"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if is_modification:
            query_info = MODIFICATIONS[query_num]
            print(f"\n WARNING: This is a MODIFICATION query that will change the database!")
            print(f"Query: {query_info['name']}")
            print(f"Description: {query_info['description']}")
            confirm = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Operation cancelled.")
                conn.close()
                return False
        else:
            query_info = QUERIES[query_num]
        
        print(f"\n{'='*70}")
        print(f"Executing: {query_info['name']}")
        print(f"Description: {query_info['description']}")
        print(f"{'='*70}\n")
        
        # Handle special case: Query 13 has two queries
        if query_num == 13:
            print("--- Lightest 10 Pokemon ---")
            cursor.execute(query_info['query'])
            results = cursor.fetchall()
            print(format_results(cursor, results))
            print("\n--- Heaviest 10 Pokemon ---")
            cursor.execute(query_info['query2'])
            results = cursor.fetchall()
            print(format_results(cursor, results))
        else:
            # Execute the query
            query = query_info['query'].strip()
            
            # Handle multiple statements for modifications
            if is_modification:
                # Check if modification query requires user input
                input_params = query_info.get('input_params', [])
                
                if input_params:
                    param_values = []
                    
                    # Collect all input parameters first
                    for param in input_params:
                        param_name = param.get('name', 'value')
                        param_prompt = param.get('prompt', f'Enter {param_name}: ')
                        param_type = param.get('type', 'str')
                        param_default = param.get('default', '')
                        
                        # Get user input
                        user_input = input(param_prompt).strip()
                        
                        # Handle empty input - use default
                        if not user_input and param_default:
                            user_input = str(param_default)
                            print(f"  Using default: {user_input}")
                        elif not user_input:
                            if param_type == 'int':
                                if param_default:
                                    user_input = str(param_default)
                                    print(f"  Using default: {user_input}")
                                else:
                                    print(f"  Error: {param_name} is required.")
                                    conn.close()
                                    return False
                            elif param_type == 'str':
                                if param_default:
                                    user_input = param_default
                                    print(f"  Using default: {user_input}")
                                else:
                                    print(f"  Error: {param_name} is required.")
                                    conn.close()
                                    return False
                            else:
                                user_input = ''
                        
                        # Transform input based on type
                        if param_type == 'int':
                            try:
                                transformed_value = int(user_input)
                                param_values.append(transformed_value)
                            except ValueError:
                                if param_default:
                                    print(f"  Invalid integer: {user_input}. Using default: {param_default}")
                                    param_values.append(int(param_default))
                                else:
                                    print(f"  Error: Invalid integer: {user_input}")
                                    conn.close()
                                    return False
                        elif param_type == 'str':
                            transformed_value = user_input
                            param_values.append(transformed_value)
                        else:
                            param_values.append(user_input)
                    
                    # Execute statements with parameters
                    # For modification queries, we need to distribute parameters across statements
                    statements = [s.strip() for s in query.split(';') if s.strip()]
                    
                    if query_num == 29:  # INSERT - New Pokemon
                        # Parameters: pokemon_id, name, height, weight, type_id, stat1_id, stat1_value, stat2_id, stat2_value, stat3_id, stat3_value
                        pokemon_id, name, height, weight, type_id, stat1_id, stat1_val, stat2_id, stat2_val, stat3_id, stat3_val = param_values
                        cursor.execute(statements[0], (pokemon_id, name))
                        cursor.execute(statements[1], (pokemon_id, height))
                        cursor.execute(statements[2], (pokemon_id, weight))
                        cursor.execute(statements[3], (pokemon_id, type_id))
                        # Last statement has 3 rows: (pokemon_id, stat_id, value) × 3
                        cursor.execute(statements[4], (pokemon_id, stat1_id, stat1_val, pokemon_id, stat2_id, stat2_val, pokemon_id, stat3_id, stat3_val))
                        
                    elif query_num == 30:  # UPDATE - Pokemon Stats
                        # Parameters: stat_increase, avg_threshold, stat_id
                        stat_increase, avg_threshold, stat_id = param_values
                        cursor.execute(statements[0], (stat_increase, avg_threshold, stat_id))
                        
                    elif query_num == 31:  # DELETE - Test Data
                        # Parameters: min_pokemon_id, pokemon_id
                        min_pokemon_id, pokemon_id = param_values
                        cursor.execute(statements[0], (min_pokemon_id,))
                        cursor.execute(statements[1], (pokemon_id,))
                        cursor.execute(statements[2], (pokemon_id,))
                        cursor.execute(statements[3], (pokemon_id,))
                        cursor.execute(statements[4], (pokemon_id,))
                        cursor.execute(statements[5], (pokemon_id,))
                    
                    conn.commit()
                    print(f"✓ Successfully executed {len(statements)} statement(s).")
                else:
                    # No input parameters - execute as before
                    statements = [s.strip() for s in query.split(';') if s.strip()]
                    for stmt in statements:
                        cursor.execute(stmt)
                    conn.commit()
                    print(f"✓ Successfully executed {len(statements)} statement(s).")
            else:
                # Check if query requires user input
                input_params = query_info.get('input_params', [])
                
                if input_params:
                    param_values = []
                    query_to_execute = query
                    
                    for param in input_params:
                        param_name = param.get('name', 'value')
                        param_prompt = param.get('prompt', f'Enter {param_name}: ')
                        param_type = param.get('type', 'str')
                        param_default = param.get('default', '')
                        
                        # Get user input
                        user_input = input(param_prompt).strip()
                        
                        # Handle empty input - use default
                        if not user_input and param_default:
                            user_input = str(param_default)
                            print(f"  Using default: {user_input}")
                        elif not user_input:
                            if param_type == 'like':
                                user_input = '%'
                            elif param_type == 'int':
                                if param_default:
                                    user_input = str(param_default)
                                    print(f"  Using default: {user_input}")
                                else:
                                    print(f"  No input provided. Skipping this parameter.")
                                    continue
                            elif param_type == 'in':
                                if param_default:
                                    user_input = param_default
                                    print(f"  Using default: {user_input}")
                                else:
                                    print("  No types provided. Skipping this parameter.")
                                    continue
                            else:
                                user_input = ''
                        
                        # Transform input based on type
                        if param_type == 'like':
                            # Add wildcards if not present
                            if '%' not in user_input:
                                transformed_value = f'%{user_input}%'
                            else:
                                transformed_value = user_input
                            param_values.append(transformed_value)
                            
                        elif param_type == 'in':
                            # Handle IN clause - split comma-separated values
                            type_list = [t.strip().lower() for t in user_input.split(',') if t.strip()]
                            if type_list:
                                # Create placeholders for IN clause
                                placeholders = ','.join(['?' for _ in type_list])
                                # Replace {} placeholder in query with actual placeholders
                                query_to_execute = query_to_execute.format(placeholders)
                                param_values.extend(type_list)
                            else:
                                # Fallback: use default if available
                                if param_default:
                                    type_list = [t.strip().lower() for t in param_default.split(',') if t.strip()]
                                    placeholders = ','.join(['?' for _ in type_list])
                                    query_to_execute = query_to_execute.format(placeholders)
                                    param_values.extend(type_list)
                                else:
                                    print("  Error: No types provided and no default available.")
                                    raise ValueError("Missing required IN parameter")
                                
                        elif param_type == 'int':
                            try:
                                transformed_value = int(user_input)
                                param_values.append(transformed_value)
                            except ValueError:
                                if param_default:
                                    print(f"  Invalid integer: {user_input}. Using default: {param_default}")
                                    param_values.append(int(param_default))
                                else:
                                    print(f"  Invalid integer: {user_input}. Using 0.")
                                    param_values.append(0)
                                
                        elif param_type == 'str':
                            transformed_value = user_input.lower() if param_name == 'move_name' else user_input
                            param_values.append(transformed_value)
                            
                        else:
                            # Default: use as-is
                            param_values.append(user_input)
                    
                    # Execute query with parameters
                    cursor.execute(query_to_execute, tuple(param_values))
                else:
                    cursor.execute(query)
                
                results = cursor.fetchall()
                print(format_results(cursor, results))
                print(f"\n({len(results)} row(s) returned)")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\nDatabase Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"\nError: {e}")
        if conn:
            conn.close()
        return False


def main():
    """Main program loop"""
    print("Welcome to the Pokemon Database Query Runner!")
    
    while True:
        print_menu()
        
        try:
            choice = input("\nEnter query number (0 to exit): ").strip()
            
            if choice == '0':
                print("\nGoodbye!")
                break
            
            query_num = int(choice)
            
            if query_num in QUERIES:
                execute_query(query_num, is_modification=False)
            elif query_num in MODIFICATIONS:
                execute_query(query_num, is_modification=True)
            else:
                print(f"\nInvalid query number: {query_num}")
                max_query = max(QUERIES.keys()) if QUERIES else 0
                max_mod = max(MODIFICATIONS.keys()) if MODIFICATIONS else 0
                print(f"Please enter a number between 1-{max_query} for queries or {min(MODIFICATIONS.keys()) if MODIFICATIONS else 0}-{max_mod} for modifications.")
            
            input("\nPress Enter to continue...")
            
        except ValueError:
            print("\nInvalid input. Please enter a number.")
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


if __name__ == '__main__':
    main()
