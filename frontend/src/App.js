// App.js
import React, { useState } from 'react';
import Header from './components/Header';
import ChannelGrid from './components/ChannelGrid';
import Footer from './components/Footer';

const App = () => {
    // Cambiar a 15 slots (5 filas x 3 columnas)
    const initialChannels = Array(15).fill(null).map((_, index) => index < 15 ? {
        channel_title: ` `,
        description: `Analiza un canal para ver la descripción.`,
        videos: []
    } : null);

    const [channels, setChannels] = useState(initialChannels);
    const [activeSlot, setActiveSlot] = useState(null);

    const addChannelData = (data, index) => {
        console.log('Adding data to slot:', index, data);
        const newChannels = [...channels];
        newChannels[index] = data;
        setChannels(newChannels);
    };

    return (
        <div style={{ 
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            margin: 0,
            padding: 0
        }}>
            <Header />
            <main style={{
                flex: '1 0 auto',
                display: 'flex',
                flexDirection: 'column'
            }}>
                <ChannelGrid 
                    channels={channels}
                    addChannelData={addChannelData}
                    activeSlot={activeSlot}
                    setActiveSlot={setActiveSlot}
                />
            </main>
            <Footer />
        </div>
    );
};

export default App;