import React, { useEffect, useRef, useState } from "react";
import { Chart } from "chart.js/auto";
import axios from "axios";

const PERFUME_BRANDS = [
    // Marcas comerciales populares
    "Tom Ford", "Dior", "Chanel", "Gucci", "Yves Saint Laurent", "Versace", "Hermès", 
    "Prada", "Dolce & Gabbana", "Givenchy", "Burberry", "Armani", "Hugo Boss", "Calvin Klein",
    "Lacoste", "Marc Jacobs", "Ralph Lauren", "Paco Rabanne", "Carolina Herrera", 
    "Jean Paul Gaultier", "Valentino", "Balenciaga", "Bulgari", "Fendi", "Lancome", 
    "Victoria's Secret", "Zara", "Mercadona", "Amouage", "Creed", "Maison Francis Kurkdjian", 
    "Byredo", "Le Labo", "Diptyque", "Frederic Malle", "Jo Malone", "Penhaligon's", "Aesop", 
    "Xerjoff", "Clive Christian", "Parfums de Marly", "Roja Parfums", "Mancera", "Montale", 
    "Initio", "Tiziana Terenzi", "Nishane", "Serge Lutens", "Comme des Garçons", 
    "Etat Libre d'Orange", "Zoologist", "Acqua di Parma", "BDK Parfums", "Carner Barcelona", 
    "Memo Paris", "Floris London", "Bond No.9", "Vilhelm Parfumerie", "Histoires de Parfums", 
    "Masque Milano", "The Different Company", "Atelier Cologne", "Maison Margiela", 
    "Ormonde Jayne", "House of Oud", "Olfactive Studio", "The Harmonist", "Viktor & Rolf",
    "Kilian", "Nasomatto", "Profumum Roma", "Nicolai", "Fueguia 1833", "Eight & Bob",
    "Juliette Has a Gun", "Miller Harris", "L'Artisan Parfumeur", "Frapin",
    "Arquiste", "Escentric Molecules", "Heeley", "Floraiku", "Keiko Mecheri",
    "Laboratorio Olfattivo", "Lubin", "M.Micallef", "Majda Bekkali", "Moresque",
    "Neela Vermeire", "Ormonde Jayne", "Parfums MDCI", "Perris Monte Carlo", "Projet Alternative",
    "Robert Piguet", "Rothschild", "SHL 777", "Six Scents", "Stephane Humbert Lucas",
    "The House of Oud", "The Merchant of Venice", "Von Eusersdorff", "Widian", "Xerjoff",
    "Abel", "Acca Kappa", "Acqua dell'Elba", "Aedes de Venustas", "Affinessence",
    "Alyson Oldoini", "Angela Ciampagna", "Annick Goutal", "Antonio Alessandria", "April Aromatics",
    "Areej Le Doré", "Armaf", "Atelier des Ors", "Berdoues", "Bois 1920", "Croxatto"
];

