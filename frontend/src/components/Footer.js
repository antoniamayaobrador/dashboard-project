// Footer.js
import React from 'react';

const Footer = () => {
    return (
        <footer
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '2rem',
                backgroundColor: '#333',
                color: 'white',
                marginTop: 'auto', // Cambiado de 2rem a auto para que se pegue al fondo
                width: '100%',
                boxSizing: 'border-box',
                flexShrink: 0, // Evita que el footer se encoja
            }}
        >
            <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                <p style={{ margin: '0', fontSize: '1rem' }}>Antoni Amaya Obrador</p>
                <p style={{ margin: '0', fontSize: '0.9rem' }}>Todos los derechos reservados</p>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <button
                    onClick={() => (window.location.href = 'mailto:influencermarketingyoutubetool@gmail.com')}
                    style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: '#d3d3d3',
                        color: '#000',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        fontSize: '1rem',
                        margin: '0'
                    }}
                >
                    Contacto
                </button>
                <button
                    onClick={() => window.open('https://www.linkedin.com/in/antoniamaya/', '_blank')}
                    style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: '#d3d3d3',
                        color: '#000',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                        fontSize: '1rem',
                    }}
                >
                    LinkedIn
                </button>
            </div>
            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                <p style={{ fontSize: '0.8rem', margin: '0', fontStyle: 'italic' }}>
                    Disclaimer: Los resultados presentados se generan utilizando inteligencia artificial.
                    No deben ser utilizados para decisiones médicas, legales o financieras sin verificación adicional.
                </p>
            </div>
        </footer>
    );
};

export default Footer;