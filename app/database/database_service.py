from app.database.models import get_db_connection

def insert_video_wordcount(video_id, channel_id, channel_name, video_title, wordcount, total_palabras):
    """
    Inserta o actualiza información de wordcount y total de palabras para un video.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Inserta o actualiza el total de palabras y wordcount en la tabla de videos
            query = """
                INSERT INTO videos (video_id, channel_id, channel_name, video_title, total_palabras)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (video_id) DO UPDATE SET total_palabras = EXCLUDED.total_palabras, channel_id = EXCLUDED.channel_id;
            """
            cursor.execute(query, (video_id, channel_id, channel_name, video_title, total_palabras))

            # Inserta cada palabra en la tabla wordcount
            wordcount_query = """
                INSERT INTO wordcount (video_id, channel_id, word, count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (video_id, word) DO UPDATE SET count = EXCLUDED.count;
            """
            cursor.executemany(
                wordcount_query,
                [(video_id, channel_id, word, count) for word, count in wordcount]
            )

        conn.commit()
        print(f"✅ Datos guardados para video {video_id}")
    except Exception as e:
        print(f"❌ Error al insertar datos del video {video_id}: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_wordcount_summary():
    """
    Obtiene el resumen total de todas las palabras.
    Returns:
        Lista de diccionarios con {word, count}
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT word, SUM(count) as total_count
                FROM wordcount
                GROUP BY word
                ORDER BY total_count DESC
                LIMIT 20;
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return [{"word": row["word"], "count": row["total_count"]} for row in results]
    except Exception as e:
        print(f"❌ Error al obtener resumen de wordcount: {e}")
        return []
    finally:
        conn.close()

def get_historical_wordcount_by_channel(channel_name):
    conn = get_db_connection()
    try:
        print(f"Channel name received: {channel_name}")  # Log de entrada
        with conn.cursor() as cursor:
            # Consulta SQL
            query = """
                SELECT w.word, w.count
                FROM wordcount w
                JOIN videos v ON w.video_id = v.video_id
                WHERE v.channel_name = %s
                ORDER BY w.count DESC;
            """
            cursor.execute(query, (channel_name,))
            results = cursor.fetchall()
            print(f"SQL Results: {results}")  # Log de resultados
            
            # Procesa los resultados y convierte RealDictRow a un formato usable
            processed_results = [{"word": row["word"], "count": row["count"]} for row in results]
            
            return processed_results
    except Exception as e:
        print(f"Error fetching historical wordcount: {e}")
        return []
    finally:
        conn.close()

def check_video_exists(video_id):
    """
    Verifica si un video ya existe en la base de datos.
    Args:
        video_id: ID del video a verificar
    Returns:
        Boolean indicando si existe
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = "SELECT 1 FROM wordcount WHERE video_id = %s LIMIT 1;"
            cursor.execute(query, (video_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"❌ Error al verificar video: {e}")
        return False
    finally:
        conn.close()


def save_feedback(feedback_type, result, content, prompt=None):
    """
    Guarda el feedback en la base de datos incluyendo el prompt.


    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO feedback (type, result, content, prompt) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (feedback_type, result, content, prompt or None))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al guardar el feedback: {e}")
        raise

