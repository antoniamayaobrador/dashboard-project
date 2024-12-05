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
DEVICE = "cpu"  # Force CPU usage

def init_models():
    try:
        qwen_model = AutoModelForCausalLM.from_pretrained(
            SMALL_CHAT_MODEL_CON_CASTELLANO,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto"
        ).to(DEVICE)
        qwen_tokenizer = AutoTokenizer.from_pretrained(SMALL_CHAT_MODEL_CON_CASTELLANO)
        
        if qwen_tokenizer.pad_token is None:
            qwen_tokenizer.pad_token = qwen_tokenizer.eos_token
            qwen_model.config.pad_token_id = qwen_model.config.eos_token_id

        return qwen_model, qwen_tokenizer
    except Exception as e:
        print(f"Error initializing models: {e}")
        return None, None
    
# Initialize models globally
qwen_model, qwen_tokenizer = init_models()

def download_audio_yt_dlp(video_url):
    try:
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'keepvideo': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        return output_dir
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def transcribir_audio_whisper(audio_file):
    try:
        print("\nIniciando transcripción con Whisper...")
        model = whisper.load_model("small")
        
        print("Transcribiendo con Whisper...")
        result = model.transcribe(
            audio_file,
            language="es",
            task="transcribe"
        )
        
        if result and "text" in result and result["text"].strip():
            print("Transcripción completada con Whisper.")
            return result["text"]
        else:
            print("La transcripción con Whisper está vacía.")
            return None
                
    except Exception as e:
        print(f"Error en la transcripción con Whisper: {e}")
        return None

def transcribir_audio_google(audio_file, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"\nIntento de transcripción con Google {attempt + 1}/{max_retries}")
            recognizer = sr.Recognizer()
            
            recognizer.pause_threshold = 0.8
            recognizer.energy_threshold = 300
            
            with sr.AudioFile(audio_file) as source:
                print("Leyendo archivo de audio...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Grabando audio...")
                audio = recognizer.record(source)
                
                print("Realizando transcripción...")
                transcription = recognizer.recognize_google(
                    audio, 
                    language='es-ES',
                    show_all=False
                )
                if transcription and transcription.strip():
                    print("Transcripción completada con Google Speech.")
                    return transcription
                    
        except sr.RequestError as e:
            print(f"Error de solicitud en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Esperando antes de reintentar...")
                time.sleep(2)
            
        except Exception as e:
            print(f"Error en intento {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Esperando antes de reintentar...")
                time.sleep(2)
    
    print("Se agotaron los intentos con Google Speech.")
    return None

def transcribir_audio_vosk(audio_file):
    try:
        print("\nIniciando transcripción con Vosk...")
        model = Model(lang="es")
        
        print("Abriendo archivo de audio...")
        wf = wave.open(audio_file, "rb")
        
        print("Inicializando reconocedor...")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        print("Transcribiendo audio...")
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part = json.loads(rec.Result())
                if 'text' in part and part['text'].strip():
                    results.append(part['text'])
        
        part = json.loads(rec.FinalResult())
        if 'text' in part and part['text'].strip():
            results.append(part['text'])
            
        transcription = ' '.join(results)
        
        if transcription.strip():
            print("Transcripción completada con Vosk.")
            return transcription
        else:
            print("La transcripción con Vosk está vacía.")
            return None
            
    except Exception as e:
        print(f"Error en la transcripción con Vosk: {e}")
        return None

def transcribir_audio(audio_file):
    # 1. Intentar con Whisper
    transcription = transcribir_audio_whisper(audio_file)
    if transcription:
        return transcription
        
    print("\nWhisper falló, intentando con Google Speech...")
    
    # 2. Si falla Whisper, intentar con Google Speech
    transcription = transcribir_audio_google(audio_file)
    if transcription:
        return transcription
        
    print("\nGoogle Speech falló, intentando con Vosk...")
    
    # 3. Si falla Google Speech, intentar con Vosk
    transcription = transcribir_audio_vosk(audio_file)
    return transcription

