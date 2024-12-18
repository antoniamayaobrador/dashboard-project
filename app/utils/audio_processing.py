# Importaciones
import os
import re
import time
import yt_dlp
import whisper
import speech_recognition as sr
from vosk import Model, KaldiRecognizer
import wave
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from youtube_transcript_api import YouTubeTranscriptApi
import torch
from app.utils.text_analysis import limpiar_y_contar, TextAnalyzer

# Set environment variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configuración de los modelos
SMALL_CHAT_MODEL_CON_CASTELLANO = "Qwen/Qwen2-1.5B-Instruct"  # Asegúrate de que el nombre es correcto
DEVICE = "cpu"  # Forzar uso de CPU

def init_models():
    try:
        print("Cargando modelo Qwen...")
        qwen_model = AutoModelForCausalLM.from_pretrained(
            SMALL_CHAT_MODEL_CON_CASTELLANO,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto"
        ).to(DEVICE)
        
        print("Cargando tokenizer Qwen...")
        qwen_tokenizer = AutoTokenizer.from_pretrained(SMALL_CHAT_MODEL_CON_CASTELLANO)
        
        if qwen_tokenizer.pad_token is None:
            qwen_tokenizer.pad_token = qwen_tokenizer.eos_token
            qwen_model.config.pad_token_id = qwen_model.config.eos_token_id

        print("Modelo y tokenizer inicializados correctamente.")
        return qwen_model, qwen_tokenizer
    except Exception as e:
        print(f"❌ Error al inicializar modelos/tokenizer: {e}")
        return None, None

# Inicialización global de modelos
qwen_model, qwen_tokenizer = init_models()

# Verificación del modelo y tokenizador
if not qwen_model or not qwen_tokenizer:
    raise ValueError("El modelo o el tokenizer no se inicializaron correctamente.")

def download_audio_yt_dlp(video_url):
    try:
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'keepvideo': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        return output_dir
    except Exception as e:
        print(f"Error al descargar audio: {e}")
        return None

def transcribir_audio_whisper(audio_file):
    try:
        print("\nIniciando transcripción con Whisper...")
        model = whisper.load_model("small", device="cpu")  # Forzar FP32 y CPU
        
        print("Transcribiendo con Whisper...")
        result = model.transcribe(audio_file, language="es", task="transcribe")
        
        if result and "text" in result and result["text"].strip():
            print("Transcripción completada con Whisper.")
            return result["text"]
        else:
            print("La transcripción con Whisper está vacía.")
            return None
                
    except Exception as e:
        print(f"Error en la transcripción con Whisper: {e}")
        return None

def obtener_transcripcion_youtube(video_url):
    try:
        video_id = video_url.split("https://www.youtube.com/watch?v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es'])
        transcription = " ".join([item['text'] for item in transcript])
        return transcription
    except Exception as e:
        print(f"Error al obtener la transcripción con YouTubeTranscriptApi: {str(e)}")
        return None

def puntuar_texto_en_espanol(texto):
    try:
        texto = re.sub(r'\.(\s*)([a-záéíóúñ])', lambda x: x.group(1) + x.group(2).upper(), texto)
        texto = re.sub(r'\s+([.,!?])', r'\1', texto)
        if not texto.endswith('.'):
            texto += '.'
        return texto
    except Exception as e:
        print(f"Error al puntuar el texto: {e}")
        return texto

def generar_resumen(texto):
    try:
        prompt = f"Resume el siguiente texto en español manteniendo las ideas clave: {texto}"
        messages = [
            {"role": "system", "content": "Eres un asistente que proporciona resúmenes de textos."},
            {"role": "user", "content": prompt}
        ]

        text = qwen_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = qwen_tokenizer([text], return_tensors="pt").to(DEVICE)
        generated_ids = qwen_model.generate(model_inputs.input_ids, max_new_tokens=512)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        resumen = qwen_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return resumen
        
    except Exception as e:
        print(f"Error al generar el resumen: {e}")
        return None

def procesar_video(video_url):
    try:
        print("\n=== Intentando el flujo con YouTubeTranscriptApi ===")
        analyzer = TextAnalyzer()
        
        transcription = obtener_transcripcion_youtube(video_url)
        if not transcription:
            print("No se pudo obtener la transcripción, iniciando flujo alternativo...")
            return None

        print("\nPuntuando texto...")
        puntuado_texto = puntuar_texto_en_espanol(transcription)
        
        print("\nGenerando resumen...")
        resumen = generar_resumen(puntuado_texto)
        if not resumen:
            raise ValueError("No se pudo generar el resumen correctamente.")

        print("\nAnalizando texto...")
        wordcount = limpiar_y_contar(transcription)
        detected_brands = analyzer.find_brands_in_transcription(transcription)
        total_palabras = sum(frecuencia for _, frecuencia in wordcount)

        return {
            "transcription": transcription,
            "punctuated_text": puntuado_texto,
            "summary": resumen,
            "wordcount": wordcount,
            "brands": detected_brands,
            "total_palabras": total_palabras,
        }

    except Exception as e:
        print(f"\n❌ Error en el flujo: {str(e)}")
        return None
