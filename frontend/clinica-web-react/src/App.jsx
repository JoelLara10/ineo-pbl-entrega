import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PatientProvider } from './context/PatientContext';
import AppRouter from './router/AppRouter';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PatientProvider>
          <AppRouter />
        </PatientProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;