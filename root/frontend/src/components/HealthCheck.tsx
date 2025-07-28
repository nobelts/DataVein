import React, { useEffect, useState } from 'react';

const HealthCheck: React.FC = () => {
    const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    setIsHealthy(true);
                } else {
                    setIsHealthy(false);
                }
            } catch (error) {
                setIsHealthy(false);
            }
        };

        checkHealth();
    }, []);

    return (
        <div>
            <h1>Health Check</h1>
            {isHealthy === null ? (
                <p>Checking...</p>
            ) : isHealthy ? (
                <p>Backend is healthy!</p>
            ) : (
                <p>Backend is not healthy!</p>
            )}
        </div>
    );
};

export default HealthCheck;