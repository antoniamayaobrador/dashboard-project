// ChannelGrid.js
import React from 'react';
import ChannelCard from './ChannelCard';

const ChannelGrid = ({ channels, addChannelData, activeSlot, setActiveSlot }) => {
    console.log('ChannelGrid rendering, activeSlot:', activeSlot); // Debugging

    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2rem',
            padding: '2rem',
            background: '#b5b5b5'
        }}>
            {channels.map((channel, index) => {
                console.log(`Rendering card ${index}, isActive: ${activeSlot === index}`); // Debugging
                return (
                    <ChannelCard
                        key={index}
                        index={index}
                        channel={channel}
                        addChannelData={addChannelData}
                        isActive={activeSlot === index}
                        setActiveSlot={setActiveSlot}
                    />
                );
            })}
        </div>
    );
};

export default ChannelGrid;