const Dashboard = ({ data }) => {
    if (!data) {
        return (
            <div
                style={{
                    padding: "4rem",
                    margin: "3rem",
                    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                    borderRadius: "8px",
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                    textAlign: "center",
                    fontFamily: "Roboto, sans-serif",
                }}
            >
                <p
                    style={{
                        fontSize: "1.2rem",
                        color: "#333",
                        margin: "1rem 0",
                    }}
                >
                    No hay datos para mostrar. Por favor, analiza un canal primero. El análisis puede tardar varios minutos. 
                </p>
            </div>
        );
    }

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: true, // Maintains a fixed aspect ratio
        plugins: {
            legend: {
                display: true,
                position: "top",
            },
        },
        scales: {
            x: {
                ticks: {
                    autoSkip: true,
                    maxRotation: 45,
                    minRotation: 0,
                },
            },
            y: {
                beginAtZero: true,
            },
        },
    };
    
    const { channel_title, description, videos = [] } = data;
    const latestVideo = videos[0];

    const chartRef = useRef(null);
    const [searchTerm, setSearchTerm] = useState("");
    const [definition, setDefinition] = useState("");
    const [summary, setSummary] = useState(""); // Estado del resumen
    const [isSearching, setIsSearching] = useState(false);
    const [sortedVideos, setSortedVideos] = useState(videos);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: "asc" });
    const [showDefinitionFeedback, setShowDefinitionFeedback] = useState(false);
    const [showSummaryFeedback, setShowSummaryFeedback] = useState(false);
    const [historicalWordCount, setHistoricalWordCount] = useState([]);
    const [queryInput, setQueryInput] = useState(""); // Estado para almacenar el texto ingresado por el usuario
    const [queryResult, setQueryResult] = useState(""); // Estado para almacenar el resultado de la consulta
    const [isQuerying, setIsQuerying] = useState(false); // Estado para manejar el estado de carga de la consulta
    const [showQueryFeedback, setShowQueryFeedback] = useState(false);


    
    


    // Fetch historical word count
    useEffect(() => {
        async function fetchHistoricalWordCount() {
            try {
                const response = await axios.get(`http://127.0.0.1:8000/api/historical-wordcount/${channel_title}`);
                console.log("API Response:", response.data.historical_wordcount); // Log para verificar datos
                setHistoricalWordCount(response.data.historical_wordcount || []);
            } catch (error) {
                console.error("Error fetching historical word count:", error);
            }
        }
    
        if (channel_title) {
            fetchHistoricalWordCount();
        }
    }, [channel_title]);
    
      useEffect(() => {
          if (latestVideo?.summary) {
              setSummary(latestVideo.summary);
          } else {
              setSummary(""); 
          }
      }, [latestVideo]);
    

    const highlightBrands = (title) => {
        let result = title;
        PERFUME_BRANDS.forEach(brand => {
            const regex = new RegExp(brand, 'gi');
            result = result.replace(regex, `<strong>${brand}</strong>`);
        });
        return <span dangerouslySetInnerHTML={{ __html: result }} />;
    };

    const handleSearch = async () => {
        if (!searchTerm.trim()) {
            setDefinition("Por favor, ingresa un término para buscar.");
            return;
        }

        setIsSearching(true);
        setDefinition("La búsqueda puede tardar varios minutos. Los resultados han sido generados utilizando inteligencia artificial. No utilice las definiciones con fines médicos, legales o técnicos.");

        try {
            const response = await axios.post("http://localhost:8000/api/define", { 
                term: searchTerm 
            });
            setDefinition(response.data.definition || "No se encontró una definición.");
        } catch (error) {
            console.error("Error buscando definición:", error);
            if (error.response) {
                console.log("Respuesta del servidor:", error.response.data);
            }
            setDefinition("Ocurrió un error al buscar la definición.");
        } finally {
            setIsSearching(false);
        }
    };

    const handleSort = (key) => {
        let direction = "asc";
        if (sortConfig.key === key && sortConfig.direction === "asc") {
            direction = "desc";
        }
        setSortConfig({ key, direction });

        const sorted = [...videos].sort((a, b) => {
            if (a[key] < b[key]) return direction === "asc" ? -1 : 1;
            if (a[key] > b[key]) return direction === "asc" ? 1 : -1;
            return 0;
        });

        setSortedVideos(sorted);
    };

    const handleDefinitionFeedback = async (result) => {
        if (!definition) {
            console.error("No hay definición disponible para enviar.");
            return;
        }
    
        try {
            await axios.post("http://127.0.0.1:8000/api/feedback", {
                type: "definition",
                result,
                content: definition,
            });
            console.log("Feedback de definición guardado exitosamente.");
            setShowDefinitionFeedback(true); // Activa el mensaje
            setTimeout(() => setShowDefinitionFeedback(false), 3000); // Oculta después de 3 segundos
        } catch (error) {
            console.error("Error guardando el feedback de definición:", error);
        }
    };
    
    const handleSummaryFeedback = async (result) => {
        if (!summary) {
            console.error("No hay resumen disponible para enviar.");
            return;
        }
    
        try {
            await axios.post("http://127.0.0.1:8000/api/feedback", {
                type: "summary",
                result,
                content: summary,
            });
            console.log("Feedback de resumen guardado exitosamente.");
            setShowSummaryFeedback(true); // Activa el mensaje
            setTimeout(() => setShowSummaryFeedback(false), 3000); // Oculta después de 3 segundos
        } catch (error) {
            console.error("Error guardando el feedback de resumen:", error);
        }
    };
    
    const handleQuery = async () => {
        if (!queryInput.trim()) {
            setQueryResult("Por favor, escribe una consulta en lenguaje natural.");
            return;
        }
    
        setIsQuerying(true); // Cambia a estado de carga
        setQueryResult("Procesando la consulta, por favor espera...");
    
        try {
            const response = await axios.post("http://localhost:8000/api/query", {
                question: queryInput,
            });
    
            if (response.data && response.data.results) {
                setQueryResult(JSON.stringify(response.data.results, null, 2)); // Formatea los resultados como JSON legible
            } else {
                setQueryResult("No se encontraron resultados para la consulta.");
            }
        } catch (error) {
            console.error("Error realizando la consulta:", error);
            setQueryResult("Ocurrió un error al procesar la consulta.");
        } finally {
            setIsQuerying(false); // Finaliza el estado de carga
        }
    };

    const handleQueryFeedback = async (result) => {
        if (!queryResult) {
            console.error("No hay resultado de consulta disponible para enviar.");
            return;
        }
    
        const feedbackData = {
            type: "query", // Debe ser un string
            result: Boolean(result), // Debe ser un booleano (true o false)
            content: queryResult, // Debe ser un string
            prompt: null // Asegúrate de enviar el campo prompt como null si no es necesario
        };
    
        console.log("Enviando feedback:", feedbackData);
    
        try {
            await axios.post("http://127.0.0.1:8000/api/feedback", feedbackData);
            setShowQueryFeedback(true);
            setTimeout(() => setShowQueryFeedback(false), 3000);
        } catch (error) {
            console.error("Error guardando el feedback de consulta:", error);
            if (error.response) {
                console.log("Error response data:", error.response.data);
            }
        }
    };
    
    const calculateStats = (videos) => {
        if (!videos || videos.length === 0) return null;
    
        // Funciones auxiliares
        const average = arr => arr.reduce((a, b) => a + b, 0) / arr.length;
        const calculateGrowthRate = arr => {
            const last = arr[0];
            const first = arr[arr.length - 1];
            return ((last - first) / first) * 100;
        };
        const median = arr => {
            const sorted = [...arr].sort((a, b) => a - b);
            const mid = Math.floor(sorted.length / 2);
            return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
        };
        const stdDev = arr => {
            const mean = average(arr);
            const squareDiffs = arr.map(value => Math.pow(value - mean, 2));
            return Math.sqrt(average(squareDiffs));
        };
    
        // Datos para cálculos
        const viewsData = videos.map(v => v.views);
        const likesData = videos.map(v => v.likes);
        const commentsData = videos.map(v => v.comments_count);
        const averageStarsData = videos.map(v => v.average_stars).filter(val => val !== null);
    
        const baseStats = {
            views: {
                min: Math.min(...viewsData),
                max: Math.max(...viewsData),
                mean: average(viewsData),
                median: median(viewsData),
                stdDev: stdDev(viewsData)
            },
            likes: {
                min: Math.min(...likesData),
                max: Math.max(...likesData),
                mean: average(likesData),
                median: median(likesData),
                stdDev: stdDev(likesData)
            },
            comments: {
                min: Math.min(...commentsData),
                max: Math.max(...commentsData),
                mean: average(commentsData),
                median: median(commentsData),
                stdDev: stdDev(commentsData)
            }
        };
    
        return {
            baseStats,
            engagement: (average(likesData) + average(commentsData)) / average(viewsData) * 100,
            viewsGrowth: calculateGrowthRate(viewsData),
            likesPerView: average(likesData) / average(viewsData) * 100,
            commentsPerView: average(commentsData) / average(viewsData) * 100,
            averageStars: average(averageStarsData)
        };
    };

    
    const videoChartRef = useRef(null);
    const channelChartRef = useRef(null);

    useEffect(() => {
    if (latestVideo?.wordcount) {
        const videoCanvas = document.getElementById("wordcountChart");
        const channelCanvas = document.getElementById("channelWordcountChart");

        if (!videoCanvas || !channelCanvas) {
            console.error("Canvas element not found");
            return;
        }

        const videoCtx = videoCanvas.getContext("2d");
        const channelCtx = channelCanvas.getContext("2d");

        // Destruye gráficos existentes antes de crear nuevos
        if (videoChartRef.current) {
            videoChartRef.current.destroy();
        }

        if (channelChartRef.current) {
            channelChartRef.current.destroy();
        }

        // Gráfico del vídeo
        videoChartRef.current = new Chart(videoCtx, {
            type: "bar",
            data: {
                labels: latestVideo.wordcount.map(([word]) => word),
                datasets: [
                    {
                        label: "Conteo de Palabras del Vídeo",
                        data: latestVideo.wordcount.map(([_, count]) => count),
                        backgroundColor: "rgba(75, 192, 192, 0.2)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });

        // Gráfico del canal
        channelChartRef.current = new Chart(channelCtx, {
            type: "bar",
            data: {
                labels: historicalWordCount.map(({ word }) => word),
                datasets: [
                    {
                        label: "Conteo de Palabras del Canal",
                        data: historicalWordCount.map(({ count }) => count),
                        backgroundColor: "rgba(255, 159, 64, 0.2)",
                        borderColor: "rgba(255, 159, 64, 1)",
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });

        return () => {
            // Limpia los gráficos al desmontar o actualizar
            if (videoChartRef.current) {
                videoChartRef.current.destroy();
            }
            if (channelChartRef.current) {
                channelChartRef.current.destroy();
            }
        };
    }
}, [latestVideo, historicalWordCount]);

    return (
        <div style={{
            padding: "2rem",
            background: "linear-gradient(to bottom, #d9d9d9, #b5b5b5)",
            fontFamily: "Roboto, sans-serif",
            minHeight: "100vh",
            margin: '0',
        }}>
            <div style={{ display: "flex", gap: "2rem", marginBottom: "2rem" }}>
                <div style={{
                    flex: "1",
                    padding: "1rem",
                    borderRadius: "8px",
                    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                }}>
                    <h2>Canal: {channel_title}</h2>
                    <h3>Descripción:</h3>
                    <p>{description}</p>

                    <p style={{
                marginTop: "1rem",
                fontSize: "0.9rem",
                color: "#333",
                fontStyle: "italic",
            }}>
                Descripción del canal de YouTube analizado. 
            </p>
                </div>
                <div style={{
                    flex: "1",
                    padding: "1rem",
                    borderRadius: "8px",
                    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                }}>
                    <h3>Buscar Término</h3>
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Escribe un término..."
                        style={{
                            width: "95%",
                            padding: "0.5rem",
                            marginBottom: "1rem",
                            border: "1px solid #ccc",
                            borderRadius: "4px",
                        }}
                    />
                    <button
                        onClick={handleSearch}
                        disabled={isSearching}
                        style={{
                            padding: "0.5rem 1rem",
                            backgroundColor: "#333",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            cursor: isSearching ? "wait" : "pointer",
                            opacity: isSearching ? 0.7 : 1,
                        }}
                    >
                        {isSearching ? "Buscando..." : "Buscar"}
                    </button>
                    {definition && (
                        <div style={{
                            marginTop: "1rem",
                            padding: "0.5rem",
                            borderRadius: "4px",
                            backgroundColor: "#f9f9f9",
                            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
                        }}>
                            <strong>Definición:</strong>
                            <p style={{
                                fontSize: isSearching ? "0.9rem" : "1rem",
                                color: isSearching ? "#666" : "#333",
                                fontStyle: isSearching ? "italic" : "normal"
                            }}>{definition}</p>
                            <div style={{
                                marginTop: "1rem",
                                display: "flex",
                                justifyContent: "flex-end",
                                gap: "1rem"
                            }}>
                                <span style={{
                                    alignSelf: "center",
                                    fontSize: "0.9rem",
                                    color: "#333",
                                }}>¿Le ha resultado útil?</span>
                                <button
                                    onClick={() => handleDefinitionFeedback(true)} 
                                    style={{
                                        padding: "0.5rem 1rem",
                                        backgroundColor: "#333",
                                        color: "white",
                                        border: "none",
                                        borderRadius: "4px",
                                        cursor: "pointer",
                                    }}
                                >Sí</button>
                                <button 
                                    onClick={() => handleDefinitionFeedback(false)}
                                    style={{
                                        padding: "0.5rem 1rem",
                                        backgroundColor: "#333",
                                        color: "white",
                                        border: "none",
                                        borderRadius: "4px",
                                        cursor: "pointer",
                                    }}
                                >No</button>
                            </div>
                            {showDefinitionFeedback && (
                                <p style={{
                                    marginTop: "1rem",
                                    color: "#333",
                                    fontStyle: "italic"
                                }}>Gracias por su valoración.</p>
                            )}
                        </div>
                    )}

                <p style={{
                marginTop: "1rem",
                fontSize: "0.9rem",
                color: "#333",
                fontStyle: "italic",
            }}>
                Este buscador de términos genera respuestas a búsquedas terminológicas usando inteligencia artificial. 
            </p>
                </div>
            </div>





            <div style={{ display: "flex", gap: "2rem", marginBottom: "2rem" }}>
    {latestVideo && (
        <div style={{
            flex: "0.5",
            padding: "1rem",
            borderRadius: "8px",
            background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        }}>
            <h3>Último Video</h3>
            <iframe
                width="100%"
                height="315"
                src={`https://www.youtube.com/embed/${latestVideo.videoId}`}
                title={latestVideo.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
            ></iframe>
            <p style={{ marginTop: "1rem" }}>{highlightBrands(latestVideo.title)}</p>
        </div>
    )}

    <div style={{
        flex: "1.2",
        padding: "1rem",
        borderRadius: "8px",
        background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    }}>
        <h3>Últimos Videos</h3>
        {sortedVideos.length === 0 ? (
            <p>Analiza un canal para ver la información de los últimos vídeos.</p>
        ) : (
            <>
                <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
                    <thead style={{ backgroundColor: "#e9e9e9" }}>
                        <tr>
                            <th onClick={() => handleSort("title")} style={{ cursor: "pointer", padding: "0.5rem" }}>Título</th>
                            <th onClick={() => handleSort("published_date")} style={{ cursor: "pointer", padding: "0.5rem" }}>Fecha</th>
                            <th onClick={() => handleSort("views")} style={{ cursor: "pointer", padding: "0.5rem" }}>Vistas</th>
                            <th onClick={() => handleSort("likes")} style={{ cursor: "pointer", padding: "0.5rem" }}>Likes</th>
                            <th onClick={() => handleSort("comments_count")} style={{ cursor: "pointer", padding: "0.5rem" }}>Comentarios</th>
                            <th onClick={() => handleSort("average_stars")} style={{ cursor: "pointer", padding: "0.5rem" }}>Valoración Media</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedVideos.map((video, index) => (
                            <tr key={index}>
                                <td style={{ padding: "0.5rem" }}>
                                    <a 
                                        href={`https://www.youtube.com/watch?v=${video.videoId}`} 
                                        target="_blank" 
                                        rel="noopener noreferrer" 
                                        style={{ textDecoration: "none", color: "#333" }}
                                    >
                                        {highlightBrands(video.title)}
                                    </a>
                                </td>
                                <td style={{ padding: "0.5rem" }}>{new Date(video.published_date).toLocaleString()}</td>
                                <td style={{ padding: "0.5rem" }}>{video.views}</td>
                                <td style={{ padding: "0.5rem" }}>{video.likes}</td>
                                <td style={{ padding: "0.5rem" }}>{video.comments_count}</td>
                                <td style={{ padding: "0.5rem" }}>
                                    {typeof video.average_stars === "number" ? video.average_stars.toFixed(2) : "N/A"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <p style={{
                    marginTop: "1rem",
                    fontSize: "0.9rem",
                    color: "#333",
                    fontStyle: "italic",
                }}>
                    Esta tabla muestra los 10 últimos vídeos del canal. Las marcas objetivo están en negrita. Puede ordenarse de forma ascendente o descendiente clicando sobre Título, Fecha, Visitas, Likes, Comentarios y Valoración Media.
                    La valoración media se ha generado usando un modelo de análisis de sentimiento a partir de los últimos 25 comentarios en el vídeo. 
                </p>
            </>
        )}
    </div>

    <div style={{
        flex: "0.4",
        padding: "1rem",
        borderRadius: "8px",
        background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    }}>
        <h3>Estadísticas Últimos Vídeos</h3>
        {sortedVideos.length === 0 ? (
            <p>Analiza un canal para ver las estadísticas.</p>
        ) : (
            <>
                {/* Primera tabla: Estadísticas calculadas */}
                <div style={{ marginBottom: "2rem" }}>
                    <h4 style={{ marginBottom: "1rem", color: "#333" }}>Métricas de Engagement</h4>
                    <table style={{ 
                        width: "100%", 
                        borderCollapse: "collapse",
                        backgroundColor: "white",
                        borderRadius: "8px"
                    }}>
                        <tbody>
                            {(() => {
                                const stats = calculateStats(sortedVideos);
                                if (!stats) return null;
                                
                                return Object.entries({
                                    'Tasa de Engagement (%)': stats.engagement.toFixed(2),
                                    'Crecimiento de Vistas (%)': stats.viewsGrowth.toFixed(2),
                                    'Ratio Likes/Vistas (%)': stats.likesPerView.toFixed(2),
                                    'Ratio Comentarios/Vistas (%)': stats.commentsPerView.toFixed(2),
                                    'Valoración Media': stats.averageStars.toFixed(2)
                                }).map(([key, value]) => (
                                    <tr key={key} style={{ borderBottom: "1px solid #e0e0e0" }}>
                                        <td style={{ 
                                            padding: "0.8rem", 
                                            fontWeight: "500",
                                            color: "#444"
                                        }}>
                                            {key}
                                        </td>
                                        <td style={{ 
                                            padding: "0.8rem", 
                                            textAlign: "right",
                                            fontWeight: "600",
                                            color: "#333"
                                        }}>
                                            {value}
                                        </td>
                                    </tr>
                                ));
                            })()}
                        </tbody>
                    </table>
                </div>

                {/* Segunda tabla: Estadísticas descriptivas */}
                <div>
                    <h4 style={{ marginBottom: "1rem", color: "#333" }}>Estadísticas Descriptivas</h4>
                    <table style={{ 
                        width: "100%", 
                        borderCollapse: "collapse",
                        backgroundColor: "white",
                        borderRadius: "8px"
                    }}>
                        <thead style={{ backgroundColor: "#f4f4f4" }}>
                            <tr>
                                <th style={{ padding: "0.8rem", textAlign: "left" }}>Métrica</th>
                                <th style={{ padding: "0.8rem", textAlign: "right" }}>Mín</th>
                                <th style={{ padding: "0.8rem", textAlign: "right" }}>Máx</th>
                                <th style={{ padding: "0.8rem", textAlign: "right" }}>Media</th>
                                <th style={{ padding: "0.8rem", textAlign: "right" }}>Mediana</th>
                                <th style={{ padding: "0.8rem", textAlign: "right" }}>Desv.</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(() => {
                                const stats = calculateStats(sortedVideos);
                                if (!stats) return null;
                                
                                const metrics = {
                                    "Vistas": stats.baseStats.views,
                                    "Likes": stats.baseStats.likes,
                                    "Comentarios": stats.baseStats.comments
                                };

                                return Object.entries(metrics).map(([key, values]) => (
                                    <tr key={key} style={{ borderBottom: "1px solid #e0e0e0" }}>
                                        <td style={{ padding: "0.8rem", fontWeight: "500" }}>{key}</td>
                                        <td style={{ padding: "0.8rem", textAlign: "right" }}>{values.min.toLocaleString()}</td>
                                        <td style={{ padding: "0.8rem", textAlign: "right" }}>{values.max.toLocaleString()}</td>
                                        <td style={{ padding: "0.8rem", textAlign: "right" }}>{values.mean.toFixed(0).toLocaleString()}</td>
                                        <td style={{ padding: "0.8rem", textAlign: "right" }}>{values.median.toFixed(0).toLocaleString()}</td>
                                        <td style={{ padding: "0.8rem", textAlign: "right" }}>{values.stdDev.toFixed(0).toLocaleString()}</td>
                                    </tr>
                                ));
                            })()}
                        </tbody>
                    </table>
                </div>
            </>
        )}
    </div>
</div>
{/* Third Row: Summary and Query Box */}
<div style={{ display: "flex", gap: "2rem", marginBottom: "2rem" }}>
    {/* Summary Section */}
    <div style={{
        flex: "1",
        padding: "1rem",
        borderRadius: "8px",
        background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    }}>
        <h3>Resumen del Video</h3>
        {latestVideo?.summary ? (
            <>
                <p>{latestVideo.summary}</p>
                <div style={{
                    marginTop: "1rem",
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: "2rem",
                }}>
                    <span style={{
                        alignSelf: "center",
                        fontSize: "0.9rem",
                        color: "#333",
                    }}>¿Le ha resultado útil?</span>
                    <button
                        onClick={() => handleSummaryFeedback(true)}
                        style={{
                            padding: "0.5rem 1rem",
                            backgroundColor: "#333",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                        }}
                    >Sí</button>
                    <button
                        onClick={() => handleSummaryFeedback(false)}
                        style={{
                            padding: "0.5rem 1rem",
                            backgroundColor: "#333",
                            color: "white",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                        }}
                    >No</button>
                </div>
                {showSummaryFeedback && (
                    <p style={{
                        marginTop: "1rem",
                        color: "#333",
                        fontStyle: "italic",
                    }}>Gracias por su valoración.</p>
                )}
            </>
        ) : (
            <p>No hay resumen disponible para este video.</p>
        )}
        <p style={{
        marginTop: "1rem",
        fontSize: "0.9rem",
        color: "#333",
        fontStyle: "italic",
        }}>
        Los resumenes del contenido del vídeo son generados usando inteligencia artificial en base a la transcripción de los mismos. </p>
    </div>

    {/* Query Box */}
   {/* Query Box */}
{/* Query Box */}
<div style={{
    flex: "1",
    padding: "1rem",
    borderRadius: "8px",
    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
}}>
    <h3>Consultas en Lenguaje Natural</h3>
    <input
        type="text"
        value={queryInput}
        onChange={(e) => setQueryInput(e.target.value)}
        placeholder="Escribe tu consulta en lenguaje natural..."
        style={{
            width: "95%",
            padding: "0.5rem",
            marginBottom: "1rem",
            borderRadius: "4px",
            border: "1px solid #ccc",
        }}
    />
    <button
        onClick={handleQuery}
        disabled={isQuerying}
        style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#333",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: isQuerying ? "wait" : "pointer",
            opacity: isQuerying ? 0.7 : 1,
        }}
    >
        {isQuerying ? "Consultando..." : "Consultar"}
    </button>

    {queryResult && (
        <div style={{
            marginTop: "1rem",
            padding: "0.5rem",
            borderRadius: "4px",
            backgroundColor: "#f9f9f9",
        }}>
            <strong>Resultados:</strong>
            <pre style={{
                marginTop: "0.5rem",
                background: "#f7f7f7",
                padding: "0.5rem",
                borderRadius: "4px",
                whiteSpace: "pre-wrap",
                wordWrap: "break-word",
            }}>
                {queryResult}
            </pre>
            
            <div style={{
                marginTop: "1rem",
                display: "flex",
                justifyContent: "flex-end",
                gap: "2rem",
            }}>
                <span style={{
                    alignSelf: "center",
                    fontSize: "0.9rem",
                    color: "#333",
                }}>¿Le ha resultado útil?</span>
                <button
                    onClick={() => handleQueryFeedback(true)}
                    style={{
                        padding: "0.5rem 1rem",
                        backgroundColor: "#333",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                    }}
                >Sí</button>
                <button
                    onClick={() => handleQueryFeedback(false)}
                    style={{
                        padding: "0.5rem 1rem",
                        backgroundColor: "#333",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                    }}
                >No</button>
            </div>

            {showQueryFeedback && (
                <p style={{
                    marginTop: "1rem",
                    color: "#333",
                    fontStyle: "italic",
                }}>Gracias por su valoración.</p>
            )}
        </div>
    )}

    <p style={{
        marginTop: "1rem",
        fontSize: "0.9rem",
        color: "#333",
        fontStyle: "italic",
    }}>
        Este sistema permite consultar la base de datos sin conocimientos previos de lenguajes de consulta.
    </p>
</div>


</div>

{/* Fourth Row: Detected Brands, Word Counts, and Graphs */}
<div style={{ display: "flex", gap: "2rem" }}>
    {/* Left Column: Detected Brands */}
    <div style={{
        flex: "0.5",
        padding: "1rem",
        borderRadius: "8px",
        background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
    }}>
        <h3>Marcas Detectadas</h3>
        {latestVideo?.brands?.length > 0 ? (
            <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
                <thead style={{ backgroundColor: "#e9e9e9" }}>
                    <tr>
                        <th style={{ padding: "0.5rem" }}>Marca</th>
                    </tr>
                </thead>
                <tbody>
                    {latestVideo.brands.map((brand, index) => (
                        <tr key={index}>
                            <td style={{ padding: "0.5rem" }}>{brand}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        ) : (
            <p>No se detectaron marcas en este video.</p>
        )}
    </div>

    {/* Center Column: Word Counts */}
    <div style={{ flex: "1", display: "flex", flexDirection: "row", gap: "1.5rem" }}>
        {/* Video Word Count */}
        <div style={{
            padding: "1rem",
            borderRadius: "8px",
            background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        }}>
            <h3>Conteo de Palabras del Video</h3>
            {latestVideo?.wordcount ? (
                <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
                    <thead style={{ backgroundColor: "#e9e9e9" }}>
                        <tr>
                            <th style={{ padding: "0.5rem" }}>Palabra</th>
                            <th style={{ padding: "0.5rem" }}>Conteo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {latestVideo.wordcount.map(([word, count], index) => (
                            <tr key={index}>
                                <td style={{ padding: "0.5rem" }}>{word}</td>
                                <td style={{ padding: "0.5rem" }}>{count}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No hay datos de conteo disponibles.</p>
            )}
        </div>

        {/* Channel Word Count */}
        <div style={{
            padding: "1rem",
            borderRadius: "8px",
            background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        }}>
            <h3>Conteo Palabras Histórico del Canal</h3>
            {historicalWordCount.length > 0 ? (
                <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
                    <thead style={{ backgroundColor: "#e9e9e9" }}>
                        <tr>
                            <th style={{ padding: "0.5rem" }}>Palabra</th>
                            <th style={{ padding: "0.5rem" }}>Conteo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {historicalWordCount.map((item, index) => (
                            <tr key={index}>
                                <td style={{ padding: "0.5rem" }}>{item.word}</td>
                                <td style={{ padding: "0.5rem" }}>{item.count}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No hay datos históricos disponibles.</p>
            )}
        </div>
    </div>

    {/* Right Column: Graphs */}
    <div style={{ flex: "2", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Video Word Count Graph */}
        {latestVideo?.wordcount && (
            <div style={{
                padding: "1rem",
                borderRadius: "8px",
                background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}>
                <h3>Gráfico de Conteo de Palabras del Video</h3>
                <div style={{ height: "300px", position: "relative" }}>
                    <canvas id="wordcountChart" style={{
                        width: "100%",
                        height: "100%",
                        display: "block",
                    }} />
                </div>
            </div>
        )}

        {/* Channel Word Count Graph */}
        {historicalWordCount?.length > 0 && (
            <div style={{
                padding: "1rem",
                borderRadius: "8px",
                background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}>
                <h3>Gráfico de Conteo de Palabras del Canal</h3>
                <div style={{ height: "300px", position: "relative" }}>
                    <canvas id="channelWordcountChart" style={{
                        width: "100%",
                        height: "100%",
                        display: "block",
                    }} />
                </div>
            </div>
        )}
    </div>
</div>

</div>
    );
};

export default Dashboard;