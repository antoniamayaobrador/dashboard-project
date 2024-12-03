// ChannelCard.js
import React from 'react';
import Form from './Form';
import Dashboard from './Dashboard';

const ChannelCard = ({ index, channel, addChannelData, isActive, setActiveSlot }) => {
    const handleClick = () => {
        console.log('Card clicked:', index);
        setActiveSlot(current => current === index ? null : index);
    };

    // Estilos para la card en modo pantalla completa
    const fullscreenStyle = {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 1000,
        margin: 0,
        borderRadius: '0 0 15px 15px',  // Solo bordes inferiores redondeados
        overflow: 'auto',
        transition: 'all 0.3s ease-in-out',
        padding: '20px',
        background: '#333',
        boxSizing: 'border-box',
    };
    
    const baseCardStyle = {
        background: 'white',
        borderRadius: '8px',
        transition: 'all 0.3s ease-in-out', // Misma transición para consistencia
        margin: '10px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        border: '1px solid #ddd',
    };
    

    // Si no hay canal (slot vacío)
    if (!channel) {
        return (
            <div 
                onClick={handleClick}
                style={{
                    ...baseCardStyle,
                    height: '100px',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                    cursor: 'pointer',
                    border: '2px dashed #333b',
                }}
            >
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    background: "linear-gradient(to bottom, #f7f7f7, #d4d4d4)",
                    color: '#b333',
                }}>
                    <span style={{ fontSize: '2rem' }}>+</span>
                    <span style={{ fontSize: '0.8rem', marginTop: '5px' }}>Añadir canal</span>
                </div>
            </div>
        );
    }

    // Si hay canal
    return (
        <div 
            style={{
                ...(isActive ? fullscreenStyle : baseCardStyle),
                padding: '1rem',
                minHeight: '100px',
                borderRadius: isActive ? '0 0 15px 15px' : '8px', 

            }}
        >
            {/* Header */}
        
        <div 
            style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: isActive ? '#333' : 'transparent',
                padding: '10px',
                marginBottom: isActive ? '1rem' : '0',
                borderRadius: '4px',
                position: isActive ? 'sticky' : 'relative',
                top: isActive ? '0' : 'auto',
                zIndex: isActive ? 1001 : 1,
                borderBottom: isActive ? '1px solid #666' : 'none', // Borde más oscuro
                color: isActive ? 'white' : 'inherit', // Texto blanco cuando está expandido
                transition: 'all 1s ease-in-out' // Transición suave
            }}
        >
            <h3 style={{ 
                margin: 0,
                color: isActive ? 'white' : '#666',
                transition: 'color 0.3s ease-in-out' // Transición suave para el color
            }}>
                    {channel.channel_title}
                </h3>
                <button
                    onClick={handleClick}
                    style={{
                        width: '30px',
                        height: '30px',
                        borderRadius: '50%',
                        border: 'none',
                        background: isActive ? '#333' : '#f0f0f0',
                        color: isActive ? 'white' : '#666',
                        cursor: 'pointer',
                        fontSize: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: '#b5b5b5',
                        transition: 'all 0.3s ease-in-out' // Transición suave

                    }}
                >
                    {isActive ? '×' : '+'}
                </button>
            </div>

            {/* Contenido */}
            <div style={{
                opacity: isActive ? 1 : 0,
                maxHeight: isActive ? 'none' : '0',
                transition: 'all 1s ease',
                background: "#333b",
                overflow: 'hidden',
            }}>
                {isActive && (
                    <div style={{ padding: '20px 0' }}>
                        <Form setDashboardData={(data) => addChannelData(data, index)} />
                        <Dashboard data={channel} />
                    </div>
                )}
            </div>

            {/* Botón expandir (solo visible cuando está contraído) */}
            {!isActive && (
                <div style={{
                    textAlign: 'center',
                    padding: '5px 0',
                }}>
                    <button
                        onClick={handleClick}
                        style={{
                            border: 'none',
                            background: 'none',
                            color: '#333b',
                            cursor: 'pointer',
                            padding: '5px 10px',
                            
                        }}
                    >
                    </button>
                </div>
            )}
        </div>
    );
};

export default ChannelCard;
