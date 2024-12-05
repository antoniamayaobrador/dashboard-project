from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import psycopg2
import logging
import sys
import torch

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s - %(funcName)s:%(lineno)d",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Device configuration
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Model configuration
MODEL_NAME = "abdulmannan-01/qwen-2.5-1.5b-finetuned-for-sql-generation"

try:
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    logger.info("Model and tokenizer loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

# Database configuration
DATABASE_CONFIG = {
    "dbname": "youtube_analysis",
    "user": "toniamayaobrador",
    "password": "Amaya992",
    "host": "localhost",
    "port": 5432
}

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

### Helper Functions ###

def generate_sql_from_question(question: str) -> dict:
    """
    Uses the Qwen model to convert a question into an SQL query.
    """
    try:
        logger.info(f"Generating SQL query for question: {question}")
        prompt = (
            "You are a powerful text-to-SQL model. Given the SQL tables and natural language question, your job is to write SQL query that answers the question."
            "The tables you can use and join are:\n\n"
            "1. wordcount(word TEXT, count INT, video_id TEXT, created_at TIMESTAMP)\n"
            "2. videos(video_id TEXT, channel_name TEXT, video_title TEXT, total_palabras INT, total_words INT, created_at TIMESTAMP)\n"
            f"Question: {question}\n\n"
            "SQL:"
        )
        logger.debug(f"Prompt created: {prompt}")
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            num_beams=4,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.2,
            early_stopping=True,
        )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        raw_query = generated_text.split("SQL:")[-1].strip()
        logger.debug(f"Raw SQL query: {raw_query}")
        return {
            "query": raw_query,
            "prompt": prompt
        }
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating SQL query")

def sanitize_sql_query(sql_query: str) -> str:
    """
    Cleans and corrects the generated SQL query for PostgreSQL.
    """
    try:
        logger.debug(f"Sanitizing SQL query: {sql_query}")
        cleaned_query = sql_query.replace("`", '"').split(";")[0].strip() + ";"
        logger.debug(f"Sanitized SQL query: {cleaned_query}")
        return cleaned_query
    except Exception as e:
        logger.error(f"Error in sanitize_sql_query: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sanitizing SQL query")

def execute_sql_query(sql_query: str):
    """
    Executes a sanitized SQL query in the PostgreSQL database.
    """
    try:
        logger.info(f"Executing SQL query: {sql_query}")

        # Verificar que sql_query es una cadena de texto
        if not isinstance(sql_query, str):
            logger.error(f"sql_query is not a string: {type(sql_query)}")
            raise ValueError("SQL query must be a string.")

        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchone()
        conn.close()
        final_result = result[0] if result else 0
        logger.info(f"Query result: {final_result}")
        return final_result

    except Exception as e:
        logger.error(f"Error executing SQL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error executing SQL query")


### API Endpoint ###

@router.post("/api/query")
async def query_llm(request: QueryRequest):
    try:
        logger.info(f"Received question: {request.question}")

        # Generar consulta SQL y prompt
        sql_result = generate_sql_from_question(request.question)
        logger.debug(f"Generated SQL result: {sql_result}")  # Should be a dict with 'query' and 'prompt'

        # Sanear la consulta SQL
        raw_query = sql_result.get("query")
        if not raw_query:
            logger.error("No query found in sql_result")
            raise ValueError("No SQL query generated.")

        sanitized_query = sanitize_sql_query(raw_query)
        logger.debug(f"Sanitized SQL query: {sanitized_query}")  # Should be a string

        # Verificar que sanitized_query es una cadena de texto
        if not isinstance(sanitized_query, str):
            logger.error(f"sanitized_query is not a string: {type(sanitized_query)}")
            raise ValueError("Sanitized query is not a string.")

        # Ejecutar la consulta SQL saneada
        results = execute_sql_query(sanitized_query)
        logger.info(f"Final result from query execution: {results}")

        # Retornar solo el resultado
        return {"results": results}

    except Exception as e:
        logger.error(f"Error in query process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

