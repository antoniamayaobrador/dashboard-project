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
            // Envía la solicitud POST al backend
            const response = await axios.post('http://127.0.0.1:8000/api/analyze', {
                url: url
            });
            
            // Actualiza el estado con los datos recibidos
            setDashboardData(response.data);
        } catch (err) {
            console.error('Error while analyzing URL:', err);
            setError('Failed to analyze the URL. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ padding: '1rem' }}>
            <label htmlFor="url">URL del Canal de YouTube:</label>
            <input
                type="text"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="URL del Canal de Youtube: "
                style={{ margin: '0.5rem', padding: '0.5rem', width: '80%' }}
            />
            <button
                type="submit"
                style={{  padding: "0.5rem 1rem",
                    backgroundColor: "#333",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer", }}
                disabled={loading}
            >
                {loading ? 'Análisis en curso...' : 'Analizar'}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </form>
    );
};

export default Form;

const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
        console.log("Sending URL to backend:", url);
        const response = await axios.post('http://127.0.0.1:8000/api/analyze', { url });
        console.log("Response from backend:", response.data);
        setDashboardData(response.data);
    } catch (err) {
        console.error('Error while analyzing URL:', err.response || err);
        setError('Failed to analyze the URL. Please try again.');
    } finally {
        setLoading(false);
    }
};
