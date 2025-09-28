#!/usr/bin/env python3
"""
Simple script to view all registered members in the database.
"""

import sqlite3
import os
from datetime import datetime

# Database path - can be overridden with environment variable
DB_PATH = os.getenv('DATABASE_PATH', 'members.db')

def view_all_members():
    """Display all members from the database in a nice format."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, surname, mobile, email, registration_date 
            FROM members 
            ORDER BY registration_date DESC
        ''')
        
        members = cursor.fetchall()
        conn.close()
        
        if not members:
            print("No members registered yet.")
            return
        
        print(f"\n{'='*80}")
        print(f"{'REGISTERED MEMBERS':^80}")
        print(f"{'='*80}")
        print(f"{'ID':<4} {'Name':<15} {'Surname':<15} {'Mobile':<12} {'Email':<25} {'Date':<15}")
        print(f"{'-'*80}")
        
        for member in members:
            id_num, name, surname, mobile, email, reg_date = member
            # Parse the date string
            try:
                date_obj = datetime.fromisoformat(reg_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except:
                formatted_date = reg_date[:10] if reg_date else 'Unknown'
            
            print(f"{id_num:<4} {name[:14]:<15} {surname[:14]:<15} {mobile:<12} {email[:24]:<25} {formatted_date}")
        
        print(f"{'-'*80}")
        print(f"Total members: {len(members)}")
        print(f"{'='*80}\n")
        
    except sqlite3.OperationalError:
        print("Database not found. Run the main application first to create it.")
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    view_all_members()