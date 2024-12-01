import os
import yt_dlp
import speech_recognition as sr
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
from app.utils.text_analysis import limpiar_y_contar, find_brands_in_transcription

# Configuración del modelo Qwen para resúmenes
SMALL_CHAT_MODEL_CON_CASTELLANO = "Qwen/Qwen1.5-1.8B-Chat"
DEVICE = "cpu"

# Configuración del modelo BART para puntuación
PUNCT_MODEL_NAME = "facebook/bart-large-cnn"

# Inicializar modelos
qwen_model = AutoModelForCausalLM.from_pretrained(SMALL_CHAT_MODEL_CON_CASTELLANO).to(DEVICE)
qwen_tokenizer = AutoTokenizer.from_pretrained(SMALL_CHAT_MODEL_CON_CASTELLANO)

punct_model = AutoModelForSeq2SeqLM.from_pretrained(PUNCT_MODEL_NAME)
punct_tokenizer = AutoTokenizer.from_pretrained(PUNCT_MODEL_NAME)

# Lista de palabras en inglés a filtrar
stopwords_ingles = set([
    "the", "is", "and", "of", "in", "on", "for", "to", "this", "that", "with", "it", "as", "at", "by", "from", "be",
    "an", "has", "have", "but", "or", "not", "you", "me", "he", "she", "we", "they", "us", "their", "my", "your",
    "its", "more", "so", "can", "will", "should", "if", "about", "like", "just", "because", "into", "over", "before",
    "after", "then"
])

def filtrar_ingles(texto):
    """
    Filtra palabras en inglés del texto.
    """
    palabras = texto.split()
    return " ".join([palabra for palabra in palabras if palabra.lower() not in stopwords_ingles])

def normalizar_puntuacion(texto):
    """
    Normaliza puntuación asegurando capitalización tras puntos.
    """
    oraciones = texto.split(". ")
    oraciones = [oracion.capitalize() for oracion in oraciones]
    return ". ".join(oraciones)

def puntuar_texto_en_espanol(texto, max_length=1024):
    """
    Función híbrida que combina BART con reglas básicas para puntuar texto en español.
    """
    if not texto:
        raise ValueError("El texto para puntuación está vacío.")
    
    try:
        print("\n=== INICIANDO PUNTUACIÓN DEL TEXTO ===")
        print(f"Longitud del texto original: {len(texto)} caracteres")

        # Paso 1: División en fragmentos manejables
        palabras = texto.split()
        fragmentos = []
        fragmento_actual = []
        longitud_actual = 0
        
        for palabra in palabras:
            if longitud_actual + len(palabra) + 1 <= (max_length - 200):  # Margen de seguridad
                fragmento_actual.append(palabra)
                longitud_actual += len(palabra) + 1
            else:
                fragmentos.append(" ".join(fragmento_actual))
                fragmento_actual = [palabra]
                longitud_actual = len(palabra) + 1
        
        if fragmento_actual:
            fragmentos.append(" ".join(fragmento_actual))

        print(f"Texto dividido en {len(fragmentos)} fragmentos")
        texto_final = ""

        # Paso 2: Procesar cada fragmento
        for i, fragmento in enumerate(fragmentos, 1):
            print(f"\n--- Procesando fragmento {i}/{len(fragmentos)} ---")
            print(f"Longitud del fragmento: {len(fragmento)} caracteres")

            # Intentar primero con BART
            try:
                prompt = f"Añade signos de puntuación a este texto en español:\n\n{fragmento}"
                inputs = punct_tokenizer(prompt, return_tensors="pt", max_length=max_length, truncation=True)
                
                with torch.no_grad():
                    outputs = punct_model.generate(
                        inputs["input_ids"],
                        max_length=max_length,
                        num_beams=4,
                        length_penalty=1.0,
                        early_stopping=True,
                        do_sample=False
                    )
                
                texto_bart = punct_tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Limpiar resultado de BART
                texto_bart = texto_bart.split(":")[-1].strip()
                
                # Verificar que BART no perdió contenido significativo
                palabras_originales = set(fragmento.lower().split())
                palabras_bart = set(texto_bart.lower().split())
                
                if len(palabras_bart) >= len(palabras_originales) * 0.9:
                    print("✓ Usando salida de BART")
                    texto_procesado = texto_bart
                else:
                    print("⚠️ BART perdió contenido, aplicando reglas básicas")
                    texto_procesado = aplicar_reglas_basicas(fragmento)
            except Exception as e:
                print(f"⚠️ Error con BART: {e}")
                texto_procesado = aplicar_reglas_basicas(fragmento)

            # Paso 3: Aplicar reglas básicas adicionales al resultado
            texto_procesado = mejorar_puntuacion(texto_procesado)
            texto_final += texto_procesado + " "

        # Paso 4: Limpieza y formato final
        texto_final = texto_final.strip()
        texto_final = re.sub(r'\s+', ' ', texto_final)
        texto_final = re.sub(r'\s+([.,!?])', r'\1', texto_final)
        texto_final = texto_final[0].upper() + texto_final[1:]

        print("\n=== RESULTADO DE LA PUNTUACIÓN ===")
        print(f"Longitud original: {len(texto)} caracteres")
        print(f"Longitud final: {len(texto_final)} caracteres")
        
        return texto_final

    except Exception as e:
        print(f"\n❌ Error durante la puntuación: {str(e)}")
        print("Detalles del error:")
        import traceback
        print(traceback.format_exc())
        return texto

