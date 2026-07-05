import sqlite3
import os

def fix_guide_table():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'edo_odyssey.db')
    
    print(f"📁 Database path: {db_path}")
    print(f"📁 Database exists: {os.path.exists(db_path)}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(guides)")
    columns = cursor.fetchall()
    
    print("\n📋 Current columns in guides table:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check if phone column exists
    column_names = [col[1] for col in columns]
    
    if 'phone' not in column_names:
        print("\n📱 Adding phone column to guides table...")
        cursor.execute("ALTER TABLE guides ADD COLUMN phone VARCHAR(20)")
        conn.commit()
        print("✅ Phone column added successfully!")
    else:
        print("\n✅ Phone column already exists!")
    
    # Verify again
    cursor.execute("PRAGMA table_info(guides)")
    columns = cursor.fetchall()
    
    print("\n📋 Updated columns in guides table:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✅ Done! Restart your Flask app.")

if __name__ == "__main__":
    fix_guide_table()