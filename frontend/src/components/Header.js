// Header.js
import React from 'react';

const Header = () => {
    return (
        <header
            style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '2rem',
                backgroundColor: '#333',
                color: 'white',
                height: '80px',
                position: 'relative' 
            }}
        >
            <h1 style={{ 
                position: 'absolute', 
                left: '50%', 
                transform: 'translateX(-50%)', 
                margin: '0',
                padding: '0',
                fontSize: '1.5rem',
                fontFamily: 'Roboto, sans-serif',
                color: 'white',
                fontWeight: '400'
            }}>
                YouTube Influencer Marketing Analytics Tool
            </h1>
            <div style={{ width: '100px' }}></div> {/* Espaciador izquierdo */}
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
                    zIndex: 1 
                }}
            >
                Contacto
            </button>
        </header>
    );
};

export default Header;
