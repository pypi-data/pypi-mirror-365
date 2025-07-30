#!/usr/bin/env python3
"""
Check if reflections in the database have stored text.
This helps determine which version of BadgeQuest was running.
"""

import sqlite3
import sys
import base64
from pathlib import Path

def check_database(db_path):
    """Check database for text storage."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if text_encrypted column exists
        cursor.execute("PRAGMA table_info(reflections)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'text_encrypted' not in columns:
            print("❌ text_encrypted column not found - you're running an old version (pre-v0.3.0)")
            return
        
        print("✅ text_encrypted column exists")
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM reflections")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reflections WHERE text_encrypted IS NOT NULL")
        with_text = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reflections WHERE text_encrypted IS NULL")
        without_text = cursor.fetchone()[0]
        
        print(f"\nDatabase Statistics:")
        print(f"  Total reflections: {total}")
        print(f"  With saved text: {with_text}")
        print(f"  Without saved text: {without_text}")
        
        if with_text > 0:
            print(f"\n✅ You have {with_text} reflections with saved text!")
            print("   Your BadgeQuest includes text saving (v0.3.0+)")
            
            # Show a sample
            cursor.execute("""
                SELECT week_id, timestamp, LENGTH(text_encrypted) as text_len
                FROM reflections 
                WHERE text_encrypted IS NOT NULL 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            
            print("\nRecent reflections with text:")
            for row in cursor.fetchall():
                print(f"  - Week {row[0]} on {row[1][:10]} ({row[2]} chars stored)")
                
            # Decode and show word count of one
            cursor.execute("""
                SELECT text_encrypted 
                FROM reflections 
                WHERE text_encrypted IS NOT NULL 
                LIMIT 1
            """)
            sample = cursor.fetchone()[0]
            if sample:
                try:
                    decoded = base64.b64decode(sample).decode('utf-8')
                    word_count = len(decoded.split())
                    print(f"\nSample reflection has {word_count} words")
                except:
                    pass
        else:
            print("\n⚠️  No reflections have saved text")
            print("   Either:")
            print("   1. Text saving wasn't enabled when these were submitted")
            print("   2. The forms weren't sending text properly")
            
    finally:
        conn.close()

def main():
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        import os
        db_path = os.environ.get('DATABASE_URL', 'sqlite:///reflections.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        sys.exit(1)
    
    print(f"BadgeQuest Database Text Check")
    print(f"==============================")
    print(f"Database: {db_path}\n")
    
    check_database(db_path)

if __name__ == "__main__":
    main()