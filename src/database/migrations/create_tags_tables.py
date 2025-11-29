"""
Migración: Crear tablas tags e item_tags para relación many-to-many

Esta migración crea la infraestructura para el nuevo sistema de tags relacional.
"""

import logging

logger = logging.getLogger(__name__)


def migration_003_create_tags_tables(db):
    """
    Migración 003: Crear tablas tags e item_tags para relación many-to-many

    Esta migración:
    1. Crea tabla 'tags' con nombres únicos (UNIQUE constraint)
    2. Crea tabla pivot 'item_tags' para relación many-to-many
    3. Crea índices para optimización de búsquedas

    Args:
        db: DBManager instance
    """
    try:
        print("\n" + "=" * 80)
        print("MIGRACION 003: Creacion de Tablas tags e item_tags")
        print("=" * 80)

        conn = db.connect()
        cursor = conn.cursor()

        # Verificar si las tablas ya existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tags'")
        tags_exists = cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='item_tags'")
        item_tags_exists = cursor.fetchone() is not None

        if tags_exists and item_tags_exists:
            print("ADVERTENCIA: Las tablas 'tags' e 'item_tags' ya existen.")
            print("   Saltando creacion de tablas...")
            return

        # Paso 1: Crear tabla tags
        print("\n[1/3] Creando tabla 'tags'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                color TEXT,
                description TEXT
            )
        """)
        conn.commit()
        print("   OK Tabla 'tags' creada")

        # Paso 2: Crear índices para tabla tags
        print("   Creando indices para 'tags'...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_usage_count ON tags(usage_count DESC)")
        conn.commit()
        print("   OK Indices creados: idx_tags_name, idx_tags_usage_count")

        # Paso 3: Crear tabla pivot item_tags
        print("\n[2/3] Creando tabla pivot 'item_tags'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (item_id, tag_id),
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("   OK Tabla 'item_tags' creada")

        # Paso 4: Crear índices para tabla item_tags
        print("   Creando indices para 'item_tags'...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_tags_item_id ON item_tags(item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_tags_tag_id ON item_tags(tag_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_tags_composite ON item_tags(tag_id, item_id)")
        conn.commit()
        print("   OK Indices creados: idx_item_tags_item_id, idx_item_tags_tag_id, idx_item_tags_composite")

        # Paso 5: Verificar creación
        print("\n[3/3] Verificando tablas creadas...")

        # Verificar tabla tags
        cursor.execute("PRAGMA table_info(tags)")
        tags_columns = cursor.fetchall()
        print(f"   OK Tabla 'tags': {len(tags_columns)} columnas")

        # Verificar tabla item_tags
        cursor.execute("PRAGMA table_info(item_tags)")
        item_tags_columns = cursor.fetchall()
        print(f"   OK Tabla 'item_tags': {len(item_tags_columns)} columnas")

        # Verificar indices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tags'")
        tags_indices = cursor.fetchall()
        print(f"   OK Indices en 'tags': {len(tags_indices)}")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='item_tags'")
        item_tags_indices = cursor.fetchall()
        print(f"   OK Indices en 'item_tags': {len(item_tags_indices)}")

        print("\n" + "=" * 80)
        print("MIGRACION 003 COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print("\nTablas creadas:")
        print("  - tags (id, name UNIQUE, created_at, updated_at, usage_count, last_used, color, description)")
        print("  - item_tags (item_id, tag_id, created_at) - PRIMARY KEY (item_id, tag_id)")
        print("\nIndices creados:")
        print("  - idx_tags_name - Busqueda rapida por nombre")
        print("  - idx_tags_usage_count - Ordenamiento por uso")
        print("  - idx_item_tags_item_id - Busqueda por item")
        print("  - idx_item_tags_tag_id - Busqueda por tag")
        print("  - idx_item_tags_composite - Busqueda compuesta")
        print("\nSiguiente paso: Ejecutar script de migracion de datos")
        print("   Comando: python util/migrate_tags_to_relational.py")

    except Exception as e:
        logger.error(f"ERROR en migracion 003: {e}")
        print(f"\nERROR durante migracion 003: {e}")
        import traceback
        traceback.print_exc()
        raise
