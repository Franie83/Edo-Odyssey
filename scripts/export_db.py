import sqlite3
import json
import os
from datetime import datetime

def export_database():
    db_path = 'edo_odyssey.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    data = {}
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        if rows:
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            data[table] = [dict(zip(columns, row)) for row in rows]
            print(f"✅ Exported {len(rows)} rows from {table}")
    
    conn.close()
    
    # Save to JSON file
    with open('data_export.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"\n✅ Data exported to data_export.json")
    print(f"📊 Tables exported: {', '.join(data.keys())}")
    return data

if __name__ == "__main__":
    export_database()