import React from 'react';
import HealthCheck from './components/HealthCheck';

const App: React.FC = () => {
  return (
    <div className="App">
      <h1 className="text-2xl font-bold">Welcome to the Project</h1>
      <HealthCheck />
    </div>
  );
};

export default App;