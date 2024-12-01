import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import pandas as pd

# Configuración de conexión a la base de datos
DATABASE_CONFIG = {
    "dbname": "youtube_analysis",
    "user": "my_user",
    "password": "my_password",
    "host": "localhost",
    "port": 5432,
}

def save_wordcount(channel_id, channel_name, video_id, video_title, published_at, word_count):
    """
    Guarda el wordcount de un video, evitando duplicados.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO channel_wordcount (channel_id, channel_name, video_id, video_title, published_at, word_count)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (video_id) DO NOTHING;
        """, (channel_id, channel_name, video_id, video_title, published_at, Json(word_count)))
        conn.commit()
    except Exception as e:
        print("Error al guardar el wordcount:", e)
    finally:
        cursor.close()
        conn.close()

def check_video_exists(video_id):
    """
    Comprueba si un video ya existe en la base de datos.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM channel_wordcount WHERE video_id = %s LIMIT 1;", (video_id,))
        exists = cursor.fetchone() is not None
        return exists
    except Exception as e:
        print("Error al verificar existencia del video:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_word_total_by_channel(word):
    """
    Suma el total de ocurrencias de una palabra agrupadas por canal.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT channel_name, SUM((word_count->>%s)::INTEGER) AS total_count
        FROM channel_wordcount
        WHERE word_count ? %s
        GROUP BY channel_name
        ORDER BY total_count DESC;
        """, (word, word))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print("Error al consultar el total de palabras:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def export_wordcount_to_df():
    """
    Exporta los datos de wordcount a un DataFrame.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        query = """
        SELECT channel_name, video_title, word_count, published_at
        FROM channel_wordcount
        ORDER BY published_at DESC;
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print("Error al exportar datos:", e)
        return pd.DataFrame()
    finally:
        conn.close()
