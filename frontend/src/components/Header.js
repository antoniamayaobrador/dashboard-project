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
                height: '80px', // Adjust for a taller header
            }}
        >
            <h1 style={{ margin: '0', padding: '0', fontSize: '1.5rem' }}>
                YouTube Influencer Marketing Analytics
            </h1>
            <button
                onClick={() => (window.location.href = 'mailto:influencermarketingyoutubetool@gmail.com')}
                style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#d3d3d3', // Light gray background
                    color: '#000', // Black text
                    border: 'none',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontSize: '1rem',
                }}
            >
                Contacto
            </button>
        </header>
    );
};

export default Header;
