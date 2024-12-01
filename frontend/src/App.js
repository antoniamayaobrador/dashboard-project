import React, { useState } from 'react';
import Header from './components/Header';
import Form from './components/Form';
import Dashboard from './components/Dashboard';
import Footer from './components/Footer'; // Importar el Footer

const App = () => {
    const [dashboardData, setDashboardData] = useState(null);

    return (
        <div>
            {/* Header */}
            <Header />

            {/* Form para cargar datos */}
            <Form setDashboardData={setDashboardData} />

            {/* Dashboard que muestra los datos cargados */}
            <Dashboard data={dashboardData} />

            {/* Footer al final de la aplicación */}
            <Footer />
        </div>
    );
};

export default App;
