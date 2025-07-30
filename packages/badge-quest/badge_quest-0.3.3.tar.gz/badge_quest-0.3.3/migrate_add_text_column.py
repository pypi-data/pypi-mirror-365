#!/usr/bin/env python3
"""
Migration script to add text_encrypted column to existing database.
This preserves all existing badge progress and stamps.

Usage:
    python migrate_add_text_column.py [database_path]
    
If no database path is provided, uses the default from environment.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

def backup_database(db_path):
    """Create a backup of the database before migration."""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creating backup at: {backup_path}")
    
    # Use SQLite's backup API
    source = sqlite3.connect(db_path)
    dest = sqlite3.connect(backup_path)
    source.backup(dest)
    source.close()
    dest.close()
    
    return backup_path

def check_column_exists(conn, table_name, column_name):
    """Check if a column already exists in a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)

def migrate_database(db_path):
    """Add text_encrypted column if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        print("\nChecking current database schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reflections'")
        schema = cursor.fetchone()
        if schema:
            print("Current reflections table schema:")
            print(schema[0])
        
        # Check if text_encrypted column already exists
        if check_column_exists(conn, 'reflections', 'text_encrypted'):
            print("\n✓ text_encrypted column already exists!")
        else:
            print("\nAdding text_encrypted column...")
            cursor.execute("ALTER TABLE reflections ADD COLUMN text_encrypted TEXT")
            print("✓ text_encrypted column added successfully!")
        
        # Check if theme_id column exists (added with micro-credentials)
        if not check_column_exists(conn, 'reflections', 'theme_id'):
            print("\nAdding theme_id column...")
            cursor.execute("ALTER TABLE reflections ADD COLUMN theme_id TEXT")
            print("✓ theme_id column added successfully!")
        
        # Verify the migration
        print("\nVerifying migration...")
        cursor.execute("PRAGMA table_info(reflections)")
        columns = cursor.fetchall()
        print("\nReflections table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM reflections")
        total_reflections = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT student_id) FROM reflections")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reflections WHERE text_encrypted IS NOT NULL")
        reflections_with_text = cursor.fetchone()[0]
        
        print(f"\nDatabase statistics:")
        print(f"  Total reflections: {total_reflections}")
        print(f"  Total students: {total_students}")
        print(f"  Reflections with saved text: {reflections_with_text}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

def main():
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Try to use default path from environment
        import os
        from pathlib import Path
        
        db_path = os.environ.get('DATABASE_URL', 'sqlite:///reflections.db')
        if db_path.startswith('sqlite:///'):
            db_path = db_path[10:]  # Remove sqlite:/// prefix
    
    db_path = Path(db_path)
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("Please provide the path to your BadgeQuest database.")
        sys.exit(1)
    
    print(f"BadgeQuest Database Migration")
    print(f"============================")
    print(f"Database: {db_path}")
    print(f"\nThis migration will:")
    print(f"  1. Create a backup of your database")
    print(f"  2. Add text_encrypted column if missing")
    print(f"  3. Preserve all existing badge progress")
    print(f"\nNote: Reflections from before this update won't have saved text,")
    print(f"      but all new reflections will save the text automatically.")
    
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Create backup
    backup_path = backup_database(db_path)
    print(f"✓ Backup created successfully!")
    
    # Run migration
    try:
        migrate_database(db_path)
    except Exception as e:
        print(f"\n❌ Migration failed! Your database has not been modified.")
        print(f"   A backup was created at: {backup_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()