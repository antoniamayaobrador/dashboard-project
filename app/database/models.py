import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from app.database.config import DATABASE_CONFIG  

def create_tables():
    # Conectarse a la base de datos usando DATABASE_CONFIG
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    # Tabla wordcount
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

    # Tabla feedback
    create_feedback_table_query = """
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        type VARCHAR(20) NOT NULL,
        result BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_feedback_table_query)

    # Tabla videos
    create_videos_table_query = """
    CREATE TABLE IF NOT EXISTS videos (
        video_id VARCHAR NOT NULL PRIMARY KEY,
        channel_name VARCHAR NOT NULL,
        video_title VARCHAR NOT NULL,
        total_palabras INTEGER,
        total_words INTEGER DEFAULT 0,
        channel_id VARCHAR(255)
    );
    """
    cursor.execute(create_videos_table_query)

    # Tabla brands
    create_brands_table_query = """
    CREATE TABLE IF NOT EXISTS brands (
        brand_id SERIAL PRIMARY KEY,
        brand VARCHAR NOT NULL,
        video_id VARCHAR NOT NULL,
        FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
    );
    """
    cursor.execute(create_brands_table_query)

    # Confirmar los cambios
    conn.commit()

    # Cerrar la conexión
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