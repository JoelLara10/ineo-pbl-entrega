# Componentes — INEO

## Objetivo
Los componentes de INEO deben ser reutilizables, consistentes, accesibles y adaptables a las diferentes áreas del sistema clínico. El repositorio actualmente separa componentes en categorías como `cards`, `common` y `layout`, además de formularios y paginación. 

## Botones

### Primario
Se utiliza para la acción principal de una pantalla: Guardar, Registrar, Continuar o Confirmar.

### Secundario
Se utiliza para acciones complementarias: Cancelar, Volver o consultar información.

### Éxito
Se utiliza para confirmar operaciones completadas correctamente.

### Peligro
Se utiliza para acciones destructivas, como eliminar registros.

### Enlace
Se utiliza para navegación contextual, por ejemplo "Ver más".

## Formularios
Los campos deben incluir:
- Etiqueta visible.
- Área de interacción claramente delimitada.
- Placeholder únicamente como apoyo, no como sustituto de la etiqueta.
- Estados normal, foco, error, deshabilitado y correcto.
- Mensajes de validación próximos al campo correspondiente.

Componentes previstos: campo de texto, selector, fecha, checkbox y radio button.

## Tarjetas
Las tarjetas agrupan información relacionada, como indicadores del dashboard, datos de pacientes, estudios y resúmenes. Deben utilizar fondo blanco, borde sutil, esquinas redondeadas y separación suficiente entre contenidos.

## Tablas
Las tablas se emplean para información clínica y administrativa que requiere comparación de registros. Deben incluir encabezados claros, filas legibles, acciones identificables y desplazamiento horizontal cuando el ancho disponible sea insuficiente.

## Navegación
La navegación principal se organiza mediante un menú lateral en escritorio y un menú colapsable en dispositivos pequeños. Las opciones deben depender del rol del usuario y mostrar visualmente la sección activa.

Los módulos principales del sistema incluyen:
- Dashboard
- Pacientes
- Médico
- Enfermería
- Estudios
- Administrativo
- Configuración

## Estados
Los componentes deben contemplar estados de carga, vacío, éxito, advertencia y error.

## Accesibilidad
- Los elementos interactivos deben ser accesibles mediante teclado.
- El foco debe ser visible.
- Los iconos deben acompañarse de texto cuando su significado no sea evidente.
- No depender exclusivamente del color para transmitir información.
