# Validación automática de Jesús del 8 de octubre de 2026

Commit revisado: `f3c76029ada836586fcea4a390668e06dc47bef5` (main).

Instalación: `npm ci` completada. Resultados: 14 archivos y 76 pruebas aprobadas; idiomas, lint y compilación aprobados. No se repitieron las pruebas del backend ni una sesión de aceptación humana. Las capturas históricas no se utilizan como evidencia de esta ejecución.

## npm run check:i18n

Código de salida: 0.

```text
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> ineo-web@0.0.0 check:i18n
> node scripts/check-i18n-keys.mjs

i18n OK: todas las claves estáticas usadas existen en es.json y en.json.
```

## npm test

Código de salida: 0.

```text
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> ineo-web@0.0.0 test
> vitest run


 RUN  v4.1.10 /workspace/scratch/9af03ed3b3c9/ineo-review/frontend/clinica-web-react


 Test Files  14 passed (14)
      Tests  76 passed (76)
   Start at  18:13:14
   Duration  2.59s (transform 1.06s, setup 0ms, import 2.31s, tests 3.19s, environment 2.87s)

```

## npm run lint

Código de salida: 0.

```text
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> ineo-web@0.0.0 lint
> oxlint

```

## npm run build

Código de salida: 0.

```text
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> ineo-web@0.0.0 build
> vite build

vite v8.1.3 building client environment for production...
[2K
transforming...✓ 178 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                                         0.45 kB │ gzip:   0.29 kB
dist/assets/BackupStyles-B9tW3XSj.css                   0.80 kB │ gzip:   0.42 kB
dist/assets/EstudiosScreen-DeV_Ag6f.css                 0.92 kB │ gzip:   0.37 kB
dist/assets/MetAnalyticsScreen-DFDnBz48.css             1.45 kB │ gzip:   0.58 kB
dist/assets/LoginScreen-DcwcM3ph.css                    2.08 kB │ gzip:   0.78 kB
dist/assets/DashboardScreen-TJr2iOHJ.css                2.22 kB │ gzip:   0.86 kB
dist/assets/EnfermeriaCareScreen-DuC9n4gq.css           3.56 kB │ gzip:   1.05 kB
dist/assets/index-Q7STvVPo.css                          4.00 kB │ gzip:   1.49 kB
dist/assets/AdminLayout-DzVzvAn-.css                    4.36 kB │ gzip:   1.42 kB
dist/assets/Spark-BFv3DDwB.css                          4.66 kB │ gzip:   1.36 kB
dist/assets/ConfigHeader-BwB5Zb7W.css                   8.10 kB │ gzip:   2.20 kB
dist/assets/EditarResultadoGabScreen-DJr9gjgC.js        0.16 kB │ gzip:   0.15 kB
dist/assets/EditarResultadoLabScreen-DJr9gjgC.js        0.16 kB │ gzip:   0.15 kB
dist/assets/VerResultadoGabScreen-DGPUJjIt.js           0.16 kB │ gzip:   0.15 kB
dist/assets/VerResultadoLabScreen-DGPUJjIt.js           0.16 kB │ gzip:   0.15 kB
dist/assets/ClinicalAnalyticsScreen-quuR9iDU.js         0.17 kB │ gzip:   0.16 kB
dist/assets/UnsupervisedAnalyticsScreen-z-UVnlqJ.js     0.17 kB │ gzip:   0.16 kB
dist/assets/Spark-CYjEpWF_.js                           0.48 kB │ gzip:   0.28 kB
dist/assets/ConfigHeader-B8eYzKjX.js                    0.50 kB │ gzip:   0.29 kB
dist/assets/EstudiosCache-BlJcoKWf.js                   0.51 kB │ gzip:   0.31 kB
dist/assets/configCache-BNeWtphW.js                     0.78 kB │ gzip:   0.38 kB
dist/assets/BackupStyles-CpLQQ-Zy.js                    0.83 kB │ gzip:   0.37 kB
dist/assets/useAdminData-CQRCVASY.js                    0.90 kB │ gzip:   0.53 kB
dist/assets/AdminLayout-B8FvcIcz.js                     0.93 kB │ gzip:   0.45 kB
dist/assets/AdminScreen-CKhJafhV.js                     0.94 kB │ gzip:   0.53 kB
dist/assets/regional-Cr_cz2zb.js                        0.95 kB │ gzip:   0.45 kB
dist/assets/ProfileConfigScreen-TyCBoHRe.js             1.31 kB │ gzip:   0.46 kB
dist/assets/SparkDashboard-DW7E-Yql.js                  1.71 kB │ gzip:   0.68 kB
dist/assets/adminService-JjOfuHpr.js                    1.78 kB │ gzip:   0.81 kB
dist/assets/ConfigScreen-CtQGjvp0.js                    1.84 kB │ gzip:   0.69 kB
dist/assets/md-Z1ocDe0k.js                              2.05 kB │ gzip:   0.73 kB
dist/assets/LoginScreen-udBTmT5O.js                     2.39 kB │ gzip:   0.86 kB
dist/assets/AnalyticsScreen-CDeOpWbP.js                 2.73 kB │ gzip:   1.07 kB
dist/assets/CensoScreen-BcZPY6Og.js                     3.21 kB │ gzip:   1.15 kB
dist/assets/GeneralSettingsScreen-CpwO7eBy.js           3.53 kB │ gzip:   0.94 kB
dist/assets/PacientesScreen-C-f0gNLP.js                 4.12 kB │ gzip:   1.47 kB
dist/assets/AutomationConfigScreen-DuGnzsj4.js          4.31 kB │ gzip:   1.30 kB
dist/assets/MetAnalyticsScreen-D85VhHG6.js              4.32 kB │ gzip:   1.39 kB
dist/assets/DiagnosticosConfigScreen-B6jS55o8.js        4.60 kB │ gzip:   1.47 kB
dist/assets/CorteCajaScreen-QhtrZvJ5.js                 4.87 kB │ gzip:   1.42 kB
dist/assets/NuevoPacienteScreen-B7q14_fj.js             5.79 kB │ gzip:   1.78 kB
dist/assets/EnfermeriaCareScreen-BHfqlevJ.js            5.90 kB │ gzip:   1.64 kB
dist/assets/SparkAnalysisScreen-nF4aQqhv.js             5.94 kB │ gzip:   1.88 kB
dist/assets/BackupConfigScreen-CEWiOjph.js              6.30 kB │ gzip:   1.96 kB
dist/assets/EnfermeriaFluidBalanceScreen-_bgTSx3i.js    7.11 kB │ gzip:   2.18 kB
dist/assets/CamasConfigScreen-DU4RbR7G.js               7.56 kB │ gzip:   2.05 kB
dist/assets/VitalSignsListScreen-DFwEKmql.js            7.58 kB │ gzip:   2.37 kB
dist/assets/ViewResultForm-xpED2bkq.js                  7.88 kB │ gzip:   2.50 kB
dist/assets/DashboardScreen-BvWNKK-H.js                 8.20 kB │ gzip:   3.16 kB
dist/assets/PacienteDetailScreen-D5qOXOG7.js            8.46 kB │ gzip:   2.39 kB
dist/assets/EnfermeriaNoteScreen-CD0T0uvK.js            8.71 kB │ gzip:   2.71 kB
dist/assets/MedicoScreen-CxtE7dZ0.js                    8.76 kB │ gzip:   2.91 kB
dist/assets/EnfermeriaScreen--RaM9-4f.js                8.85 kB │ gzip:   2.98 kB
dist/assets/SubirResultadoScreen-D12U6V0r.js            8.85 kB │ gzip:   3.13 kB
dist/assets/ServiciosConfigScreen-BT7XIawD.js           9.23 kB │ gzip:   2.47 kB
dist/assets/EditResultForm-uz6dma2z.js                  9.36 kB │ gzip:   3.19 kB
dist/assets/HistoriaClinicaScreen-y5fRvDOu.js           9.42 kB │ gzip:   2.92 kB
dist/assets/UsuariosConfigScreen-CAr_n5ed.js            9.44 kB │ gzip:   2.25 kB
dist/assets/MedicalNoteScreen-96Sqzmro.js               9.81 kB │ gzip:   2.96 kB
dist/assets/EnfermeriaVitalSignsScreen-C2ehxC1h.js     10.12 kB │ gzip:   3.09 kB
dist/assets/EnfermeriaAssessmentScreen-Cp70Ux41.js     10.12 kB │ gzip:   2.88 kB
dist/assets/PatientDetailScreen-DTt-W8gx.js            10.20 kB │ gzip:   3.21 kB
dist/assets/VitalSignsScreen-D36YpNCk.js               10.29 kB │ gzip:   3.06 kB
dist/assets/PatientDetailScreen-DRAXTJ1I.js            10.61 kB │ gzip:   3.28 kB
dist/assets/PrintDocsScreen-CmLHg8BD.js                10.70 kB │ gzip:   3.38 kB
dist/assets/LabExamsScreen-BFv0R2w6.js                 11.01 kB │ gzip:   3.25 kB
dist/assets/ImagingExamsScreen-DAaoxHga.js             11.11 kB │ gzip:   3.24 kB
dist/assets/StudyResultsScreen-CiXV_vzU.js             11.60 kB │ gzip:   3.30 kB
dist/assets/EnfermeriaMedicationsScreen-BUMhIs2D.js    12.07 kB │ gzip:   3.33 kB
dist/assets/DiagnosisScreen-BeF-Eqfe.js                12.44 kB │ gzip:   3.23 kB
dist/assets/PrescriptionScreen-DWUZ8g0j.js             12.94 kB │ gzip:   3.43 kB
dist/assets/EstudiosScreen-CUz5_p2E.js                 16.20 kB │ gzip:   5.22 kB
dist/assets/index-Bu5-VAg1.js                         447.37 kB │ gzip: 138.60 kB

✓ built in 743ms
```
