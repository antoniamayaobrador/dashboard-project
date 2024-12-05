import nltk
from nltk.corpus import stopwords
from collections import Counter
import string

# Descargar stopwords si no están descargadas
nltk.download("stopwords")

# Lista ampliada de stopwords (adicionales)
stopwords_adicionales = [
    # Stopwords en Español
    'el', 'la', 'los', 'las', 'le', 'les', 'un', 'una', 'unos', 'unas', 'del', 'de', 'en', 'con', 'para', 'por', 'sobre',
    'entre', 'sin', 'se', 'que', 'y', 'a', 'o', 'como', 'es', 'ser', 'hacer', 'estar', 'tener', 'haber', 'puede', 
    'bien', 'muy', 'no', 'sí', 'también', 'ni', 'cuando', 'porque', 'mientras', 'este', 'estos', 'estas', 'ahora', 'ya',
    'ahí', 'aquel', 'aquella', 'por qué', 'donde', 'así', 'algo', 'alguien', 'cualquiera', 'yo', 'tú', 'él', 'ella', 
    'nosotros', 'vosotros', 'ellos', 'ellas', 'hacer', 'tener', 'saber', 'ver', 'ir', 'comer', 'beber', 'pensar', 'te', 
    'aquí', 'muy', 'mucho', 'nada', 'todo', 'uno', 'todos', 'mismo', 'nos', 'ha', 'después', 'delante', 'tras',
    'durante', 'acerca', 'fuera', 'toda', 'cada', 'casi', 'tan', 'solamente', 'me', 'te', 'este', 'esa', 'quien',
    'su', 'para', 'ese', 'esos', 'estas', 'como', 'cual', 'alguno', 'pero', 'tampoco', 'uno', 'dos', 'tres', 'cuatro',
    'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 
    'diecisiete', 'dieciocho', 'diecinueve', 'veinte', 'principio', 'final', 'hace', 'dice', 'pues', 'entonces', 
    'claro', 'tema', 'hecho', 'dicho', 'sido', 'ha', 'has', 'he', 'hemos', 'habéis', 'adiós', 'hola', 'antes', 'luego', 
    'dices', 'vale', 'parece', 'cree', 'creemos', 'creéis', 'creen', 'sé', 'sabes', 'sabemos', 'sabéis', 'cómo', 'si', 'eh', 'ah', 'incluso',
    'además', 'también', 'oh', 'ay', 'uy', 'oy', 'ei', 'ey', 'voy', 'vas', 'va', 'vamos', 'vais', 'van', 'decir', 'hablar', 'siempre',
    'nunca', 'gustó', 'gusté', 'gustaste', 'gustamos', 'gustásteis', 'gustaron', 'fui', 'fuiste', 'fuimos', 'tengo', 'tienes', 
    'tiene', 'tenemos', 'tenéis', 'tienen', 'puedo', 'puedes', 'puede', 'podemos', 'podéis', 'pueden',

    # Stopwords Adicionales en Español
    'aunque', 'sobre', 'bajo', 'tras', 'excepto', 'salvo', 'ya', 'todavía', 'hasta', 'incluso', 'aún', 'quizá', 'siquiera',
    'hoy', 'mañana', 'ayer', 'hace', 'tal', 'cada', 'nadie', 'ninguno', 'ninguna', 'cual', 'demás', 'debe', 'igual', 'lugar',
    'vez', 'misma', 'mayor', 'peor', 'menor', 'mejor', 'nuevo', 'alrededor', 'pronto', 'tarde', 'lejos', 'cerca', 'allí',

    # Stopwords en Inglés
    'the', 'and', 'a', 'an', 'of', 'to', 'in', 'on', 'at', 'with', 'for', 'by', 'about', 'as', 'into', 'through', 'from', 
    'up', 'down', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 
    'all', 'any', 'both', 'each', 'few', 'more', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 
    'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'has', 'have', 'had', 'do', 
    'does', 'did', 'be', 'is', 'are', 'was', 'were', 'being', 'been', 'having', 'i', 'you', 'he', 'she', 'it', 'we', 
    'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'their', 'our', 'yours', 'mine', 'hers', 'what', 'like', 'in', 'out',

    'although', 'towards', 'against', 'beyond', 'below', 'unless', 'despite', 'whether', 'until', 'along', 'either', 
    'meanwhile', 'soon', 'sometime', 'neither', 'anyone', 'somebody', 'everybody', 'nobody', 'someone', 'anything', 
    'everything', 'nothing', 'whatever', 'whenever', 'wherever', 'whichever', 'whomever', 'whose', 'whom', 'around', 
    'within', 'outside', 'inside', 'nearby', 'almost', 'several', 'plenty', 'fewest', 'greatest', 'less', 'least', 
    'fewer', 'whereas', 'beside', 'alongside'
]


