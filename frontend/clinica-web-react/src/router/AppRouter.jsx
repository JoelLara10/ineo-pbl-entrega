import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';

// Layouts y componentes base (Carga normal)
import MainLayout from '../components/layout/MainLayout';

// --- CARGA DIFERIDA (LAZY LOADING) DE PÁGINAS ---

// Auth & Dashboard
const LoginScreen = lazy(() => import('../pages/auth/LoginScreen'));
const DashboardScreen = lazy(() => import('../pages/dashboard/DashboardScreen'));

// Enfermería
const EnfermeriaScreen = lazy(() => import('../pages/enfermeria/EnfermeriaScreen'));
const PatientDetailScreen = lazy(() => import('../pages/enfermeria/PatientDetailScreen'));
const EnfermeriaVitalSignsScreen = lazy(() => import('../pages/enfermeria/EnfermeriaVitalSignsScreen'));
const EnfermeriaNoteScreen = lazy(() => import('../pages/enfermeria/EnfermeriaNoteScreen'));
const EnfermeriaMedicationsScreen = lazy(() => import('../pages/enfermeria/EnfermeriaMedicationsScreen'));
const EnfermeriaAssessmentScreen = lazy(() => import('../pages/enfermeria/EnfermeriaAssessmentScreen'));
const EnfermeriaCareScreen = lazy(() => import('../pages/enfermeria/EnfermeriaCareScreen'));
const EnfermeriaFluidBalanceScreen = lazy(() => import('../pages/enfermeria/EnfermeriaFluidBalanceScreen'));

// Médico
const MedicoScreen = lazy(() => import('../pages/medico/MedicoScreen'));
const MedicoPatientDetailScreen = lazy(() => import('../pages/medico/PatientDetailScreen'));
const VitalSignsScreen = lazy(() => import('../pages/medico/VitalSignsScreen'));
const MedicalNoteScreen = lazy(() => import('../pages/medico/MedicalNoteScreen'));
const DiagnosisScreen = lazy(() => import('../pages/medico/DiagnosisScreen'));
const HistoriaClinicaScreen = lazy(() => import('../pages/medico/HistoriaClinicaScreen'));
const PrescriptionScreen = lazy(() => import('../pages/medico/PrescriptionScreen'));
const LabExamsScreen = lazy(() => import('../pages/medico/LabExamsScreen'));
const ImagingExamsScreen = lazy(() => import('../pages/medico/ImagingExamsScreen'));
const PrintDocsScreen = lazy(() => import('../pages/medico/PrintDocsScreen'));
const StudyResultsScreen = lazy(() => import('../pages/medico/StudyResultsScreen'));
const VitalSignsListScreen = lazy(() => import('../pages/medico/VitalSignsListScreen'));

// Estudios
const EstudiosScreen = lazy(() => import('../pages/estudios/EstudiosScreen'));
const SubirResultadoScreen = lazy(() => import('../pages/estudios/SubirResultadoScreen'));
const VerResultadoLabScreen = lazy(() => import('../pages/estudios/VerResultadoLabScreen'));
const VerResultadoGabScreen = lazy(() => import('../pages/estudios/VerResultadoGabScreen'));
const EditarResultadoLabScreen = lazy(() => import('../pages/estudios/EditarResultadoLabScreen'));
const EditarResultadoGabScreen = lazy(() => import('../pages/estudios/EditarResultadoGabScreen'));

// Configuración
const ConfigScreen = lazy(() => import('../pages/config/ConfigScreen'));
const GeneralSettingsScreen = lazy(() => import('../pages/config/GeneralSettingsScreen'));
const UsuariosConfigScreen = lazy(() => import('../pages/config/UsuariosConfigScreen'));
const CamasConfigScreen = lazy(() => import('../pages/config/CamasConfigScreen'));
const ServiciosConfigScreen = lazy(() => import('../pages/config/ServiciosConfigScreen'));
const DiagnosticosConfigScreen = lazy(() => import('../pages/config/DiagnosticosConfigScreen'));
const AutomationConfigScreen = lazy(() => import('../pages/config/AutomationConfigScreen'));
const BackupConfigScreen = lazy(() => import('../pages/config/BackupConfigScreen'));
const ProfileConfigScreen = lazy(() => import('../pages/config/ProfileConfigScreen'));

// Administrativo
const AdminScreen = lazy(() => import('../pages/administrativo/AdminScreen.jsx'));
const PacientesScreen = lazy(() => import('../pages/administrativo/PacientesScreen.jsx'));
const NuevoPacienteScreen = lazy(() => import('../pages/administrativo/NuevoPacienteScreen.jsx'));
const PacienteDetailScreen = lazy(() => import('../pages/administrativo/PacienteDetailScreen.jsx'));
const CensoScreen = lazy(() => import('../pages/administrativo/CensoScreen.jsx'));
const CorteCajaScreen = lazy(() => import('../pages/administrativo/CorteCajaScreen.jsx'));

// Spark y Analítica
const SparkDashboard = lazy(() => import('../pages/spark/SparkDashboard.jsx'));
const AnalyticsScreen = lazy(() => import('../pages/spark/AnalyticsScreen.jsx'));
const MetAnalyticsScreen = lazy(() => import('../pages/spark/MetAnalyticsScreen.jsx'));
const ClinicalAnalyticsScreen = lazy(() => import('../pages/spark/ClinicalAnalyticsScreen.jsx'));
const UnsupervisedAnalyticsScreen = lazy(() => import('../pages/spark/UnsupervisedAnalyticsScreen.jsx'));

// Componente para pantalla de carga entre transiciones de rutas
const PageLoader = () => {
  const { t } = useTranslation();
  return <div className="loading-screen">{t('common.loading')}</div>;
};

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
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={<PublicLoginRoute />} />

        <Route
          path="/*"
          element={
            <PrivateRoute>
              <MainLayout>
                <Suspense fallback={<PageLoader />}>
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
                </Suspense>
              </MainLayout>
            </PrivateRoute>
          }
        />
      </Routes>
    </Suspense>
  );
}