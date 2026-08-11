# Criterios Responsive — INEO

## Objetivo
La interfaz de INEO debe adaptarse a diferentes tamaños de pantalla manteniendo legibilidad, funcionalidad y facilidad de navegación. El diseño parte de un enfoque **mobile-first** y escala progresivamente hacia tabletas y escritorio.

## Puntos de quiebre

| Dispositivo | Ancho | Descripción |
|---|---:|---|
| Móvil | `< 768 px` | Smartphones en orientación vertical y horizontal |
| Tablet | `768–1024 px` | Tabletas y pantallas intermedias |
| Escritorio | `> 1024 px` | Laptops, monitores y pantallas grandes |

## Criterios generales

1. **Mobile-first:** primero se garantiza una experiencia funcional en pantallas pequeñas.
2. **Navegación adaptable:** el menú lateral se colapsa o transforma en menú desplegable en móviles.
3. **Contenido flexible:** tarjetas y paneles deben pasar de varias columnas a una columna cuando sea necesario.
4. **Tablas:** cuando una tabla no pueda comprimirse sin perder información, se debe permitir desplazamiento horizontal.
5. **Formularios:** los campos deben ocupar el ancho disponible y evitar controles demasiado pequeños.
6. **Tipografía:** los tamaños de títulos se reducen en pantallas pequeñas para mantener proporción y legibilidad.
7. **Imágenes y gráficos:** deben utilizar dimensiones fluidas y no superar el ancho de su contenedor.
8. **Espaciado:** utilizar unidades relativas y espaciado consistente.
9. **Interacción táctil:** los controles interactivos deben contar con un área de interacción cómoda.
10. **Accesibilidad:** mantener contraste, foco visible, lectura clara y navegación por teclado.

## Comportamiento esperado

### Móvil
- Sidebar oculto por defecto.
- Menú accesible mediante botón.
- Tarjetas en una sola columna.
- Formularios en una columna.
- Tablas con desplazamiento horizontal.
- Acciones principales visibles sin saturar la pantalla.

### Tablet
- Sidebar reducido o colapsable.
- Tarjetas en dos columnas cuando el espacio lo permita.
- Formularios de una o dos columnas según el contenido.

### Escritorio
- Sidebar visible.
- Dashboard con tarjetas e información distribuida en varias columnas.
- Tablas y formularios pueden utilizar el ancho disponible.
- Mantener un ancho máximo de contenido para evitar líneas de texto excesivamente largas.

## Validación
Las pantallas deben probarse al menos en 360 px, 768 px, 1024 px y 1280 px de ancho para verificar que no exista desbordamiento horizontal ni pérdida de funcionalidad.
