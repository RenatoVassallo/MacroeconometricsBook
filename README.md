# Macroeconometría aplicada con Python

Libro de posgrado sobre macroeconometría aplicada, escrito en Quarto con Python.
Se publica en dos formatos desde la misma fuente: un libro web (HTML) y un PDF
compuesto con LuaLaTeX.

**Se lee en <https://renatovassallo.github.io/MacroeconometricsBook/>.** Primera
edición en preparación: los capítulos aparecen a medida que quedan listos y cada
push a `main` recompila y vuelve a publicar el sitio.

## Cómo compilarlo

El entorno se maneja con [uv](https://docs.astral.sh/uv/). Todo está declarado
en `pyproject.toml` y fijado en `uv.lock`.

```bash
# 1. Entorno (uv descarga Python 3.11 si hace falta)
uv sync

# 2. Libro web
uv run quarto preview

# 3. PDF
uv run quarto render --to pdf
```

`uv run` antepone `.venv/bin` al PATH, así que Quarto arranca el kernel de
Python del proyecto. Si prefieres activar el entorno a mano, `source
.venv/bin/activate` y después `quarto preview` a secas.

Para el PDF hace falta una distribución de LaTeX. Si no hay ninguna:
`quarto install tinytex`. Las tipografías del libro están en `styles/fonts/`
(todas con licencia SIL OFL), así que no hay que instalar nada más.

### Quarto y Python tienen que vivir en la misma máquina

Quarto arranca él mismo el kernel de Jupyter, así que no se puede tener Quarto
en el Mac y el entorno de Python en un contenedor: el `.venv` de Linux no
sirve para el Quarto del Mac y viceversa. Hay que elegir uno de los dos:

- **Todo en el Mac** (lo más simple si Quarto ya está instalado ahí): `uv sync`
  y `uv run quarto preview`. uv descarga Python 3.11 si no está.
- **Todo en el contenedor**: instalar Quarto dentro de la imagen con
  `bash scripts/instalar-quarto.sh`, publicar el puerto (`-p 4200:4200`) y
  levantar el preview con
  `uv run quarto preview --host 0.0.0.0 --port 4200 --no-browser`.
  Si el contenedor no tiene el puerto publicado, sirve igual
  `uv run quarto render --to html` y abrir `_book/index.html` desde el Finder,
  porque la carpeta está compartida.

  Para que la instalación sobreviva a la reconstrucción de la imagen, en el
  `Dockerfile`:

  ```dockerfile
  ARG QUARTO_VERSION=1.11.5
  RUN ARCH=$(dpkg --print-architecture) && \
      curl -fsSL "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-${ARCH}.tar.gz" \
      | tar -xz -C /opt && ln -s /opt/quarto-${QUARTO_VERSION}/bin/quarto /usr/local/bin/quarto
  ```

Si se usan las dos, conviene que cada una tenga su entorno y que el del
contenedor no caiga dentro de la carpeta compartida:

```bash
# dentro del contenedor
export UV_PROJECT_ENVIRONMENT=/opt/venv-libro
uv sync
```

## Estructura

```
_quarto.yml            configuración del libro (formatos, referencias cruzadas, filtros)
index.qmd              presentación
prefacio.qmd           prefacio
chapters/              los once capítulos
appendices/            notación y repaso bayesiano
references.bib         bibliografía
pyproject.toml         entorno y dependencias (uv); incluye el paquete `macrobook`
uv.lock                versiones exactas de todo el entorno
code/python/           paquete `macrobook`: estilo, paletas, gráficos, VAR, SVAR, BVAR, rutas de datos
data/raw/              datos tal como se descargan (no se editan nunca)
data/processed/        series construidas por los scripts y capítulos
figures/generated/     figuras producidas por scripts (las de capítulo las escribe Quarto)
figures/external/      figuras que no produce el libro
styles/                book.scss, book.tex, matplotlib.mplstyle, tipografías, sistema de diseño
filters/blocks.lua     bloques de contenido (intuición, cuidado, solución, apertura de capítulo)
scripts/               utilidades del repositorio (instalación de Quarto en Linux)
archive/               material de clases previo, fuera de Git (temporal)
```

## Bloques de contenido

El libro usa ocho bloques. Los numerados son entornos de Quarto con referencia
cruzada; los demás son divs con clase:

| Bloque | Cómo se escribe | Referencia |
|:-------|:----------------|:-----------|
| Supuesto | `::: {#cnj-nombre}` + título `## ...` | `@cnj-nombre` |
| Definición | `::: {#def-nombre}` | `@def-nombre` |
| Resultado | `::: {#thm-nombre}` (o `prp-`, `lem-`, `cor-`) | `@thm-nombre` |
| Algoritmo | `::: {#alg-nombre}` con la leyenda como último párrafo | `@alg-nombre` |
| Ejemplo | `::: {#exm-nombre}` | `@exm-nombre` |
| Ejercicio | `::: {#exr-nombre}` | `@exr-nombre` |
| Intuición | `::: {.intuicion}` | sin referencia |
| Cuidado | `::: {.cuidado}` | sin referencia |

Las soluciones van en `::: {.solucion}` justo después del ejercicio: en la web
aparecen plegadas y en el PDF impresas. Para ocultarlas por completo, poner
`mostrar-soluciones: false` en `_quarto.yml`.

En las pestañas de código (`::: {.panel-tabset}`) los títulos van con `####`,
para que en el PDF salgan como etiqueta y no como sección del libro.

## Resaltado de código

El tema por defecto es `styles/warmfolio.theme`. Hay dos alternativas listas:

| Tema | Aspecto |
|:-----|:--------|
| `warmfolio.theme` | palabras clave en tinta, nombres de función en azul acero, cadenas en oliva, números en terracota |
| `warmfolio-minimo.theme` | casi monocromo: sólo cadenas y comentarios salen del gris |
| `warmfolio-azul.theme` | palabras clave en azul acero, al estilo de un editor |

Para cambiarlo, edita `highlight-style` en `_quarto.yml`.

## Figuras

Todas las figuras usan `styles/matplotlib.mplstyle`. En cada capítulo:

```python
from macrobook import use_style, PALETTE, charts
use_style()
```

`use_style()` registra las tipografías, aplica la hoja de estilo y neutraliza
el estilo propio de MacroPy, que de otro modo lo sobrescribiría en cada llamada
a sus funciones de dibujo.

Las figuras **nunca fijan el ancho**. Quarto define `figure.figsize` por formato
(7 pulgadas en la web, 4.5 en el PDF, que es el ancho del bloque de texto) y los
capítulos llaman a `figsize(ratio)`, que devuelve `(ancho, ratio * ancho)`. Así
el mismo código produce una figura con el tipo al mismo tamaño en los dos medios.

`macrobook.var` reúne la mecánica del VAR clásico (rezagos, MCO, forma companion,
raíces, pesos de Wold, pronóstico, simulación); `macrobook.svar`, la
identificación, las respuestas al impulso, la FEVD, la descomposición histórica,
las bandas bootstrap y las proyecciones locales; `macrobook.bvar`, el prior de
Minnesota, el muestreador de Gibbs y la densidad predictiva. Todo el código del
libro está escrito en inglés; la prosa y las etiquetas, en español.

## Publicación

`.github/workflows/publish.yml` compila el libro en cada push a `main` y lo
despliega en GitHub Pages. El flujo instala Quarto con TinyTeX, crea el entorno
con `uv sync --frozen` y ejecuta un único `uv run quarto render`, que produce las
dos versiones. Nota: `quarto render --to <formato>` limpia `_book`, así que no
sirve renderizar los dos formatos en pasos separados.

`_freeze/` se versiona a propósito: guarda el resultado de las celdas, de modo
que el compilado en CI no vuelve a ejecutar los capítulos lentos salvo que su
fuente haya cambiado.

## Licencias

Texto: [CC BY-NC-SA 4.0](LICENSE). Código: [MIT](LICENSE-CODE).
Tipografías en `styles/fonts/`: SIL OFL 1.1 (cada una con su licencia al lado).
