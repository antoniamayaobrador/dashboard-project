# app/database/config.py
DATABASE_CONFIG = {
    "dbname": "youtube_analysis",  # Reemplaza con el nombre de tu base de datos
    "user": "toniamayaobrador",       # Reemplaza con tu usuario de PostgreSQL
    "password": "Amaya992",      # Reemplaza con tu contraseña de PostgreSQL
    "host": "localhost",            # Usa "localhost" si está en tu máquina local
    "port": 5432                    # Puerto por defecto de PostgreSQL
}

import psycopg2
from datetime import datetime


def save_wordcount(channel_name, video_title, video_id, word_count):
    """
    Guarda el wordcount en la tabla `wordcount` en formato fila por palabra.
    """
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    try:
        # Inserta cada palabra y su conteo como una fila separada
        for word, count in word_count:
            cursor.execute("""
                INSERT INTO wordcount (channel_name, video_title, video_id, word, count, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (channel_name, video_title, video_id, word, count, datetime.now()))

        conn.commit()
        print(f"✅ Wordcount guardado para el video: {video_id}")
    except Exception as e:
        print(f"❌ Error al guardar el wordcount: {e}")
    finally:
        cursor.close()
        conn.close()
