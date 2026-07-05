# add_phone_column.py
import sqlite3
import os

def add_phone_column():
    db_path = os.path.join(os.path.dirname(__file__), 'edo_odyssey.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(guides)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'phone' not in columns:
            print("📱 Adding phone column to guides table...")
            cursor.execute("ALTER TABLE guides ADD COLUMN phone VARCHAR(20)")
            conn.commit()
            print("✅ Phone column added successfully!")
        else:
            print("✅ Phone column already exists!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(guides)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current columns in guides table: {columns}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    add_phone_column()