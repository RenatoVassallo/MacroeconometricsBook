# Macroeconometrics Book

## Objective

Develop a modern graduate-level textbook on applied
macroeconometrics using Python.

The book should bridge economic intuition, econometric theory,
computation, and empirical macroeconomic applications.

**Language: the first edition is written in Spanish.** Prose, headings, figure
labels, code comments and block labels are in Spanish. This file and the
technical scaffolding stay in English.

## Audience

Advanced undergraduate, MSc, beginning PhD students, central-bank
economists, policy economists and applied researchers.

Readers should know:
- undergraduate econometrics
- linear algebra
- probability
- basic Python

## Model reference

*Applied Bayesian Econometrics for Central Bankers* (Blake and Mumtaz, CCBS,
Bank of England, 2017) is the closest reference in spirit: applied, algorithm
first, written for people who have to produce results. This book aims at the
same usefulness, in Python, with uniform notation and somewhat more formality.

## Pedagogical philosophy

Models should be introduced as solutions to empirical problems.

Each chapter should generally follow:

1. Economic question
2. Motivation
3. Model
4. Statistical assumptions
5. Estimation
6. Economic interpretation
7. Python implementation
8. Empirical application
9. Diagnostics
10. Limitations
11. Extensions
12. Exercises

Do not present models as disconnected mathematical objects.

Whenever possible:

simple model -> limitation -> richer model

## Mathematical style

Use matrix notation when it simplifies the exposition.

Explain important equations in words.

Do not skip identification assumptions.

Separate clearly:
- model
- estimator
- identification assumptions
- computational algorithm

### Notation (fixed across the book)

- Vectors in bold (`\mathbf{y}_t`, `\mathbf{u}_t`) so they are not confused with
  GDP (`y_t`); matrices uppercase (`\Phi_\ell`, `\Sigma`).
- Lag matrices are `\Phi_1, ..., \Phi_p` (as in the 2023 slides); `B` is reserved
  for the stacked `k x n` matrix of the compact form, with the constant in the
  FIRST row. MacroPy stacks it last, so reorder when comparing with MacroPy.
  Reduced-form innovations are `u_t`, structural shocks `\varepsilon_t`, impact
  matrix `S`. Vectorised objects are lowercase: `y = vec(Y)`, `b = vec(B)`,
  `u = vec(U)`.
- Reduced form: `\mathbf{y}_t = c + \Phi_1 \mathbf{y}_{t-1} + ... + \Phi_p \mathbf{y}_{t-p} + \mathbf{u}_t`,
  `\mathbf{u}_t ~ N(0, \Sigma)`; compact form `Y = XB + U` with `k = np + 1`.
- Bayesian objects follow Blake and Mumtaz: prior `b ~ N(b_0, H)`,
  `\Sigma ~ IW(S_0, \nu_0)`; Minnesota hyperparameters `\lambda_1` to
  `\lambda_4` and `\delta_i`.
- `appendices/a-notacion.qmd` is the single source of truth; update it when a
  new symbol appears.

## Computational philosophy

Python is the primary language.

Code should illuminate the econometrics rather than replace it.

Three levels may be used:

1. equations / algorithm
2. transparent NumPy/Pandas implementation
3. high-level MacroPy implementation

Avoid unnecessarily long code blocks. Keep code lines at or under 64
characters: that is exactly what fits the PDF column at the current mono size.
Longer lines wrap (fvextra in the PDF, `code-overflow: wrap` on the web) and
the continuation reads badly.

Forecast bands: say the level explicitly and keep it across chapters.
Frequentist chapters report a single 95 % interval; the Bayesian chapters report
68 % and 95 % posterior quantiles. The 68 % convention of the SVAR literature
(Sims and Zha, 1999) is discussed in @sec-var-pronostico, not used by default.

`Cuidado` blocks are at most 120 words. Anything longer belongs in the running
text.

Standard topics the book does not develop (lag selection, residual diagnostics,
unit roots and cointegration) live in one "Otros temas" section per chapter:
criteria, good practice and where to study them.

Syntax highlighting: `styles/warmfolio.theme` (ink keywords, steel blue for
function names, olive strings, terracotta numbers). Two alternates ship with the
book, `warmfolio-minimo.theme` and `warmfolio-azul.theme`; switch by changing
`highlight-style` in `_quarto.yml`.

MacroPy is pinned to 0.1.11 in `pyproject.toml` (and in `uv.lock`); the book
depends on its API and its behaviour.

## Figures

Figures should use a common Matplotlib style defined in:

styles/matplotlib.mplstyle

Figures should be publication quality.

Do not manually specify styling independently in individual scripts.

**All code in the book is written in English**: identifiers, comments and
docstrings, in the chapters and in the package. Prose, figure labels and block
labels stay in Spanish.

Every chapter that draws starts with:

```python
from macrobook import use_style, PALETTE, charts
use_style()
```

`use_style()` registers the fonts, applies the style sheet and neutralises
MacroPy's own `set_bse_style()`, which otherwise overwrites the rcParams on
every call to its plotting functions.

