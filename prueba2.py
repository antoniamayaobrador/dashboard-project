from app.database.models import get_db_connection


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
