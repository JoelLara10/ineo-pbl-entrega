# OftalCore — Interpretación de indicadores y decisión

**Módulo:** Administración / Analytics.  
**Escenario:** Interpretar indicadores y tomar una decisión.  
**Precondición:** Usuario de Administración autenticado; indicadores conocidos cargados o disponibles.  
**Datos:** periodo, unidad, conteos y valores de referencia conocidos. Utilizar datos sintéticos en QA.

| Paso | Acción del usuario | Resultado esperado | Soporte en el sistema |
|---|---|---|---|
| 1 | Iniciar sesión con credenciales de Administración | Acceso concedido; Analytics visible | Control de acceso para `admin` y `administrativo`; otros roles sin acceso a resultados, opciones o evaluaciones |
| 2 | Abrir la vista correspondiente | Gráficas y KPIs visibles | General, Actividad diaria, Clínica y Patrones; estados de ejecución, vacío y error diferenciados |
| 3 | Identificar el periodo representado | El usuario indica el periodo correctamente | Periodo del resultado guardado y filtros aplicados; un cambio en el formulario no relabela el resultado anterior |
| 4 | Identificar la unidad | El usuario indica la unidad correctamente | Unidades visibles en tarjetas, gráficas, tablas y exportaciones; señales clínicas con unidades separadas |
| 5 | Explicar el significado | Explicación coherente con los datos | Guía de lectura, referencia al periodo previo o al promedio general, observaciones válidas y exclusiones; el participante explica los datos al evaluador |
| 6 | Formular una conclusión o decisión | Conclusión lógica y accionable | Pistas de revisión por apartado; la conclusión/acción y el dato que la respalda se registran en la documentación UAT |
| 7 | Calificar claridad | Calificación cualitativa de textos, leyendas y diseño | El evaluador registra Clara, Aceptable o Confusa y los comentarios en la documentación UAT; no hay formulario de evaluación en los cuatro análisis |

## Conjunto conocido para ejecutar el escenario

La semilla automatizada contiene ocho atenciones con ingreso del 1 al 8 de enero de 2026. En Actividad diaria, seleccionar del **5 al 10 de enero de 2026** y comparar con el periodo anterior:

- Periodo seleccionado: seis días calendario, cuatro ingresos.
- Referencia: del 30 de diciembre de 2025 al 4 de enero de 2026, también seis días, cuatro ingresos.
- Cambio: cero atenciones, 0 %.
- Promedio del periodo seleccionado: 4/6 atenciones por día, incluidos los días 9 y 10 con cero ingresos.
- Si se selecciona un área, mantenerla en los dos periodos. La semilla usa `PRUEBA`.

Ejemplo de interpretación esperada: «Del 5 al 10 de enero hubo cuatro ingresos, el mismo conteo que en los seis días anteriores. El promedio fue de 0.67 ingresos por día calendario». Una posible decisión es revisar la distribución por fechas y áreas antes de ajustar recursos; la igualdad del total no demuestra igualdad de la carga diaria.

Para clínica, la semilla tiene ocho mediciones de frecuencia cardiaca con promedio 82.5 lpm, mínimo 65 y máximo 100. Las fechas clínicas deben cargarse explícitamente para las pruebas por periodo: la semilla original carece de fecha de registro de signos vitales. Los rangos observados describen el conjunto; no son límites clínicos recomendados. Para Patrones, comprobar conteos y medias contra la respuesta del análisis y la referencia general ponderada por el tamaño de cada grupo.

## Evidencia y criterio de aceptación

El compañero responsable de la documentación registra la interpretación, la decisión y la calificación real de claridad del participante, junto con el tipo de análisis, fecha del resultado, periodo, filtros, unidades y referencias. Esta evaluación se realiza fuera de la aplicación.

Capturar la vista con periodo/unidad/referencias y registrar las respuestas y observaciones en el documento de pruebas. Las pruebas automatizadas verifican acceso, filtros, cálculos y descargas; **no sustituyen la prueba con una persona ni demuestran que el diseño sea claro**.

**Estado de aceptación humana: pendiente de ejecución con usuario de Administración.** Registrar fecha, participante, resultado por paso y observaciones durante la sesión UAT. No rellenar calificaciones por adelantado.

## Alcance de filtros y referencias

Las fechas filtran ingresos de atenciones o registros de signos vitales en UTC y son inclusivas. El comparativo usa el periodo inmediatamente anterior de igual duración. Las áreas se resuelven con el área actualmente registrada en la atención. El catálogo de pacientes es global; camas y estados de estudios son una captura actual, no históricos reconstruidos. Estos límites aparecen en la guía de la vista.

Las descargas PNG/SVG y CSV se generan en el navegador a partir del resultado guardado para evitar trabajo adicional en Render. Las filas incompletas, fechas inválidas y ausencia de base porcentual se indican explícitamente. Se conserva el límite de fuente de 20,000 filas y la selección automática del motor de bajo consumo.