Recurring figures (fan charts, IRF grids, stacked decompositions, prior vs
posterior, traces, unit circle) have helpers in `code/python/macrobook/charts.py`.
Extend that module instead of restyling inside a chapter. VAR mechanics (lag
matrix, OLS, companion, roots, Wold weights, forecasting, simulation) live in
`code/python/macrobook/var.py`; identification, impulse responses, FEVD,
historical decomposition, bootstrap bands and local projections live in
`code/python/macrobook/svar.py`; the Minnesota prior, the Gibbs sampler and the
predictive density live in `code/python/macrobook/bvar.py`.

**Figures never hardcode a width.** Quarto sets `figure.figsize` per format
(7 in for the web, 4.5 in for the PDF) and chapters call
`figsize(ratio)` from `macrobook`, which returns `(width, ratio * width)`. Both
formats then draw at their own physical size with the same 8.5 pt type, and the
web shows the figure at the full width of the text column. `styles/matplotlib.mplstyle`
deliberately does not set `figure.figsize`.

Stacked decompositions use `PALETA["rellenos"]`, not `PALETA["choques"]`: see
`styles/design/NOTAS-IMPLEMENTACION.md` for why.

## Content blocks

Eight blocks, and only these eight:

| Block | Syntax | Cross-reference |
|:------|:-------|:----------------|
| Supuesto | `::: {#cnj-name}` with `## Title` | `@cnj-name` |
| Definición | `::: {#def-name}` | `@def-name` |
| Resultado | `::: {#thm-name}` / `prp-` / `lem-` / `cor-` | `@thm-name` |
| Algoritmo | `::: {#alg-name}`, caption as the last paragraph | `@alg-name` |
| Ejemplo | `::: {#exm-name}` | `@exm-name` |
| Ejercicio | `::: {#exr-name}` | `@exr-name` |
| Intuición | `::: {.intuicion}` | none |
| Cuidado | `::: {.cuidado}` | none |

Solutions go in `::: {.solucion}` right after the exercise. Chapter-opening
components: `::: {.pregunta}`, `::: {.aprendizajes}`, `::: {.datos-usados}`;
chapter closing: `::: {.ideas-clave}`, `::: {.lecturas}`.

Code tab titles inside `::: {.panel-tabset}` use level-4 headings (`####`).

Chapter-closing headings (`## Ideas clave`, `## Lecturas recomendadas`,
`## Ejercicios`) carry `{.unnumbered}`.

Chapters 3 uses Peruvian data (BCRP); chapters 4 and 5 replicate the classic US
datasets shipped with Stock and Watson (2001) and Blanchard and Quah (1989), so
that the structural and Bayesian results can be checked against published
numbers. `code/python/build_us_data.py` rebuilds both CSVs from `data/raw/`.

## Reproducibility

Every empirical result should be reproducible from code.

Raw data should never be modified manually.

Use:

data/raw/
data/processed/

Generated figures belong in:

figures/generated/

Chapters execute with `execute-dir: project`, so paths are relative to the
repository root. `freeze: auto` caches chapter output; commit `_freeze/` when a
chapter's results are stable.

Build (the environment is managed with uv; `pyproject.toml` + `uv.lock`):

```bash
uv sync                         # creates .venv with Python 3.11 and macrolibro
uv run quarto preview           # web
uv run quarto render --to pdf   # PDF (LuaLaTeX; `quarto install tinytex` if needed)
```

Always call Quarto through `uv run` (or with `.venv` activated): Quarto starts
the Jupyter kernel from whatever `python3` is on PATH, and the system one has
no jupyter.

## Writing style

Precise, concise and intuitive.

Avoid unnecessary jargon.

Do not sacrifice econometric rigor for simplicity.

Use economic examples whenever possible.

The tone should resemble a professor explaining the material
carefully rather than a reference manual.

Spanish specifics: "usted" is avoided; address the reader directly and sparely.
Do not use the em dash.

## Source material

Legacy slides, MATLAB programs, Python scripts and notes are stored
under archive/.

These files are SOURCE MATERIAL.

Do not automatically reproduce their organization or wording.

Extract useful:
- explanations
- equations
- examples
- algorithms
- exercises
- empirical applications

and rewrite them into a coherent textbook.

`archive/` is git-ignored and temporary: it will be removed once the extraction
is done. It is not a dependency of the build.

**Warning about `archive/VAR/2026/_archivo_version_mensual/`:** those notebooks
used MacroPy's block-exogeneity mask inverted (see their `LEEME.md`), so every
result estimated with `b_exo` there is wrong. Reuse the explanations, never the
numbers or the figures.

## Cover

The PDF cover is drawn in TikZ inside `styles/book.tex` (`\maketitle` is
redefined): tint page, eyebrow, title, subtitle, the three-densities motif and
the author block. The same motif is an inline SVG at the top of `index.qmd` for
the web. To change the title or the author, edit the `\wfportada*` macros.

## Design system

The visual system is "Warm Folio" (see `styles/design/`). Tokens live in
`styles/design/tokens.json`; the implementation notes and the deliberate
deviations are in `styles/design/NOTAS-IMPLEMENTACION.md`. Change a colour or a
size there first, then in `book.scss`, `book.tex` and `matplotlib.mplstyle`.
