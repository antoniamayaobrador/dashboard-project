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
SMALL_CHAT_MODEL_CON_CASTELLANO = "Qwen/Qwen2-1.5B-Instruct"
DEVICE = "cpu"

# Optimizaciones de PyTorch
torch.set_grad_enabled(False)
torch.cuda.empty_cache()
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_initialized = False

    def initialize(self):
        try:
            print("Cargando modelo Qwen...")
            self.model = AutoModelForCausalLM.from_pretrained(
                SMALL_CHAT_MODEL_CON_CASTELLANO,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                device_map="cpu"
            )
            
            print("Cargando tokenizer Qwen...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                SMALL_CHAT_MODEL_CON_CASTELLANO,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.config.pad_token_id = self.model.config.eos_token_id

            self.is_initialized = True
            print("Modelo y tokenizer inicializados correctamente.")
            return True
        except Exception as e:
            print(f"❌ Error al inicializar modelos/tokenizer: {str(e)}")
            self.is_initialized = False
            return False

    def get_model_and_tokenizer(self):
        if not self.is_initialized:
            success = self.initialize()
            if not success:
                raise ValueError("No se pudo inicializar el modelo y tokenizer")
        return self.model, self.tokenizer

# Inicialización del gestor de modelos
model_manager = ModelManager()

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
        model = whisper.load_model("small", device="cpu")
        
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
        # Get model and tokenizer from the manager
        model, tokenizer = model_manager.get_model_and_tokenizer()
        
        prompt = f"Resume el siguiente texto en español manteniendo las ideas clave: {texto}"
        messages = [
            {"role": "system", "content": "Eres un asistente que proporciona resúmenes de textos."},
            {"role": "user", "content": prompt}
        ]

        with torch.no_grad():
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Fix: Properly handle the input encoding
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            
            # Move inputs to device if needed
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
            
            # Generate summary
            generated_ids = model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                num_return_sequences=1,
                pad_token_id=tokenizer.pad_token_id
            )
            
            # Process only the new tokens (exclude input tokens)
            generated_ids = generated_ids[:, inputs['input_ids'].shape[1]:]
            
            # Decode the generated text
            resumen = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return resumen.strip()
            
    except Exception as e:
        print(f"Error al generar el resumen: {str(e)}")
        traceback.print_exc()  # Add this to get more detailed error information
        return None
    
def procesar_video(video_url):
    try:
        print("\n=== Intentando el flujo con YouTubeTranscriptApi ===")
        analyzer = TextAnalyzer()
        
        # Initialize model manager if not already initialized
        if not model_manager.is_initialized:
            if not model_manager.initialize():
                raise ValueError("No se pudo inicializar el modelo")
        
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