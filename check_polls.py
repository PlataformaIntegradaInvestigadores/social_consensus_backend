#!/usr/bin/env python
"""
Script para verificar tablas de polls
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.db import connection

def check_poll_tables():
    """Verificar tablas de polls"""
    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name LIKE '%poll%';
            """)
            
            tables = cursor.fetchall()
            print("📋 Tablas de polls encontradas:")
            for table in tables:
                print(f"  - {table[0]}")
                
            if not tables:
                print("❌ No se encontraron tablas de polls")
                
            # Verificar si existe feed_polls específicamente
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'feed_polls';
            """)
            
            feed_polls = cursor.fetchone()
            if feed_polls:
                print("✅ Tabla feed_polls existe")
            else:
                print("❌ Tabla feed_polls NO existe")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_poll_tables()
