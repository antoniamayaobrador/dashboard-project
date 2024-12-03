// ChannelGrid.js
import React from 'react';
import ChannelCard from './ChannelCard';

const ChannelGrid = ({ channels, addChannelData, activeSlot, setActiveSlot }) => {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'row',
            flex : '0.5', 
            gap: '2rem',
            padding: '2rem',
            width: '100%',
            height: '100%', 
            boxSizing: 'border-box',
            overflow: 'hidden'
        }}>
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '2rem',
                flex: '2'
            }}>
                {channels.map((channel, index) => (
                    <ChannelCard
                        key={index}
                        index={index}
                        channel={channel}
                        addChannelData={addChannelData}
                        isActive={activeSlot === index}
                        setActiveSlot={setActiveSlot}
                    />
                ))}
            </div>
            <div style={{
                background: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                border: '1px solid #ddd',
                padding: '20px',
                margin: '10px',
                marginLeft: 0,
                flex: '1',
                overflowY: 'auto',
                maxHeight: '100%'
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
                    <li>Seleccione un slot vacío (marcado con +)</li>
                    <li>Pegue la URL del canal de YouTube a analizar</li>
                    <li>Haga clic en "Analizar" y espera unos minutos</li>
                    <li>Explore las diferentes secciones del análisis:
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
                    <li>Puede analizar hasta 15 canales simultáneamente</li>
                    <li>Use los controles + y x para expandir/contraer el análisis</li>
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
                    Si alguna funcionalidad aparece vacía, cierre y vuelva a abrir la carta para solucionarlo. 
                </div>
            </div>
        </div>
    );
};

export default ChannelGrid;