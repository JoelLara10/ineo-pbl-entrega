# Evidencia de Jenkins de Joel
Fecha: 28/10/2026 (America/Mexico_City).
Fuente ejecutada: 193e33868d0af71c1133ea45675fd7dcdea1e4f8.
Rama: feature/joel-sprint4-jenkins-oat.

## Resultados verificables
- Build 6: SUCCESS, 81 aprobadas, 0 fallos, 0 omitidas. Iniciado desde la interfaz de Jenkins.
- Build 5: FAILURE esperado, 80 aprobadas y 1 fallo deliberado en ci.test_gate_demo.
  El log confirma que la etapa de promoción fue omitida. No existe promotion.txt en ese build.
- Build 4: primer ensayo completo aprobado; utilizó el árbol de trabajo previo al commit.
- Builds 1–3: fallos de preparación de Windows (ruta, parámetros y temporales), conservados en el historial para transparencia.

Las 81 comprobaciones son 63 regresiones API, 7 de interfaz, 10 operativas y
1 control del pipeline. No son 81 casos UAT ni 81 casos nuevos: se reutilizan pruebas previas.
Los XML de builds 5/6, logs, JSON de Jenkins y hashes permiten revisar los resultados
sin tener Jenkins encendido. Las capturas provienen de Jenkins real.
La captura jenkins-etapas.png y jenkins-en-ejecucion.png se tomaron durante la ejecución;
jenkins-81-aprobadas.png muestra el resultado final.

La aceptación humana UAT, Terraform y OAT con Mongo/Docker reales siguen pendientes.
Ver ci/README-Jenkins.md para alcance, comandos y procedimiento del profesor.
