import React, { useState } from 'react';
import axios from 'axios';

const Form = ({ setDashboardData }) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/analyze', { url });
            setDashboardData(response.data);
        } catch (err) {
            console.error('Error while analyzing URL:', err);
            setError('Failed to analyze the URL. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ 
            padding: '0.5rem',
            marginBottom: '1rem'
        }}>
            <div style={{
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center'
            }}>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="URL del Canal de Youtube"
                    style={{
                        flex: 1,
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: '1px solid #ccc'
                    }}
                />
                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        padding: "0.5rem 1rem",
                        backgroundColor: "#333",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: loading ? "wait" : "pointer",
                        opacity: loading ? 0.7 : 1
                    }}
                >
                    {loading ? 'Analizando...' : 'Analizar'}
                </button>
            </div>
            {error && (
                <p style={{ color: 'red', margin: '0.5rem 0', fontSize: '0.9rem' }}>
                    {error}
                </p>
            )}
        </form>
    );
};

export default Form;