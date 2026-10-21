import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { UxContext } from './ux'
import { loadUxVersion } from './uiConfig'

const root = createRoot(document.getElementById('root')!);

async function bootstrap() {
  try {
    const version = await loadUxVersion(import.meta.env.VITE_API_BASE_URL);
    if (version === 2) await import('./modern/modern.css');
    document.documentElement.dataset.uxVersion = String(version);
    root.render(
      <StrictMode>
        <UxContext.Provider value={version}><App /></UxContext.Provider>
      </StrictMode>,
    );
  } catch {
    root.render(
      <main role="alert" style={{ maxWidth: 560, margin: '15vh auto', padding: 24 }}>
        <h1>Portal temporarily unavailable</h1>
        <p>Unable to load the interface configuration. Please try again.</p>
        <button onClick={() => void bootstrap()}>Try again</button>
      </main>,
    );
  }
}

void bootstrap();
