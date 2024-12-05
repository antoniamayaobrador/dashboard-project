from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
import sys
import os

# Configurar para forzar CPU
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
torch.set_num_threads(4)
torch.set_num_interop_threads(1)

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
MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"
DEVICE = "cpu"

logger.info(f"Iniciando carga del modelo {MODEL_NAME} en CPU")

try:
    # Inicializar el modelo y tokenizer forzando CPU
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        device_map=None  # Forzar no usar device mapping automático
    ).to(DEVICE)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Configurar pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = model.config.eos_token_id
    
    logger.info("Modelo y tokenizer cargados exitosamente en CPU")
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
        return text[:last_period_index + 1]
    return text

@router.post("/api/define")
async def search_definition(request: SearchRequest):
    try:
        logger.info(f"Recibida solicitud de definición para: {request.term}")
        
        # Crear el prompt usando el formato de mensajes
        messages = [
            {"role": "system", "content": "Eres un experto en perfumería que proporciona definiciones precisas y profesionales."},
            {"role": "user", "content": f"Define {request.term} de forma breve y profesional en español."}
        ]
        
        logger.info("Aplicando plantilla de chat...")
        try:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            logger.info("Plantilla de chat aplicada correctamente")
        except Exception as e:
            logger.error(f"Error al aplicar plantilla de chat: {str(e)}")
            raise
        
        # Tokenizar
        logger.info("Tokenizando input...")
        try:
            model_inputs = tokenizer([text], return_tensors="pt", padding=True)
            logger.info(f"Input tokenizado. Forma del tensor: {model_inputs.input_ids.shape}")
        except Exception as e:
            logger.error(f"Error en tokenización: {str(e)}")
            raise
        
        # Generar definición
        logger.info("Generando definición...")
        try:
            with torch.inference_mode():
                outputs = model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=200,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id
                )
            logger.info(f"Generación completada. Forma del tensor de salida: {outputs.shape}")
        except Exception as e:
            logger.error(f"Error en la generación: {str(e)}")
            raise
        
        # Procesar las IDs generadas
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(model_inputs.input_ids, outputs)
        ]
        
        # Decodificar
        logger.info("Decodificando respuesta...")
        try:
            definition = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            logger.info(f"Respuesta completa: {definition}")
        except Exception as e:
            logger.error(f"Error en la decodificación: {str(e)}")
            raise
        
        # Truncar en el último punto
        definition = truncate_at_last_period(definition)
        logger.info(f"Definición final extraída y truncada: {definition}")
        
        # Verificar calidad de la respuesta
        if len(definition) < 10:
            logger.warning("La definición generada es demasiado corta")
            raise ValueError("La definición generada es demasiado corta")
            
        return {
            "definition": definition,
            "prompt_system": messages[0]["content"],
            "prompt_user": messages[1]["content"]
        }
        
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
    test_messages = [
        {"role": "system", "content": "Eres un experto en perfumería."},
        {"role": "user", "content": "Define prueba."}
    ]
    test_text = tokenizer.apply_chat_template(
        test_messages,
        tokenize=False,
        add_generation_prompt=True
    )
    test_inputs = tokenizer([test_text], return_tensors="pt", padding=True)
    with torch.inference_mode():
        test_outputs = model.generate(
            test_inputs.input_ids,
            max_new_tokens=20,
            pad_token_id=tokenizer.pad_token_id
        )
    test_response = tokenizer.decode(test_outputs[0], skip_special_tokens=True)
    logger.info("Verificación del modelo completada exitosamente")
except Exception as e:
    logger.error(f"Error en la verificación inicial del modelo: {str(e)}")
    raise