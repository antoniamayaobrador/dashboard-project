import matplotlib.pyplot as plt
import os

def generar_grafico_wordcount(word_count, output_path="static/wordcount_plot.png"):
    """
    Genera un gráfico de barras para el conteo de palabras y guarda la imagen en la ruta especificada.
    :param word_count: Lista de tuplas (palabra, conteo).
    :param output_path: Ruta donde se guardará el gráfico.
    """
    try:
        # Asegurarse de que el directorio de salida exista
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Extraer palabras y conteos
        palabras, conteos = zip(*word_count)

        # Crear gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar(palabras, conteos)
        plt.xlabel("Palabras")
        plt.ylabel("Conteo")
        plt.title("Frecuencia de palabras en el video")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        # Guardar el gráfico
        plt.savefig(output_path)
        plt.close()
        print(f"Gráfico guardado en {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generando el gráfico de wordcount: {e}")
        return None
