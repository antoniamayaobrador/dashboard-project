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
    flex: "1",
    padding: "1rem",
    borderRadius: "8px",
    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
}}>
    <h3>Últimos Videos</h3>
    {sortedVideos.length === 0 ? (
        <p>No se encontraron videos para este canal.</p>
    ) : (
        <>
            <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
                <thead style={{ backgroundColor: "#e9e9e9" }}>
                    <tr>
                        <th onClick={() => handleSort("title")} style={{ cursor: "pointer", padding: "0.5rem" }}>Título</th>
                        <th onClick={() => handleSort("published_date")} style={{ cursor: "pointer", padding: "0.5rem" }}>Fecha</th>
                        <th onClick={() => handleSort("views")} style={{ cursor: "pointer", padding: "0.5rem" }}>Vistas</th>
                        <th onClick={() => handleSort("likes")} style={{ cursor: "pointer", padding: "0.5rem" }}>Likes</th>
                        <th onClick={() => handleSort("comments")} style={{ cursor: "pointer", padding: "0.5rem" }}>Comentarios</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedVideos.map((video, index) => (
                        <tr key={index}>
                            <td style={{ padding: "0.5rem" }}>{highlightBrands(video.title)}</td>
                            <td style={{ padding: "0.5rem" }}>{new Date(video.published_date).toLocaleString()}</td>
                            <td style={{ padding: "0.5rem" }}>{video.views}</td>
                            <td style={{ padding: "0.5rem" }}>{video.likes}</td>
                            <td style={{ padding: "0.5rem" }}>{video.comments}</td>
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
                Esta tabla muestra los 10 últimos vídeos del canal. Las marcas objetivo están en negrita. Puede ordenarse de forma ascendente o descendiente clicando sobre Título, Fecha, Visitas, Likes y Comentarios.
            </p>
        </>
    )}
</div>

            </div>

            <div style={{
    display: "grid",
    gridTemplateColumns: "1fr 0.5fr 0.5fr", // Three columns
    gap: "2rem",
    alignItems: "start",
}}>
    {/* First Column: Summary, Brands, and Historical Word Count */}
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {latestVideo?.summary && (
            <div style={{
                padding: "1rem",
                borderRadius: "8px",
                background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}>
                <h3>Resumen del Video</h3>
                <p>{latestVideo.summary}</p>
            </div>
        )}
        <div style={{
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

    {/* Second Column: Word Count Table for Video */}
    <div>
        {latestVideo?.wordcount && (
            <div style={{
                padding: "1rem",
                borderRadius: "8px",
                background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}>
                <h3>Conteo de Palabras del Video</h3>
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
            </div>
        )}
    </div>

    <div style={{
    display: "flex",
    flexDirection: "column",
    gap: "2rem", 
    width: "100%",
    maxWidth: "800px", 
    margin: "0 auto", 
    padding: "0", 
}}>
    {latestVideo?.wordcount && (
        <div style={{
            width: "96%",
            padding: "16px",
            borderRadius: "8px",
            background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        }}>
            <div style={{ marginBottom: "8px" }}>
                <h3 style={{
                    fontSize: "18px",
                    fontWeight: "600",
                }}>
                    Gráfico de Conteo de Palabras del Video
                </h3>
            </div>
            <div style={{
                overflowX: "auto", // Equivalent to overflow-x-auto
            }}>
                <div style={{
                    minWidth: "600px", // Equivalent to min-w-[600px]
                    height: "300px", // Equivalent to h-[300px]
                    position: "relative",
                }}>
                    <canvas id="wordcountChart" style={{
                        width: "80%",
                        height: "100%",
                        display: "block",
                    }} />
                </div>
            </div>
        </div>
    )}

    {historicalWordCount?.length > 0 && (
        <div style={{
            width: "96%",
            padding: "16px",
            borderRadius: "8px",
            background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        }}>
            <div style={{ marginBottom: "8px" }}>
                <h3 style={{
                    fontSize: "18px",
                    fontWeight: "600",
                }}>
                    Gráfico de Conteo de Palabras del Canal
                </h3>
            </div>
            <div style={{
                overflowX: "auto", 
            }}>
                <div style={{
                    minWidth: "auto", 
                    height: "300px", 
                    position: "relative",
                }}>
                    <canvas id="channelWordcountChart" style={{
                        width: "80%",
                        height: "100%",
                        display: "block",
                    }} />
                </div>
            </div>
        </div>
    )}
</div>


</div>

        </div>
    );
};

export default Dashboard;