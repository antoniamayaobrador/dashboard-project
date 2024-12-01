from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.youtube_api import fetch_channel_videos
from app.utils.search_llm import router as search_router
from app.database.database_service import (
    get_wordcount_summary,
    get_historical_wordcount_by_channel,
    save_feedback
)

# Crear el enrutador principal
router = APIRouter()

# Modelo Pydantic para validar la solicitud de análisis
class AnalyzeRequest(BaseModel):
    url: str

class WordcountData(BaseModel):
    channel_name: str
    video_title: str
    video_id: str
    wordcount: list


class FeedbackData(BaseModel):
    type: str
    result: bool
    content: str 

@router.post("/api/analyze")
async def analyze_channel(request: AnalyzeRequest):
    """
    Endpoint para analizar un canal de YouTube.
    """
    try:
        # Obtener datos del canal y procesar el último video
        channel_data = fetch_channel_videos(request.url)

        if not channel_data:
            raise HTTPException(status_code=400, detail="No se pudieron obtener los datos del canal")

        # Obtener histórico del canal específico
        historical_wordcount = get_historical_wordcount_by_channel(channel_data["channel_title"])

        # Generar ruta al gráfico si existe
        chart_path = None
        if "wordcount_chart" in channel_data:
            chart_path = f"/static/{channel_data['wordcount_chart']}"

        # Obtener el resumen general de palabras
        general_summary = get_wordcount_summary()

        return {
            "channel_title": channel_data["channel_title"],
            "description": channel_data["description"],
            "videos": channel_data["videos"],
            "wordcount_chart": chart_path,
            "historical_wordcount": historical_wordcount,
            "general_wordcount_summary": general_summary
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/api/save-wordcount")
async def save_wordcount(data: WordcountData):
    """
    Endpoint para guardar el conteo de palabras de un video.
    """
    try:
        insert_wordcount(
            channel_name=data.channel_name,
            video_title=data.video_title,
            video_id=data.video_id,
            wordcount_list=data.wordcount
        )
        return {"message": "Datos de wordcount guardados exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar wordcount: {str(e)}")

@router.get("/api/wordcount-summary")
async def wordcount_summary():
    """
    Endpoint para obtener el resumen general de palabras.
    """
    try:
        summary = get_wordcount_summary()
        return {"wordcount_summary": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener el resumen de wordcount: {str(e)}"
        )

@router.get("/api/historical-wordcount/{channel_name}")
async def historical_wordcount(channel_name: str):
    """
    Endpoint para obtener el histórico de palabras de un canal específico.
    """
    try:
        print(f"Received channel_name: {channel_name}")  # Log del canal recibido
        wordcount = get_historical_wordcount_by_channel(channel_name)
        print(f"Wordcount fetched: {wordcount}")  # Log del resultado
        return {"historical_wordcount": wordcount}
    except Exception as e:
        print(f"Error in API endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener el histórico del canal: {str(e)}"
        )

@router.post("/api/feedback")
async def save_user_feedback(feedback: FeedbackData):
    """
    Endpoint para guardar la retroalimentación del usuario.
    """
    try:
        save_feedback(feedback.type, feedback.result, feedback.content)
        return {"message": "Feedback guardado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el feedback: {str(e)}")

# Incluir las rutas del search_llm
router.include_router(search_router, prefix="")