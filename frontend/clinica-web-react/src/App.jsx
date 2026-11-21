import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PatientProvider } from './context/PatientContext';
import OfflineBoundary from './components/OfflineBoundary';
import AppRouter from './router/AppRouter';
import PwaInstallPrompt from './components/PwaInstallPrompt';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <OfflineBoundary>
          <PatientProvider>
            <AppRouter />
            <PwaInstallPrompt />  
          </PatientProvider>
        </OfflineBoundary>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
