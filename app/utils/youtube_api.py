import os
import re
import requests
from dotenv import load_dotenv
from app.utils.audio_processing import procesar_video
from app.utils.wordcount_plot import generar_grafico_wordcount
from app.database.database_service import insert_video_wordcount  
from app.utils.sentiment_analysis import analyze_comments

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def fetch_channel_id_from_handle(channel_handle):
    """
    Obtiene el channelId de un canal de YouTube usando su handle.
    """
    try:
        # Llamada a la API de YouTube con el parámetro forHandle
        channel_api_url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={channel_handle}&key={API_KEY}"
        response = requests.get(channel_api_url)

        if response.status_code != 200:
            raise Exception(f"Error fetching channel data by handle: {response.text}")
            

        channel_data = response.json()
        if not channel_data.get("items"):
            raise Exception("No channel data found for the provided handle.")

        return channel_data["items"][0]["id"]
    except Exception as e:
        print("Error fetching channelId by handle:", e)
        return None

def fetch_channel_id_from_html(channel_url):
    """
    Obtiene el channelId de un canal de YouTube usando scraping del HTML.
    """
    try:
        response = requests.get(channel_url)
        if response.status_code != 200:
            raise Exception(f"Error fetching HTML content: {response.status_code}")
        html_content = response.text
        match = re.search(r'"channelId"\s*:\s*"([^"]+)"', html_content)
        if match:
            return match.group(1)
        raise Exception("channelId not found in HTML")
    except Exception as e:
        print("Error fetching channelId from HTML:", e)
        return None

def fetch_video_comments(video_id, max_comments=25):
    """
    Obtiene hasta `max_comments` comentarios de un video de YouTube usando la API.
    """
    try:
        comments = []
        next_page_token = None
        while len(comments) < max_comments:
            comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={API_KEY}&maxResults=50"
            if next_page_token:
                comments_url += f"&pageToken={next_page_token}"

            response = requests.get(comments_url)
            if response.status_code != 200:
                raise Exception(f"Error fetching comments: {response.text}")

            comments_data = response.json()
            for item in comments_data.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
                if len(comments) >= max_comments:
                    break

            next_page_token = comments_data.get("nextPageToken")
            if not next_page_token:
                break  # No hay más páginas de comentarios

        return comments[:max_comments]
    except Exception as e:
        print(f"Error fetching comments for video {video_id}:", e)
        return []


def fetch_channel_videos(channel_url):
    """
    Obtiene los últimos 10 videos de un canal y procesa el más reciente.
    """
    try:
        # Priorizar obtención del channelId usando el handle
        print(f"Fetching channelId for URL: {channel_url}")
        channel_handle = channel_url.split("/")[-1]
        channel_id = fetch_channel_id_from_handle(channel_handle)

        # Si falla, intentar obtener el channelId desde el HTML
        if not channel_id:
            channel_id = fetch_channel_id_from_html(channel_url)

        if not channel_id:
            raise Exception("Could not extract channelId using handle or HTML.")

        print(f"Channel ID: {channel_id}")

        # Obtener datos del canal
        channel_api_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails&id={channel_id}&key={API_KEY}"
        response = requests.get(channel_api_url)
        if response.status_code != 200:
            raise Exception(f"Error fetching channel data: {response.text}")
        channel_data = response.json()
        if not channel_data.get("items"):
            raise Exception("No channel data found for the provided channelId")
        uploads_playlist_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # Obtener los últimos 10 videos
        videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId={uploads_playlist_id}&maxResults=10&key={API_KEY}"
        videos_response = requests.get(videos_url)
        if videos_response.status_code != 200:
            raise Exception(f"Error fetching videos data: {videos_response.text}")
        videos_data = videos_response.json()
        videos = []

        # Procesar cada video
        for item in videos_data.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            video_title = item["snippet"]["title"]
            published_date = item["snippet"].get("publishedAt", "Unknown")
            video_metrics_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}"
            video_metrics_response = requests.get(video_metrics_url)

            video_data = {
                "title": video_title,
                "videoId": video_id,
                "published_date": published_date,
                "views": 0,
                "likes": 0,
                "comments_count": 0,
                "comments": [], 
                "average_stars": None,
            }

            if video_metrics_response.status_code == 200:
                video_metrics = video_metrics_response.json().get("items", [{}])[0].get("statistics", {})
                video_data.update({
                    "views": int(video_metrics.get("viewCount", 0)),
                    "likes": int(video_metrics.get("likeCount", 0)),
                    "comments_count": int(video_metrics.get("commentCount", 0)),
                })

            # Recoger comentarios
            raw_comments = fetch_video_comments(video_id, max_comments=25)
            analyzed_comments = analyze_comments(raw_comments)  # Añadir análisis de sentimiento

            # Calcular la media de estrellas
            if analyzed_comments:
                video_data["average_stars"] = round(
                    sum(comment["stars"] for comment in analyzed_comments) / len(analyzed_comments), 2
                )

            # Agregar comentarios analizados
            video_data["comments"] = analyzed_comments

            # Agregar a la lista de videos
            videos.append(video_data)

        # Procesar el último video
        if videos:
            latest_video = videos[0]
            video_url = f"https://www.youtube.com/watch?v={latest_video['videoId']}"
            print(f"Processing latest video: {video_url}")
            processed_data = procesar_video(video_url)

            if processed_data:
                latest_video["summary"] = processed_data.get("summary", "Resumen no disponible.")
                latest_video["wordcount"] = processed_data.get("wordcount", [])
                latest_video["total_palabras"] = processed_data.get("total_palabras", 0)

                # Guardar wordcount en la base de datos
                insert_video_wordcount(
                    video_id=latest_video["videoId"],
                    channel_id=channel_id,  # Agregar el channel_id aquí
                    channel_name=channel_data["items"][0]["snippet"]["title"],
                    video_title=latest_video["title"],
                    wordcount=latest_video["wordcount"],
                    total_palabras=latest_video["total_palabras"],
                )

                # Generar gráfico de barras para el wordcount
                if latest_video["wordcount"]:
                    grafico_path = generar_grafico_wordcount(
                        latest_video["wordcount"], 
                        output_path=f"static/wordcount_{latest_video['videoId']}.png"
                    )
                    latest_video["wordcount_chart"] = grafico_path  # Añadir la ruta del gráfico al video

        return {
            "channel_title": channel_data["items"][0]["snippet"]["title"],
            "description": channel_data["items"][0]["snippet"]["description"],
            "videos": videos
        }
    except Exception as e:
        print("Error in fetch_channel_videos:", e)
        return None
