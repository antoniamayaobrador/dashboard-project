from transformers import pipeline

# Crear el pipeline de análisis de sentimientos
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", framework="pt")

def analyze_comments(comments):
    """
    Realiza análisis de sentimiento sobre una lista de comentarios y devuelve su valor en estrellas.
    
    Args:
        comments (list): Lista de comentarios (str).
        
    Returns:
        list: Lista de diccionarios con texto, estrellas y confianza.
    """
    analyzed_comments = []
    for comment in comments:
        try:
            # Realizar análisis de sentimiento con truncamiento
            result = sentiment_pipeline(comment, truncation=True)
            stars = int(result[0]["label"].split(" ")[0])  # Extraer las estrellas de la etiqueta (e.g., "5 stars")
            analyzed_comments.append({
                "text": comment[:500],  # Guardar texto truncado para no exceder 512 tokens
                "stars": stars,
                "confidence": result[0]["score"]
            })
        except Exception as e:
            print(f"Error analyzing comment: {comment[:100]}... - {e}")  # Mostrar solo una parte del comentario
    return analyzed_comments