def aplicar_reglas_basicas(texto):
    """
    Aplica reglas básicas de puntuación.
    """
    # Normalizar espacios
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    # Reglas básicas de puntuación
    texto = re.sub(r'([a-zñáéíóú])\s+(pero|porque|entonces|así que|por eso)', r'\1. \2', texto)
    texto = re.sub(r'([a-zñáéíóú])\s+([A-ZÁÉÍÓÚÑ])', r'\1. \2', texto)
    
    return texto

def mejorar_puntuacion(texto):
    """
    Aplica mejoras adicionales a la puntuación.
    """
    # Proteger nombres compuestos y términos especiales
    texto = re.sub(r'([A-Z][a-z]+)\s*\.\s*([A-Z][a-z]+)', r'\1 \2', texto)
    
    # Mejorar comas en enumeraciones
    texto = re.sub(r'(\w+)(\s+y\s+|\s+e\s+|\s+o\s+)(\w+)(?=\s+\w+)', r'\1, \2\3', texto)
    
    # Asegurar espacio después de puntuación
    texto = re.sub(r'([.,!?])([A-ZÁÉÍÓÚÑa-záéíóúñ])', r'\1 \2', texto)
    
    # Eliminar puntuación duplicada
    texto = re.sub(r'\.+', '.', texto)
    texto = re.sub(r',+', ',', texto)
    
    # Asegurar que las oraciones terminen en punto
    if not texto.endswith(('.', '!', '?')):
        texto += '.'
    
    return texto

def generar_resumen_en_espanol(texto: str) -> str:
    """
    Genera un resumen profesional y conciso del texto, independiente del contexto.
    """
    if not texto:
        print("❌ Error: El texto para resumir está vacío.")
        raise ValueError("El texto para resumir está vacío.")
    
    try:
        print("\n--- Iniciando generación del resumen ---")
        
        prompt = (
            "A partir del siguiente texto, genera un resumen breve y profesional manteniendo la coherencia con el contenido del texto"
            "de máximo 5 oraciones:\n\n"
            f"{texto}\n\n"
            "Resumen:"
        )
        
        inputs = qwen_tokenizer(prompt, return_tensors="pt").to(qwen_model.device)
        
        outputs = qwen_model.generate(
            **inputs,
            max_new_tokens=150,      # Reducido para forzar resúmenes más concisos
            num_beams=4,
            length_penalty=0.8,      # Penalizar longitud para favorecer concisión
            early_stopping=True,
            do_sample=True,
            temperature=0.3,         # Reducida para más consistencia
            top_p=0.95,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3   # Evitar repetición de frases
        )
        
        respuesta_texto = qwen_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo el resumen (después de "Resumen:")
        resumen = respuesta_texto.split("Resumen:")[-1].strip()
        
        # Limpieza y formateo
        resumen = re.sub(r'\s+', ' ', resumen)
        resumen = re.sub(r'\s+([.,])', r'\1', resumen)
        resumen = re.sub(r'([.!?])\s*([a-zñáéíóú])', 
                        lambda m: f"{m.group(1)} {m.group(2).upper()}", 
                        resumen)
        
        # Si el resumen es demasiado largo, intentar acortarlo
        if len(resumen.split()) > 60:  # Aproximadamente 3 oraciones
            oraciones = re.split(r'[.!?]+', resumen)
            resumen = '. '.join(oraciones[:3]) + '.'
        
        # Verificación de calidad
        if len(resumen.split()) < 3 or len(resumen) < 20:
            print("⚠️ Resumen demasiado corto, reintentando...")
            return generar_resumen_en_espanol(texto)
        
        print(f"\nResumen generado ({len(resumen)} caracteres)")
        return resumen

    except Exception as e:
        print(f"\n❌ Error en la generación del resumen: {e}")
        print("Detalles del error:")
        import traceback
        print(traceback.format_exc())
        return ""


