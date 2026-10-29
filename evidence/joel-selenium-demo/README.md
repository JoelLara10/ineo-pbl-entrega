# Selenium integrado en Jenkins
Fecha local: 28/10/2026 (America/Mexico_City).
Build 7: SUCCESS, 88 aprobadas, 0 fallos, 0 omitidas.
Fuente ejecutada: 6911037542b4e6da62885f05e346818a4bec74b5.
Desglose: 63 API + 7 componentes web + 10 OAT + 7 recorridos Selenium + 1 control.

Selenium usó Chrome visible y un navegador limpio por caso. React y Flask reales
se comunicaron por HTTP en puertos locales temporales; Mongo fue simulado con
datos sintéticos. No se prueba el despliegue publicado ni la persistencia de una
base externa. Los procesos temporales se cerraron al terminar.

Los siete casos verifican acceso privado, contraseña inválida, navegación de
enfermería, guardado y consulta tras recarga, dolor fuera de rango, error de
conexión con reintento y bloqueo clínico offline con reconexión.
Las nueve capturas son siete resultados finales y dos estados intermedios
(error de conexión y modo offline).

selenium.xml y junit.json proceden de la ejecución real de Jenkins; console.txt
contiene comandos y resultados. screenshots contiene PNG y resumen JSON por caso.
La aprobación técnica no sustituye aceptación humana UAT. Acciones manuales en
otra sesión no se registran automáticamente en Jenkins.
Ver ci/README-Jenkins.md para repetir la prueba con MOSTRAR_NAVEGADOR.
