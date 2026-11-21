# Copia local protegida de picomatch

Se conservó el código y la licencia MIT de picomatch 4.0.7 instalado desde npm.
Se identifica como fork privado @ineo/picomatch-guarded 4.0.7-ineo.1, con
upstream picomatch@4.0.7 explícito. No es una versión oficial de picomatch. El proveedor
todavía no publica una versión corregida para GHSA-fc5q-39xc-vjpf al revisar
el 18 de noviembre de 2026.

La modificación local en analyzeRepeatedExtglob rechaza mediante la ruta de
literalización ya existente los grupos repetidos que contienen * o ?, incluso
cuando tienen una sola alternativa. Así los patrones +(*) y +(*a) no producen
cuantificadores anidados vulnerables. Es una restricción deliberada de semántica:
esos extglobs se interpretan literalmente. Los patrones corrientes del proyecto
se verifican mediante tests, build y la suite web completa.

El override de npm hace que Vite, Vitest, tinyglobby y fdir usen esta misma copia.
Se reemplazó además removeBackslashes por un recorrido lineal: la expresión
regular original presentaba coste cuadrático con corchetes sin cierre,
señalado por CodeQL como js/polynomial-redos. Las pruebas comparan la
semántica de escapes y clases con la implementación original y limitan el
tiempo de ejecución sobre entradas adversas grandes.
Un resultado npm audit sin alertas en dependencias publicadas no audita este
código local. Su verificación se encuentra en scripts/tests/glob-security.cjs,
el diff del parser y las pruebas de compatibilidad; no sustituye la revisión
de Jesús. Al aparecer una versión oficial corregida, retirar la copia y el
override tras repetir estas pruebas.

Fuente: https://github.com/micromatch/picomatch/tree/4.0.7
Aviso: https://github.com/advisories/GHSA-fc5q-39xc-vjpf

