#!/usr/bin/env python
"""
Script para crear las tablas de polls manualmente
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.db import connection

def create_poll_tables():
    """Crear tablas de polls manualmente"""
    with connection.cursor() as cursor:
        try:
            print("📝 Creando tabla feed_polls...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_polls (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    question VARCHAR(500) NOT NULL,
                    is_multiple_choice BOOLEAN DEFAULT FALSE,
                    is_anonymous BOOLEAN DEFAULT FALSE,
                    allows_other BOOLEAN DEFAULT FALSE,
                    expires_at TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Tabla feed_polls creada")
            
            print("📝 Creando tabla feed_poll_options...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_poll_options (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    poll_id uuid REFERENCES feed_polls(id) ON DELETE CASCADE,
                    text VARCHAR(200) NOT NULL,
                    order_num INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Tabla feed_poll_options creada")
            
            print("📝 Creando tabla feed_poll_votes...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feed_poll_votes (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    poll_id uuid REFERENCES feed_polls(id) ON DELETE CASCADE,
                    option_id uuid REFERENCES feed_poll_options(id) ON DELETE CASCADE,
                    user_id VARCHAR(10) REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(poll_id, option_id, user_id)
                );
            """)
            print("✅ Tabla feed_poll_votes creada")
            
            # Ahora agregar el constraint de FK para poll_id en feeds_feedpost
            print("📝 Agregando foreign key constraint para poll_id...")
            try:
                cursor.execute("""
                    ALTER TABLE feeds_feedpost 
                    ADD CONSTRAINT feeds_feedpost_poll_id_fkey 
                    FOREIGN KEY (poll_id) REFERENCES feed_polls(id) ON DELETE SET NULL;
                """)
                print("✅ Foreign key constraint agregada")
            except Exception as e:
                print(f"⚠️  Constraint ya existe o error: {e}")
                
            print("🎉 Todas las tablas de polls fueron creadas exitosamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_poll_tables()
