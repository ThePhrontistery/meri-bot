import os
import sys
import sqlite3
from pathlib import Path

def main():
    # Use raw string for Windows paths
    db_path = r"c:\Users\pfurnica\CascadeProjects\meribot_app\meribot\chroma_db\chroma.sqlite3"
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return 1
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\nFound {len(tables)} tables in the database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # For each table, show column info and row count
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * 50)
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"\nRow count: {count}")
            
            # Show first few rows if table is not empty
            if count > 0:
                print("\nFirst 3 rows:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                for i, row in enumerate(rows, 1):
                    print(f"\nRow {i}:")
                    for col, value in zip(columns, row):
                        value_str = str(value)
                        if len(value_str) > 100:  # Truncate long values
                            value_str = value_str[:100] + "..."
                        print(f"  {col[1]}: {value_str}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    sys.exit(main())
