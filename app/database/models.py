import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from app.database.config import DATABASE_CONFIG  

def create_tables():
    # Conectarse a la base de datos usando DATABASE_CONFIG
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    create_wordcount_table_query = """
    CREATE TABLE IF NOT EXISTS wordcount (
        id SERIAL PRIMARY KEY,
        channel_name TEXT NOT NULL,
        video_title TEXT NOT NULL,
        word TEXT NOT NULL,
        count INTEGER NOT NULL,
        video_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_wordcount_table_query)
    
    create_feedback_table_query = """
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        type VARCHAR(20) NOT NULL,
        result BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_feedback_table_query)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tablas creadas con éxito.")

def get_db_connection():
    """
    Establece una conexión a la base de datos PostgreSQL usando la configuración proporcionada.
    """
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise