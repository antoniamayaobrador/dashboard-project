from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import psycopg2
from psycopg2.extras import Json
import logging
import sys
import torch
from app.utils.search_llm import model, tokenizer


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)



# Configuración de la base de datos PostgreSQL
DATABASE_CONFIG = {
    "dbname": "youtube_analysis", 
    "user": "toniamayaobrador",       
    "password": "Amaya992",     
    "host": "localhost",            
    "port": 5432           
}

# Router de FastAPI
router = APIRouter()

# Modelo de solicitud
class QueryRequest(BaseModel):
    question: str

# Generación de SQL desde el prompt
def generate_sql_from_question(question: str) -> str:
    """
    Usa el modelo Qwen para convertir una pregunta en una consulta SQL.
    """
    try:
        logger.info(f"Generando consulta SQL para la pregunta: {question}")
        
        # Crear el prompt detallado
        prompt = (
    "You are a powerful text-to-SQL model. Given the SQL tables and natural language question, your job is to write SQL query that answers the question."
    "The tables you can use and join are :\n\n"
    "1. videos(video_id TEXT, channel_name TEXT, video_title TEXT, total_palabras INT, total_words INT, created_at TIMESTAMP)\n"
    "2. wordcount(word TEXT, count INT, video_id TEXT, created_at TIMESTAMP)\n\n"
    f"Question: {question}\n\n" 
    "SQL:"
)



        

        # Tokenizar la pregunta
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Generar texto con el modelo
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                num_beams=4,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.2,
                early_stopping=True,
            )
        
        # Decodificar la respuesta
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer la consulta SQL del texto generado
        sql_query = generated_text.split("SQL:")[-1].strip()
        
        logger.info(f"Consulta SQL generada: {sql_query}")
        return sql_query
    except Exception as e:
        logger.error(f"Error generando consulta SQL: {str(e)}")
        raise ValueError("No se pudo generar la consulta SQL.")



import re

def sanitize_sql_query(sql_query: str) -> str:
    """
    Limpia y corrige la consulta SQL generada para PostgreSQL.
    """
    # Dividir en líneas y eliminar duplicados
    lines = sql_query.splitlines()
    seen = set()
    cleaned_lines = []
    for line in lines:
        if line not in seen:
            cleaned_lines.append(line.strip())
            seen.add(line)
    cleaned_query = " ".join(cleaned_lines)

    # Reemplazar comillas inclinadas por comillas dobles
    cleaned_query = cleaned_query.replace("`", '"')

    # Eliminar consultas repetitivas o incompletas después del primer punto y coma
    cleaned_query = cleaned_query.split(";")[0].strip() + ";"

    # Corregir alias incorrectos en columnas y tablas
    COLUMN_ALIAS_MAPPING = {
        "video_id": "v",
        "channel_name": "v",
        "video_title": "v",
        "total_palabras": "v",
        "total_words": "v",
        "created_at": "wc"
    }
    for column, alias in COLUMN_ALIAS_MAPPING.items():
        pattern = rf"(?<!\w)\w+\.{column}(?!\w)"  # Busca `<alias_incorrecto>.<column>`
        correct_alias = f"{alias}.{column}"
        cleaned_query = re.sub(pattern, correct_alias, cleaned_query)

    # Validar las tablas después de FROM
    VALID_TABLES = ["videos", "wordcount"]
    from_match = re.search(r"FROM\s+(\w+)", cleaned_query, re.IGNORECASE)
    if from_match:
        table_name = from_match.group(1)
        if table_name not in VALID_TABLES:
            raise ValueError(f"Tabla inválida encontrada en la consulta: {table_name}")

    # Corregir el uso incorrecto de ASC o DESC en condiciones WHERE
    cleaned_query = re.sub(r"AND\s+(\w+\.\w+)\s+(ASC|DESC)", r"ORDER BY \1 \2", cleaned_query, flags=re.IGNORECASE)

    # Asegurar que `ORDER BY` tenga un campo válido
    if "ORDER BY" in cleaned_query and not re.search(r"ORDER BY\s+\w+\.\w+", cleaned_query):
        cleaned_query = re.sub(r"ORDER BY\s+\w+", "", cleaned_query).strip()

    # Asegurar el uso correcto de funciones de agregación
    if re.search(r"SUM\(|COUNT\(", cleaned_query):
        cleaned_query = re.sub(r"ORDER BY\s+\w+\.\w+\s+(ASC|DESC)", "", cleaned_query, flags=re.IGNORECASE)

    # Manejar funciones anidadas y validar paréntesis
    stack = []
    for char in cleaned_query:
        if char == "(":
            stack.append(char)
        elif char == ")" and stack:
            stack.pop()
    if stack:  # Si hay paréntesis no balanceados
        cleaned_query = re.sub(r"\([^)]*$", "", cleaned_query)

    # Corregir condiciones WHERE incompletas
    if re.search(r"WHERE\s+(\w+\.\w+)\s*$", cleaned_query):
        cleaned_query = cleaned_query.rstrip(";") + " = TRUE;"

    # Asegurar que `ORDER BY` y `LIMIT` estén correctos
    if "ORDER BY" in cleaned_query and "LIMIT" not in cleaned_query:
        cleaned_query += " LIMIT 1;"

    # Asegurar que la consulta termine con un único punto y coma
    cleaned_query = re.sub(r";+", ";", cleaned_query)

    # Eliminar espacios redundantes
    cleaned_query = re.sub(r"\s{2,}", " ", cleaned_query).strip()

    return cleaned_query

def restructure_query_with_qwen(cleaned_query: str) -> str:
    """
    Usa el modelo Qwen para reestructurar y validar la consulta SQL.
    """
    try:
        logger.info("Reestructurando la consulta usando Qwen...")
        
        prompt = (
            "Teniendo en cuenta las tablas:\n\n"
            "1. videos(video_id TEXT, channel_name TEXT, video_title TEXT, total_palabras INT, total_words INT, created_at TIMESTAMP)\n"
            "2. wordcount(word TEXT, count INT, video_id TEXT, created_at TIMESTAMP)\n\n"
            f"Consulta recibida: {cleaned_query}\n\n"
            "Por favor, estructura esta consulta para que sea UNA  única consulta SQL válida en PostgreSQL, manteniendo la información original. Sólo estructura y corrige "
            "terminando con un único punto y coma (;).\n\n"
            "Consulta SQL:"
        )
        
        # Tokenización e inferencia
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                num_beams=4,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.2,
                early_stopping=True,
            )
        
        # Decodificar respuesta
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        cleaned_query_qwen = generated_text.split("Consulta SQL:")[-1].strip()
        logger.info(f"Consulta reestructurada por Qwen: {cleaned_query_qwen}")
        return cleaned_query_qwen
    except Exception as e:
        logger.error(f"Error al usar Qwen para reestructurar la consulta: {str(e)}")
        raise ValueError("No se pudo reestructurar la consulta SQL usando Qwen.")


def sanitize_sql_query_secondary(cleaned_query_qwen: str) -> str:
    """
    Limpia y corrige nuevamente la consulta SQL reestructurada por Qwen para PostgreSQL.
    """
    try:
        logger.info("Aplicando limpieza secundaria a la consulta SQL...")
        
        # Reutilizamos las reglas de limpieza de la función inicial
        sanitized_query = sanitize_sql_query(cleaned_query_qwen)

        logger.info(f"Consulta limpia final: {sanitized_query}")
        return sanitized_query
    except Exception as e:
        logger.error(f"Error en la limpieza secundaria de la consulta SQL: {str(e)}")
        raise ValueError("No se pudo limpiar la consulta SQL secundaria.")


def generate_final_query(question: str) -> str:
    """
    Genera la consulta final lista para ser ejecutada en la base de datos PostgreSQL.
    """
    try:
        # Limpieza inicial
        logger.info(f"Generando consulta para la pregunta: {question}")
        initial_cleaned_query = sanitize_sql_query(generate_sql_from_question(question))

        # Reestructuración con Qwen
        restructured_query = restructure_query_with_qwen(initial_cleaned_query)

        # Limpieza secundaria
        final_query = sanitize_sql_query_secondary(restructured_query)

        logger.info(f"Consulta SQL final lista para ejecución: {final_query}")
        return final_query
    except Exception as e:
        logger.error(f"Error generando la consulta final: {str(e)}")
        raise ValueError("Error generando la consulta SQL final.")



def execute_sql_query(final_query: str):
    """
    Ejecuta una consulta SQL en la base de datos PostgreSQL.
    """
    try:
        logger.info(f"Ejecutando SQL saneado: {final_query}")
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(final_query)
        result = cursor.fetchone()  # Obtener la primera fila
        conn.close()

        if result:
            # Asumimos que la primera columna tiene el resultado esperado
            return result[0]  # Devuelve el valor directamente
        else:
            return 0  # Si no hay resultado, retorna 0

    except Exception as e:
        logger.error(f"Error al ejecutar SQL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al ejecutar consulta SQL")



@router.post("/api/query")
async def query_llm(request: QueryRequest):
    """
    Endpoint para procesar preguntas y devolver resultados de SQL.
    """
    try:
        logger.info(f"Recibida pregunta: {request.question}")
        
        # Generar consulta SQL
        sql_query = generate_sql_from_question(request.question)
        
        # Ejecutar consulta SQL
        results = execute_sql_query(sql_query)
        
        return {"query": sql_query, "results": results, "prompt" : prompt}
    except Exception as e:
        logger.error(f"Error en el proceso de consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
