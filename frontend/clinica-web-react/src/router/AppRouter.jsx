import { Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';

import LoginScreen from '../pages/auth/LoginScreen';
import MainLayout from '../components/layout/MainLayout';
import DashboardScreen from '../pages/dashboard/DashboardScreen';

// Enfermeria
import EnfermeriaScreen from '../pages/enfermeria/EnfermeriaScreen';
import PatientDetailScreen from '../pages/enfermeria/PatientDetailScreen';
import EnfermeriaVitalSignsScreen from '../pages/enfermeria/EnfermeriaVitalSignsScreen';
import EnfermeriaNoteScreen from '../pages/enfermeria/EnfermeriaNoteScreen';
import EnfermeriaMedicationsScreen from '../pages/enfermeria/EnfermeriaMedicationsScreen';
import EnfermeriaAssessmentScreen from '../pages/enfermeria/EnfermeriaAssessmentScreen';
import EnfermeriaCareScreen from '../pages/enfermeria/EnfermeriaCareScreen';
import EnfermeriaFluidBalanceScreen from '../pages/enfermeria/EnfermeriaFluidBalanceScreen';

//Medico
import MedicoScreen from '../pages/medico/MedicoScreen';
import MedicoPatientDetailScreen from '../pages/medico/PatientDetailScreen';
import VitalSignsScreen from '../pages/medico/VitalSignsScreen';
import MedicalNoteScreen from '../pages/medico/MedicalNoteScreen';
import DiagnosisScreen from '../pages/medico/DiagnosisScreen';
import HistoriaClinicaScreen from '../pages/medico/HistoriaClinicaScreen';
import PrescriptionScreen from '../pages/medico/PrescriptionScreen';
import LabExamsScreen from '../pages/medico/LabExamsScreen';
import ImagingExamsScreen from '../pages/medico/ImagingExamsScreen';
import PrintDocsScreen from '../pages/medico/PrintDocsScreen';
import StudyResultsScreen from '../pages/medico/StudyResultsScreen';
import VitalSignsListScreen from '../pages/medico/VitalSignsListScreen';

//Estudios
import EstudiosScreen from '../pages/estudios/EstudiosScreen';
import SubirResultadoScreen from '../pages/estudios/SubirResultadoScreen';
import VerResultadoLabScreen from '../pages/estudios/VerResultadoLabScreen';
import VerResultadoGabScreen from '../pages/estudios/VerResultadoGabScreen';
import EditarResultadoLabScreen from '../pages/estudios/EditarResultadoLabScreen';
import EditarResultadoGabScreen from '../pages/estudios/EditarResultadoGabScreen';

// Config
import ConfigScreen from '../pages/config/ConfigScreen';
import GeneralSettingsScreen from '../pages/config/GeneralSettingsScreen';
import UsuariosConfigScreen from '../pages/config/UsuariosConfigScreen';
import CamasConfigScreen from '../pages/config/CamasConfigScreen';
import ServiciosConfigScreen from '../pages/config/ServiciosConfigScreen';
import DiagnosticosConfigScreen from '../pages/config/DiagnosticosConfigScreen';
import AutomationConfigScreen from '../pages/config/AutomationConfigScreen';
import BackupConfigScreen from '../pages/config/BackupConfigScreen';
import ProfileConfigScreen from '../pages/config/ProfileConfigScreen';
import AdminScreen from '../pages/administrativo/AdminScreen.jsx';
import PacientesScreen from '../pages/administrativo/PacientesScreen.jsx';
import NuevoPacienteScreen from '../pages/administrativo/NuevoPacienteScreen.jsx';
import PacienteDetailScreen from '../pages/administrativo/PacienteDetailScreen.jsx';
import CensoScreen from '../pages/administrativo/CensoScreen.jsx';
import CorteCajaScreen from '../pages/administrativo/CorteCajaScreen.jsx';

// Spark y Analítica
import SparkDashboard from '../pages/spark/SparkDashboard.jsx';
import AnalyticsScreen from '../pages/spark/AnalyticsScreen.jsx';
import MetAnalyticsScreen from '../pages/spark/MetAnalyticsScreen.jsx';
import ClinicalAnalyticsScreen from '../pages/spark/ClinicalAnalyticsScreen.jsx';
import UnsupervisedAnalyticsScreen from '../pages/spark/UnsupervisedAnalyticsScreen.jsx';

const PrivateRoute = ({ children }) => {
  const { t } = useTranslation();
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <div className="loading-screen">{t('common.loading')}</div>;

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const PublicLoginRoute = () => {
  const { t } = useTranslation();
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <div className="loading-screen">{t('common.loading')}</div>;

  return isAuthenticated ? <Navigate to="/" replace /> : <LoginScreen />;
};

export default function AppRouter() {
  const { user } = useAuth();

  const role = user?.role;

  const isAdmin = role === 'admin';
  const isAdminOrAdministrativo = isAdmin || role === 'administrativo';
  const isMedico = role === 'medico';
  const isEnfermeria = role === 'enfermero' || role === 'enfermeria';
  const isEstudios = role === 'estudios';

  return (
    <Routes>
      <Route path="/login" element={<PublicLoginRoute />} />

      <Route
        path="/*"
        element={
          <PrivateRoute>
            <MainLayout>
              <Routes>
                <Route path="/" element={<DashboardScreen />} />

                {isAdminOrAdministrativo && (
                  <>
                    <Route path="admin" element={<AdminScreen />} />
                    <Route path="pacientes" element={<PacientesScreen />} />
                    <Route path="pacientes/:id" element={<PacienteDetailScreen />} />
                    <Route path="pacientes/:id/editar" element={<NuevoPacienteScreen />} />
                    <Route path="nuevo-paciente" element={<NuevoPacienteScreen />} />
                    <Route path="cuenta-paciente" element={<PacienteDetailScreen />} />
                    <Route path="censo" element={<CensoScreen />} />
                    <Route path="corte-caja" element={<CorteCajaScreen />} />
                    <Route path="camas" element={<Navigate to="/config/camas" replace />} />
                    <Route path="admin/spark" element={<SparkDashboard />} />
                    <Route path="admin/spark/analytics" element={<AnalyticsScreen />} />
                    <Route path="admin/spark/met" element={<MetAnalyticsScreen />} />
                    <Route path="admin/spark/clinical" element={<ClinicalAnalyticsScreen />} />
                    <Route path="admin/spark/unsupervised" element={<UnsupervisedAnalyticsScreen />} />
                  </>
                )}

                {(isAdmin || isMedico) && (
                  <>
                    <Route path="medico" element={<MedicoScreen />} />
                    <Route path="medico/paciente/:id" element={<MedicoPatientDetailScreen />} />
                    <Route path="medico/paciente/:idAtencion/:idExp" element={<MedicoPatientDetailScreen />} />
                    <Route path="medico/historia-clinica" element={<HistoriaClinicaScreen />} />
                    <Route path="medico/signos-vitales" element={<VitalSignsScreen />} />
                    <Route path="medico/signos-vitales/historial" element={<VitalSignsListScreen />} />
                    <Route path="medico/nota-medica" element={<MedicalNoteScreen />} />
                    <Route path="medico/diagnostico" element={<DiagnosisScreen />} />
                    <Route path="medico/receta" element={<PrescriptionScreen />} />
                    <Route path="medico/lab-exams" element={<LabExamsScreen />} />
                    <Route path="medico/imaging-exams" element={<ImagingExamsScreen />} />
                    <Route path="medico/imprimir" element={<PrintDocsScreen />} />
                    <Route path="medico/resultados" element={<StudyResultsScreen />} />
                  </>
                )}

                {(isAdmin || isEnfermeria) && (
                  <>
                    <Route path="enfermeria" element={<EnfermeriaScreen />} />
                    <Route path="enfermeria/paciente/:id" element={<PatientDetailScreen />} />
                    <Route path="enfermeria/paciente/:idAtencion/:idExp" element={<PatientDetailScreen />} />
                    <Route path="enfermeria/signos-vitales" element={<EnfermeriaVitalSignsScreen />} />
                    <Route path="enfermeria/nota" element={<EnfermeriaNoteScreen />} />
                    <Route path="enfermeria/medicamentos" element={<EnfermeriaMedicationsScreen />} />
                    <Route path="enfermeria/valoracion" element={<EnfermeriaAssessmentScreen />} />
                    <Route path="enfermeria/cuidados" element={<EnfermeriaCareScreen />} />
                    <Route path="enfermeria/balance-hidrico" element={<EnfermeriaFluidBalanceScreen />} />
                  </>
                )}

                {(isAdmin || isMedico || isEstudios) && (
                  <>
                    <Route path="estudios" element={<EstudiosScreen />} />
                    <Route path="subir-resultado" element={<SubirResultadoScreen />} />
                    <Route path="ver-resultado-lab" element={<VerResultadoLabScreen />} />
                    <Route path="ver-resultado-gab" element={<VerResultadoGabScreen />} />
                    <Route path="editar-resultado-lab" element={<EditarResultadoLabScreen />} />
                    <Route path="editar-resultado-gab" element={<EditarResultadoGabScreen />} />

                    <Route path="estudios/subir-resultado" element={<SubirResultadoScreen />} />
                    <Route path="estudios/ver-lab" element={<VerResultadoLabScreen />} />
                    <Route path="estudios/ver-gab" element={<VerResultadoGabScreen />} />
                    <Route path="estudios/editar-lab" element={<EditarResultadoLabScreen />} />
                    <Route path="estudios/editar-gab" element={<EditarResultadoGabScreen />} />
                  </>
                )}

                {isAdmin && (
                  <>
                    <Route path="config" element={<ConfigScreen />} />
                    <Route path="config/general" element={<GeneralSettingsScreen />} />
                    <Route path="config/usuarios" element={<UsuariosConfigScreen />} />
                    <Route path="config/camas" element={<CamasConfigScreen />} />
                    <Route path="config/servicios" element={<ServiciosConfigScreen />} />

                    <Route path="config/diagnosticos" element={<DiagnosticosConfigScreen />} />

                    <Route path="config/automatizacion" element={<AutomationConfigScreen />} />
                    <Route path="config/backup" element={<BackupConfigScreen />} />
                    <Route path="config/perfil" element={<ProfileConfigScreen />} />
                  </>
                )}

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </MainLayout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
