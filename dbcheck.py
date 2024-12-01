from app.database.models import get_db_connection

def mostrar_tabla(tabla):
    """
    Muestra todos los datos de una tabla específica en la consola.
    Args:
        tabla (str): El nombre de la tabla a consultar.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = f"SELECT * FROM {tabla};"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print(f"La tabla '{tabla}' está vacía.")
    except Exception as e:
        print(f"❌ Error al consultar la tabla '{tabla}': {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Mostrando tabla 'videos' ===")
    mostrar_tabla("videos")

    print("\n=== Mostrando tabla 'wordcount' ===")
    mostrar_tabla("wordcount")