def obtener_transcripcion_youtube(video_url):
    try:
        video_id = video_url.split("https://www.youtube.com/watch?v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['es'])
        transcription = " ".join([item['text'] for item in transcript])
        return transcription
    except Exception as e:
        print(f"Error al obtener la transcripción con YouTubeTranscriptApi: {str(e)}")
        if "Subtitles are disabled for this video" in str(e):
            print("\nSubtítulos desactivados, iniciando flujo alternativo...")
        return None

def puntuar_texto_en_espanol(texto):
    try:
        texto = re.sub(r'\.(\s*)([a-záéíóúñ])', lambda x: x.group(1) + x.group(2).upper(), texto)
        texto = re.sub(r'\s+([.,!?])', r'\1', texto)
        if not texto.endswith('.'):
            texto += '.'
        texto = re.sub(r'\[.*?\]', '', texto).strip()
        texto = re.sub(r'((?:[^.?!]*[.?!]){5})', r'\1\n\n', texto)
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'([a-záéíóúñA-ZÁÉÍÓÚÑ])\s+([.,!?])', r'\1\2', texto)
        texto = re.sub(r'([.,!?])\s*([a-záéíóúñ])', r'\1 \2', texto)
        return texto
    except Exception as e:
        print(f"Error al puntuar el texto: {e}")
        return texto

def generar_resumen(texto):
    try:
        prompt = f"""Resume el siguiente texto en español manteniendo las ideas clave: {texto}"""
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
        generated_ids = qwen_model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
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
        print("\n=== Intentando el flujo nuevo con YouTubeTranscriptApi ===")
        analyzer = TextAnalyzer()
        
        transcription = obtener_transcripcion_youtube(video_url)
        if not transcription:
            print("No se pudo obtener la transcripción, iniciando flujo alternativo...")
            return flujo_alternativo(video_url)

        print("\nTranscripción obtenida correctamente.")

        print("\nPuntuando texto...")
        puntuado_texto = puntuar_texto_en_espanol(transcription)
        if not puntuado_texto:
            raise ValueError("No se pudo puntuar el texto correctamente.")
        print("\nTexto puntuado correctamente.")

        print("\nGenerando resumen...")
        resumen = generar_resumen(puntuado_texto)
        if not resumen:
            raise ValueError("No se pudo generar el resumen correctamente.")
        print("\nResumen generado correctamente.")

        print("\nAnalizando texto...")
        wordcount = limpiar_y_contar(transcription)
        detected_brands = analyzer.find_brands_in_transcription(transcription)
        total_palabras = sum(frecuencia for palabra, frecuencia in wordcount)
        print(f"Total de palabras analizadas: {total_palabras}")

        return {
            "transcription": transcription,
            "punctuated_text": puntuado_texto,
            "summary": resumen,
            "wordcount": wordcount,
            "brands": detected_brands,
            "total_palabras": total_palabras,
        }

    except Exception as e:
        print(f"\n❌ Error en el flujo nuevo: {str(e)}")
        print("Intentando con el flujo alternativo...")
        return flujo_alternativo(video_url)

def flujo_alternativo(video_url):
    try:
        print("\n=== Iniciando flujo alternativo con descarga de audio ===")
        analyzer = TextAnalyzer()
        downloaded_files = []
        
        download_path = download_audio_yt_dlp(video_url)
        if not download_path:
            raise ValueError("Error al descargar el audio.")

        wav_file = None
        original_file = None
        for file in os.listdir(download_path):
            file_path = os.path.join(download_path, file)
            if file.endswith(".wav"):
                wav_file = file_path
            elif file.endswith(".webm") or file.endswith(".m4a"):
                original_file = file_path
            if file_path:
                downloaded_files.append(file_path)

        if not wav_file:
            raise ValueError("No se encontró el archivo WAV.")

        print("\nTranscribiendo audio...")
        transcription = transcribir_audio(wav_file)
        if not transcription:
            raise ValueError("Error al transcribir el audio.")

        print("\nPuntuando texto...")
        puntuado_texto = puntuar_texto_en_espanol(transcription)
        if not puntuado_texto:
            raise ValueError("Error al puntuar el texto.")

        print("\nGenerando resumen...")
        resumen = generar_resumen(puntuado_texto)
        if not resumen:
            raise ValueError("Error al generar el resumen.")

        print("\nAnalizando texto...")
        wordcount = limpiar_y_contar(transcription)
        detected_brands = analyzer.find_brands_in_transcription(transcription)
        total_palabras = sum(frecuencia for palabra, frecuencia in wordcount)

        # Limpiar archivos después de procesar todo
        for file_path in downloaded_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Archivo eliminado: {file_path}")
            except Exception as e:
                print(f"Error al eliminar archivo {file_path}: {e}")

        return {
            "transcription": transcription,
            "punctuated_text": puntuado_texto,
            "summary": resumen,
            "wordcount": wordcount,
            "brands": detected_brands,
            "total_palabras": total_palabras,
        }

    except Exception as e:
        # Limpiar archivos en caso de error
        if 'downloaded_files' in locals():
            for file_path in downloaded_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as clean_error:
                    print(f"Error al limpiar archivo {file_path}: {clean_error}")
        
        print(f"\n❌ Error en el flujo alternativo: {str(e)}")
        return {"error": str(e)}