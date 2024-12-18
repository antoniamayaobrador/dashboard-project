Proyecto: Dashboard de Análisis de Videos y Feedback


Descripción del Proyecto

Este proyecto es un dashboard interactivo que permite analizar videos de un canal, generar resúmenes, detectar marcas mencionadas y realizar análisis de conteo de palabras. Incluye un sistema de feedback donde los usuarios pueden calificar la utilidad de los resúmenes y definiciones generadas. Está planteado desde la idea una agencia hipotética de influencer marketing que necesita analizar diferentes influencers del ámbito de la perfumería. 

Características Principales

Análisis de videos con generación de resúmenes automáticos.
Detección de marcas mencionadas en los títulos de los videos.
Visualización de estadísticas de conteo de palabras.
Sistema de feedback para calificar resúmenes y definiciones.
Interfaz gráfica moderna y responsiva.


Tecnologías Utilizadas

Frontend:
React: Framework para la creación de la interfaz de usuario.
Chart.js: Biblioteca para gráficos de conteo de palabras.
Axios: Para la comunicación con el backend a través de API REST.

Backend:
FastAPI: Framework para construir la API.
PostgreSQL: Base de datos para almacenar información como feedback de usuarios.
Python: Lenguaje para el backend.

Otros:
Docker (opcional): Para la contenedorización de la aplicación.
Git: Control de versiones.


Instalación y Configuración

Requisitos previos
Node.js (v16 o superior)
Python (v3.8 o superior)
PostgreSQL

Opcional: Docker para ejecución en contenedores


Configuración Backend

Clona este repositorio:

git clone https://github.com/usuario/proyecto-dashboard.git

cd proyecto-dashboard/backend
Instala las dependencias de Python:
pip install -r requirements.txt
Configura las variables de entorno:
Crea un archivo .env con las siguientes variables:
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/youtube_analysis

Inicia el servidor backend:
uvicorn app.main:app --reload

Configuración Frontend
Ve al directorio del frontend:
cd proyecto-TFB/frontend

Instala las dependencias:
npm install

Inicia el servidor de desarrollo:
npm start

El dashboard estará disponible en http://localhost:3000.

Uso
Accede al dashboard desde tu navegador en http://localhost:3000.
Carga el análisis de un canal de video.
Explora las estadísticas y proporciona feedback sobre los resúmenes y definiciones.


API Endpoints:
Feedback
POST /api/feedback
Descripción: Guarda feedback de los usuarios sobre resúmenes y definiciones.
Body esperado:
{
  "type": "definition",
  "result": true,
  "content": "Texto del resumen o definición"
}
Respuesta exitosa:
{ "message": "Feedback guardado exitosamente." }
Ejemplo de Configuración con Docker (opcional)


Construye la imagen:

docker-compose build


Inicia los servicios:

docker-compose up


Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para nuevas ideas o mejoras.

Autor
Creado por Antoni Amaya Obrador. 
2024. 

