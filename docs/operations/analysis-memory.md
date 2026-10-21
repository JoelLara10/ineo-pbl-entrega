# Análisis en instancias pequeñas de OftalCore

La API comparte la RAM del contenedor con sus procesos hijos. El límite de una JVM no representa el consumo total de Spark: también existen procesos Python, memoria nativa y la API.

`ANALYSIS_ENGINE=auto` (valor predeterminado) consulta los límites cgroup v2/v1 del contenedor. Si hay menos de 2 GiB de RAM total o menos de 1.5 GiB libres, ejecuta los análisis en un subproceso de bajo consumo. Si Render no expone el límite, selecciona la alternativa conservadora. Este motor usa agregaciones Python y, para patrones, NumPy con K-means, PCA y silueta de distancia euclidiana al cuadrado; no crea una JVM ni matrices de distancias N×N. Mantiene el máximo de 20,000 filas, exclusiones, unidades y el contrato de las gráficas. No inventa datos. Los grupos pueden cambiar respecto a Spark por la inicialización de los centroides; `engine` identifica la implementación usada en cada resultado.

`ANALYSIS_ENGINE=lightweight` permite fijar el modo de bajo consumo. `ANALYSIS_ENGINE=spark` exige la comprobación de memoria; un entorno insuficiente devuelve un error recuperable antes de lanzar Java. No se usa `spark.testing.memory` para saltar validaciones. Para un requisito académico que exija Spark, se conserva su ejecución y sus pruebas reales en CI; en producción puede ejecutarse en un trabajador separado con recursos suficientes.

Los subprocesos usan un solo hilo de BLAS. Spark recibe un heap de driver de 512 MiB antes del inicio de Java y un máximo de resultados de 32 MiB. El monitor cancela el grupo completo del análisis si se acerca al límite del contenedor o vence el tiempo; el resultado anterior se conserva. No garantiza que otras cargas independientes no agoten la RAM del servidor.

Tras desplegar `qa`, verificar en Render que el servicio cargó el commit nuevo y ejecutar Analítica clínica. El resultado debe identificar el motor de bajo consumo cuando la instancia sea pequeña. Revisar que la RAM no alcance el límite y que la API siga respondiendo durante el cálculo. No se cambia el plan de Render ni se generan cargos desde el código.

Validación automatizada: resultados clínicos con valores parciales, detección del cgroup, cancelación por presión de memoria, conservación del último resultado, los cuatro motores por subproceso, silueta contrastada con cálculo exhaustivo sobre una muestra pequeña y 20,000 observaciones bajo un límite de espacio de direcciones de 256 MiB para clínica y patrones. Este límite de proceso no sustituye una medición del contenedor completo en Render.