# Función para limpiar el texto y contar las palabras
def limpiar_y_contar(texto, idioma="spanish"):
    """
    Limpia el texto eliminando stopwords y realiza un conteo de palabras.
    """
    try:
        # Convertir a minúsculas y eliminar puntuación
        texto = texto.lower()
        texto = texto.translate(str.maketrans("", "", string.punctuation))

        # Dividir el texto en palabras
        palabras = texto.split()

        # Cargar las stopwords en el idioma especificado
        stop_words = set(stopwords.words(idioma)) | set(stopwords_adicionales)  # Unimos las stopwords por idioma con las adicionales

        # Filtrar stopwords
        palabras_filtradas = [palabra for palabra in palabras if palabra not in stop_words]

        # Contar la frecuencia de palabras
        conteo = Counter(palabras_filtradas)

        # Retornar los conteos como una lista de tuplas
        return conteo.most_common(20)

    except Exception as e:
        print(f"Error al limpiar y contar palabras: {e}")
        return None




# En text_analysis.py
class TextAnalyzer:
    def __init__(self):
        self.PERFUME_BRANDS = [
    # Marcas comerciales populares
    "Tom Ford", "Dior", "Chanel", "Gucci", "Yves Saint Laurent", "Versace", "Hermès", 
    "Prada", "Dolce & Gabbana", "Givenchy", "Burberry", "Armani", "Hugo Boss", "Calvin Klein",
    "Lacoste", "Marc Jacobs", "Ralph Lauren", "Paco Rabanne", "Carolina Herrera", 
    "Jean Paul Gaultier", "Valentino", "Balenciaga", "Bulgari", "Fendi", "Lancome", 
    "Victoria's Secret", "tom ford", 'dior', 'chanel', 'gucci', 'yves saint laurent', 'versace', 'hermes',
    'prada', 'dolce & gabbana', 'givenchy', 'burberry', 'armani', 'hugo boss', 'calvin klein', 
    'lacoste', 'marc jacobs', 'ralph lauren', 'paco rabanne', 'carolina herrera', 'jean paul gaultier', 'Zara', 'Mercadona',

    # Marcas de nicho
    "Amouage", "Creed", "Maison Francis Kurkdjian", "Byredo", "Le Labo", "Diptyque", 
    "Frederic Malle", "Jo Malone", "Penhaligon's", "Aesop", "Xerjoff", "Clive Christian", 
    "Parfums de Marly", "Roja Parfums", "Mancera", "Montale", "Initio", "Tiziana Terenzi", 
    "Nishane", "Serge Lutens", "Comme des Garçons", "Etat Libre d'Orange", "Zoologist", 
    "Acqua di Parma", "BDK Parfums", "Carner Barcelona", "Memo Paris", "Floris London",
    
    # Otros nichos relevantes
    "Bond No.9", "Vilhelm Parfumerie", "Histoires de Parfums", "Masque Milano", 
    "The Different Company", "Atelier Cologne", "Maison Margiela", "Ormonde Jayne", 
    "House of Oud", "Olfactive Studio", "The Harmonist"
]

    
    def find_brands_in_transcription(self, transcription):
        detected_brands = []
        transcription_lower = transcription.lower()
        
        for brand in self.PERFUME_BRANDS:
            if brand.lower() in transcription_lower:
                detected_brands.append(brand)
        
        return detected_brands
    
   