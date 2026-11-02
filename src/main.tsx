import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const rootElement = document.getElementById('root');
if (rootElement) {
  // Hide initial loading splash if present
  const splash = document.getElementById('bistro-splash');
  if (splash) {
    splash.style.display = 'none';
  }

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
