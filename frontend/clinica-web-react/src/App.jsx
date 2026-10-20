import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PatientProvider } from './context/PatientContext';
import OfflineBoundary from './components/OfflineBoundary';
import AppRouter from './router/AppRouter';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <OfflineBoundary>
          <PatientProvider>
            <AppRouter />
          </PatientProvider>
        </OfflineBoundary>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
