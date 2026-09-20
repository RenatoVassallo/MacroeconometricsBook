# Notas de implementación del sistema Warm Folio

Qué se implementó, qué se cambió respecto del handoff y por qué. El handoff
original (`HANDOFF.md`, `README.md`, `tokens.json`, `mockups/`) queda tal como
llegó; esto es el registro de la traducción a Quarto.

## Dónde vive cada cosa

| Pieza del sistema | Archivo |
|:------------------|:--------|
| Colores, tipografía, escalas, reglas HTML | `styles/book.scss` |
| Preámbulo LaTeX (bloques, encabezados, márgenes) | `styles/book.tex` |
| Estilo de las figuras | `styles/matplotlib.mplstyle` |
| Tema de resaltado de código | `styles/warmfolio.theme` |
| Bloques sin numeración y soluciones plegables | `filters/blocks.lua` |
| Paletas y ayudas de gráficos en Python | `code/python/macrolibro/` |
| Tipografías (SIL OFL) | `styles/fonts/` |

## Cambios respecto del handoff

1. **Paleta de rellenos para gráficos apilados.** Los seis colores de choque de
   `tokens.json` no pasan la prueba de separación para daltonismo cuando dos
   rellenos se tocan: oliva `#5A7D43` y terracota `#B0472A` quedan a ΔE 3.2 en
   deuteranopía, y oro `#9A7B2E` con oliva a ΔE 9.3 en visión normal (umbral
   15). En una descomposición histórica o de varianza el color es lo único que
   separa una serie de otra, así que las apiladas usan
   `PALETA["rellenos"] = ["#2F7CA8", "#C4522A", "#BE8C1F", "#2E8B62", "#8E5AA6", "#9A9086"]`,
   que sí pasa (peor par adyacente ΔE 9.0 en deuteranopía), más separación
   blanca de 0.5 pt entre segmentos y leyenda siempre visible. Los seis colores
   originales se conservan para series de línea, donde el estilo de línea y el
   marcador aportan la segunda señal.
2. **Bloques numerados sobre los entornos de Quarto.** No existe un tipo de
   referencia cruzada propio para "Supuesto", así que se reutiliza el entorno
   `cnj` (conjetura) retitulado, y "Algoritmo" se define como flotante propio
   (`crossref.custom`). Así funcionan las referencias entre capítulos, que un
   filtro propio no podría resolver.
3. **Matemática en HTML.** El handoff supone KaTeX; Quarto usa MathJax por
   defecto y así se dejó (soporta mejor `\operatorname` y los entornos `cases`).
   La consecuencia es que en la web la matemática sale con las tipografías de
   MathJax y no con Garamond-Math, que sí se usa en el PDF.
4. **Algoritmo en PDF.** Es un flotante con estilo `ruled` (filete arriba y
   abajo) en lugar del fondo tenue con filete doble a la izquierda que tiene en
   la web: tcolorbox no puede envolver un flotante sin romper su colocación.
5. **`axes.titlesize: 0`** del handoff no se incluyó (matplotlib no admite 0);
   la regla "sin títulos dentro de los ejes" se mantiene por convención y se
   revisa a ojo.
6. **Pestañas de código.** Los títulos van en nivel 4 (`####`): con
   `number-depth: 2` salen en el PDF como etiqueta corrida y no como sección.

7. **Tema de resaltado de código.** El handoff no fija los colores de cada
   token más allá de la tabla de `code_tokens`. La primera versión ponía las
   palabras clave en terracota, que competía con los enlaces y las etiquetas de
   bloque. La versión actual deja las palabras clave en tinta (peso, no color),
   los nombres de función en azul acero, las cadenas en oliva y los números en
   terracota oscuro. Alternativas en `styles/warmfolio-minimo.theme` y
   `styles/warmfolio-azul.theme`.
8. **Tamaño del código.** 12 px en web (0.75 rem) y `Scale=0.80` de la mono en
   el PDF: JetBrains Mono tiene una altura de x mucho mayor que EB Garamond, así
   que al mismo tamaño nominal el código se ve más grande que el texto.
9. **Portada.** Implementada en TikZ dentro de `styles/book.tex` (motivo de tres
   densidades, versión de septiembre de 2026). El mismo motivo va como SVG en
   la portada web.

## Pendiente

- Tarjeta social y favicon: están diseñados en los mockups, falta producirlos.
- Tema oscuro: no se enviará (véase §6.8 del handoff).
- Revisar el ancho de las figuras al ancho de columna en pantallas grandes.
