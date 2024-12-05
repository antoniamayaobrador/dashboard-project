from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuración del modelo Qwen
MODEL_NAME = "Qwen/Qwen1.5-1.8B-Chat"
DEVICE = "cpu"

logger.info(f"Iniciando carga del modelo {MODEL_NAME}")

try:
    # Inicializar el modelo y tokenizer
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    logger.info("Modelo y tokenizer cargados exitosamente")
except Exception as e:
    logger.error(f"Error al cargar el modelo: {str(e)}")
    raise

router = APIRouter()

class SearchRequest(BaseModel):
    term: str

def truncate_at_last_period(text: str) -> str:
    """
    Trunca el texto en el último punto encontrado.
    Si no hay punto, devuelve el texto original.
    """
    last_period_index = text.rfind('.')
    if last_period_index != -1:
        return text[:last_period_index + 1]  # Incluimos el punto
    return text



@router.post("/api/define")
async def search_definition(request: SearchRequest):
    try:
        logger.info(f"Recibida solicitud de definición para: {request.term}")
        
        # Crear el prompt
        prompt = f"Eres un experto en perfumería. Define {request.term} de forma breve y profesional en español."
        logger.info(f"Prompt generado: {prompt}")
        
        # Tokenizar
        logger.info("Tokenizando prompt...")
        try:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            logger.info(f"Prompt tokenizado. Forma del tensor: {inputs.input_ids.shape}")
        except Exception as e:
            logger.error(f"Error en tokenización: {str(e)}")
            raise
        
        # Generar definición
        logger.info("Generando definición...")
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=200,
                    num_beams=4,
                    temperature=0.3,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    early_stopping=True
                )
                logger.info(f"Generación completada. Forma del tensor de salida: {outputs.shape}")
        except Exception as e:
            logger.error(f"Error en la generación: {str(e)}")
            raise
        
        # Decodificar
        logger.info("Decodificando respuesta...")
        try:
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"Respuesta completa: {response}")
        except Exception as e:
            logger.error(f"Error en la decodificación: {str(e)}")
            raise
        
        # Procesar respuesta
        definition = response.split(prompt)[-1].strip()
        # Truncar en el último punto
        definition = truncate_at_last_period(definition)
        logger.info(f"Definición final extraída y truncada: {definition}")
        
        # Verificar calidad de la respuesta
        if len(definition) < 10:
            logger.warning("La definición generada es demasiado corta")
            raise ValueError("La definición generada es demasiado corta")
            
        return {"definition": definition, 
                "promt": prompt}
        
    except Exception as e:
        logger.error(f"Error en el proceso de definición: {str(e)}")
        logger.error("Detalles del error:", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno: {str(e)}"
        )

# Verificar estado del modelo al inicio
try:
    logger.info("Verificando estado del modelo...")
    test_prompt = "Define prueba."
    test_inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        test_outputs = model.generate(**test_inputs, max_new_tokens=20)
    test_response = tokenizer.decode(test_outputs[0], skip_special_tokens=True)
    logger.info("Verificación del modelo completada exitosamente")
except Exception as e:
    logger.error(f"Error en la verificación inicial del modelo: {str(e)}")
    raise