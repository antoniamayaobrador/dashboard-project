// Instructions.js
import React from 'react';

const Instructions = () => (
    <div style={{
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        border: '1px solid #ddd',
        padding: '20px',
        margin: '10px',
        flex: '1',
        maxHeight: 'calc(80vh - 250px)', // Ajustar para permitir que el footer sea visible
        overflowY: 'auto'
    }}>
        <h3 style={{ 
            marginTop: 0, 
            color: '#333',
            borderBottom: '1px solid #eee',
            paddingBottom: '10px'
        }}>Instrucciones de Uso</h3>
        <ol style={{ 
            padding: '0 0 0 20px',
            margin: 0,
            color: '#666',
            fontSize: '0.9rem',
            lineHeight: '1.6'
        }}>
            <li>Selecciona un slot vacío (marcado con +)</li>
            <li>Pega la URL del canal de YouTube a analizar</li>
            <li>Haz clic en "Analizar" y espera unos minutos</li>
            <li>Explora las diferentes secciones del análisis:
                <ul style={{ 
                    marginTop: '8px',
                    marginBottom: '8px',
                    paddingLeft: '20px'
                }}>
                    <li>Estadísticas del canal</li>
                    <li>Métricas de engagement</li>
                    <li>Análisis de palabras clave</li>
                    <li>Detección de marcas</li>
                </ul>
            </li>
            <li>Puedes analizar hasta 15 canales simultáneamente</li>
            <li>Usa los controles + y - para expandir/contraer el análisis</li>
        </ol>
        <div style={{ 
            marginTop: '20px',
            padding: '10px',
            background: '#f9f9f9',
            borderRadius: '4px',
            fontSize: '0.8rem',
            color: '#666',
            fontStyle: 'italic'
        }}>
            Nota: El análisis puede tardar varios minutos dependiendo del tamaño del canal y la cantidad de vídeos a procesar.
        </div>
    </div>
);

export default Instructions;