def download_audio_yt_dlp(video_url, output_path="downloads"):
    """
    Descarga el audio de un video de YouTube usando yt-dlp.
    """
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        print(f"Audio descargado en {output_path}")
        return output_path

    except Exception as e:
        print(f"Error al descargar el audio con yt-dlp: {e}")
        return None

def transcribir_audio(audio_file_path, chunk_duration=60):
    """
    Transcribe un archivo de audio dividiéndolo en fragmentos usando Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    transcription = ""

    try:
        print(f"\nIniciando transcripción del archivo: {audio_file_path}")
        
        with sr.AudioFile(audio_file_path) as source:
            # Obtener la duración total del audio
            total_duration = source.DURATION
            num_chunks = int(total_duration // chunk_duration + (1 if total_duration % chunk_duration > 0 else 0))
            print(f"Duración total del audio: {total_duration:.2f} segundos")
            print(f"Dividiendo en {num_chunks} fragmentos de {chunk_duration} segundos")

            # Ajustar el nivel de ruido ambiental
            print("Ajustando nivel de ruido ambiental...")
            recognizer.adjust_for_ambient_noise(source)

            # Leer todo el audio de una vez
            print("Leyendo el archivo de audio completo...")
            audio_data = recognizer.record(source)
            total_frames = len(audio_data.frame_data)
            frames_per_chunk = int(chunk_duration * source.SAMPLE_RATE * source.SAMPLE_WIDTH)

            for i in range(num_chunks):
                try:
                    print(f"\nProcesando fragmento {i + 1}/{num_chunks}")
                    
                    # Calcular los índices de inicio y fin para este fragmento
                    start_frame = i * frames_per_chunk
                    end_frame = min(start_frame + frames_per_chunk, total_frames)
                    
                    # Crear un nuevo AudioData para este fragmento
                    chunk_data = sr.AudioData(
                        audio_data.frame_data[start_frame:end_frame],
                        audio_data.sample_rate,
                        audio_data.sample_width
                    )

                    # Transcribir el fragmento
                    print(f"Transcribiendo fragmento {i + 1}...")
                    chunk_transcription = recognizer.recognize_google(chunk_data, language='es-ES')
                    print(f"Fragmento {i + 1} transcrito: {chunk_transcription[:50]}...")
                    
                    transcription += chunk_transcription + " "
                    
                except sr.UnknownValueError:
                    print(f"⚠️ No se pudo entender el audio en el fragmento {i + 1}/{num_chunks}")
                except sr.RequestError as e:
                    print(f"❌ Error en el servicio de Google Speech para el fragmento {i + 1}: {e}")
                    if transcription.strip():  # Si ya tenemos algo transcrito, continuamos
                        print("Continuando con el siguiente fragmento...")
                        continue
                    return ""
                except Exception as e:
                    print(f"❌ Error inesperado en el fragmento {i + 1}: {e}")
                    if transcription.strip():  # Si ya tenemos algo transcrito, continuamos
                        print("Continuando con el siguiente fragmento...")
                        continue

        transcription = transcription.strip()
        print("\n=== TRANSCRIPCIÓN COMPLETADA ===")
        print(f"Longitud total de la transcripción: {len(transcription)} caracteres")
        return transcription

    except FileNotFoundError:
        print(f"❌ Archivo de audio no encontrado: {audio_file_path}")
        return ""
    except Exception as e:
        print(f"❌ Error durante la transcripción: {e}")
        import traceback
        print(traceback.format_exc())
        return ""

def borrar_archivo(audio_file):
    """
    Elimina un archivo de audio.
    """
    try:
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"Archivo eliminado: {audio_file}")
        else:
            print("El archivo no existe.")
    except Exception as e:
        print(f"Error al eliminar el archivo: {e}")

def procesar_video(video_url):
    """
    Procesa un video de YouTube: descarga el audio, transcribe, puntúa, resume y analiza.
    Con logs detallados para debugging.
    """
    try:
        print("\n=== INICIANDO PROCESAMIENTO DEL VIDEO ===")
        
        # Descargar el audio
        print("\n1. Descargando audio...")
        download_path = download_audio_yt_dlp(video_url)
        if not download_path:
            print("❌ Error: No se pudo descargar el audio")
            return {"error": "Error al descargar el audio."}
        print("✅ Audio descargado correctamente")

        # Encuentra el archivo descargado
        print("\n2. Buscando archivo de audio...")
        audio_file = next((os.path.join(download_path, file) for file in os.listdir(download_path) if file.endswith(".wav")), None)
        if not audio_file:
            print("❌ Error: No se encontró el archivo WAV")
            return {"error": "No se encontró el archivo de audio descargado."}
        print(f"✅ Archivo de audio encontrado: {audio_file}")

        # Transcribir el audio
        print("\n3. Transcribiendo audio...")
        transcription = transcribir_audio(audio_file)
        if not transcription:
            print("❌ Error: No se pudo transcribir el audio")
            return {"error": "Error al transcribir el audio."}
        print("\n=== TRANSCRIPCIÓN COMPLETA ===")
        print(transcription)
        print("✅ Audio transcrito correctamente")

        # Puntuación del texto transcrito
        print("\n4. Puntuando texto...")
        puntuado_texto = puntuar_texto_en_espanol(transcription)
        if not puntuado_texto:
            print("❌ Error: No se pudo puntuar el texto")
            return {"error": "Error al puntuar el texto."}
        print("\n=== TEXTO PUNTUADO ===")
        print(puntuado_texto)
        print("✅ Texto puntuado correctamente")

        # Eliminar el archivo de audio descargado
        print("\n5. Eliminando archivo de audio temporal...")
        borrar_archivo(audio_file)
        print("✅ Archivo de audio eliminado")

        # Generar resumen
        print("\n6. Generando resumen...")
        resumen = generar_resumen_en_espanol(puntuado_texto)
        if not resumen:
            print("❌ Error: No se pudo generar el resumen")
            return {"error": "Error al generar el resumen."}
        print("\n=== RESUMEN GENERADO ===")
        print(resumen)
        print("✅ Resumen generado correctamente")

        # Contar palabras y detectar marcas
        print("\n7. Analizando texto...")
        wordcount = limpiar_y_contar(transcription)
        if not wordcount:
            print("❌ Error: No se pudo realizar el análisis de frecuencia de palabras")
            return {"error": "Error al realizar el wordcount."}
        
        detected_brands = find_brands_in_transcription(transcription)
        print("✅ Análisis de texto completado")
        print("\n=== ESTADÍSTICAS ===")
        
        # Calcular total de palabras sumando las frecuencias
        total_palabras = sum(frecuencia for palabra, frecuencia in wordcount)
        print(f"Total de palabras analizadas: {total_palabras}")
        
        print("\nPalabras más frecuentes:")
        for palabra, frecuencia in wordcount:
            print(f"- {palabra}: {frecuencia} veces")
        
        print(f"\nMarcas detectadas: {', '.join(detected_brands) if detected_brands else 'Ninguna'}")

        print("\n=== PROCESAMIENTO COMPLETADO CON ÉXITO ===")

        return {
            "transcription": transcription,
            "punctuated_text": puntuado_texto,
            "summary": resumen,
            "wordcount": wordcount,
            "brands": detected_brands,
            "total_palabras": total_palabras,
        }

    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {str(e)}")
        print("Detalles del error:")
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}