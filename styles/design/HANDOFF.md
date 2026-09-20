# Warm Folio — handoff for Claude Code

Visual system for *Applied Macroeconometrics with Python* (Quarto book, HTML primary, LuaLaTeX PDF secondary).
Three files to write: `styles/book.scss`, `styles/book.tex`, `styles/matplotlib.mplstyle`.
Canonical values: `handoff/tokens.json`. Mockups: the four `Warm Folio — *.dc.html` files in the project root.

No institutional branding anywhere. Light theme only.

## 1. Fonts — download sources

| Role | Family | License | Web | OTF/TTF for LuaLaTeX + matplotlib |
|---|---|---|---|---|
| Body serif | EB Garamond | SIL OFL 1.1 | `fonts.google.com/specimen/EB+Garamond` (self-host woff2) | github.com/octaviopardo/EBGaramond12 → `EBGaramond[wght].ttf`, `EBGaramond-Italic[wght].ttf` |
| Math | Garamond-Math | SIL OFL 1.1 | self-host `Garamond-Math.otf` for MathJax `HTML-CSS` fallback | github.com/YuanshengZhao/Garamond-Math → `Garamond-Math.otf` |
| Headings / UI | Source Sans 3 | SIL OFL 1.1 | `fonts.google.com/specimen/Source+Sans+3` | github.com/adobe-fonts/source-sans → `SourceSans3[wght].ttf` |
| Code | JetBrains Mono | SIL OFL 1.1 | `fonts.google.com/specimen/JetBrains+Mono` | github.com/JetBrains/JetBrainsMono → `JetBrainsMono[wght].ttf` |

Garamond-Math is the deliberate pairing: it is drawn to EB Garamond's x-height and stroke weight, so display equations sit in the text without a weight jump. Put all font files in `styles/fonts/` and register them with `\setmainfont[Path=...]`; matplotlib picks them up from the same directory via `font.serif` / `font.sans-serif` after one `fm.fontManager.addfont()` call in `conf/mpl_register.py`.

## 2. Token → SCSS → LaTeX → mplstyle

| Token | SCSS (book.scss) | LaTeX (book.tex) | mplstyle key |
|---|---|---|---|
| `color.text` #2A231D | `$body-color` | `\definecolor{ink}` | `text.color`, `axes.labelcolor` |
| `color.text_muted` #6B5F52 | `$gray-600` | `\definecolor{muted}` | `xtick.color`, `ytick.color`, `axes.edgecolor` |
| `color.bg` #FDFBF7 | `$body-bg` | `\pagecolor{paper}` (PDF: white) | — (figures stay white) |
| `color.surface` #F7EDE5 | `$light` | `\definecolor{tint}` | — |
| `color.surface_2` #F0E0D6 | `$callout-assumption-bg` | `\definecolor{tintstrong}` | — |
| `color.surface_code` #FBF6F1 | `$code-block-bg` | `\definecolor{codebg}` | — |
| `color.border` #DED0C4 | `$border-color`, `$table-border-color` | `\definecolor{rule}` | `grid.color` (soft variant) |
| `color.primary` #B0472A | `$primary`, `$link-color` | `\definecolor{accent}` | `axes.prop_cycle` [1] |
| `color.primary_dark` #8E3620 | `$link-hover-color` | `\definecolor{accentdark}` | — |
| `color.accent` #4E6E38 | `$success` (repurposed: Intuition) | `\definecolor{olive}` | `axes.prop_cycle` [3] |
| `color.info` #3D647F | `$info` (Application) | `\definecolor{blue}` | `axes.prop_cycle` [2] |
| `chart.observed[0..2]` | `$chart-obs-1..3` | `\definecolor{obsone..three}` | `axes.prop_cycle` [0] + explicit greys |
| `chart.band[0..3]` | `$chart-band-1..4` | `\definecolor{bandone..four}` | passed to `fill_between` from `macropy.plotting.BANDS` |
| `chart.shock[0..5]` | `$chart-shock-1..6` | `\definecolor{shockone..six}` | `axes.prop_cycle` (full 6-colour cycle, with `lines.linestyle` cycled in code) |
| `chart.diverging` | `$chart-div-1..7` | `\definecolor{divone..seven}` | registered as `LinearSegmentedColormap "warmfolio_div"` in `conf/mpl_register.py` |
| `chart.episode.recession` #EDE9E4 | `$chart-episode-rec` | `\definecolor{recession}` | used via `axvspan(color=...)` helper |
| `chart.episode.forecast` #FBF0EA | `$chart-episode-fcst` | `\definecolor{fcstwin}` | same |
| `chart.grid` #E7DAD0 | `$border-color-soft` | `\definecolor{rulesoft}` | `grid.color` |
| `font.body` | `$font-family-serif` | `\setmainfont{EB Garamond}` | `font.serif` |
| `font.math` | MathJax `output/chtml` + woff2 | `\setmathfont{Garamond-Math.otf}` (unicode-math) | `mathtext.fontset: custom`, `mathtext.it: EB Garamond:italic` |
| `font.ui` | `$font-family-sans-serif`, `$headings-font-family` | `\setsansfont{Source Sans 3}` | `font.sans-serif`, used for all figure text |
| `font.mono` | `$font-family-monospace` | `\setmonofont{JetBrains Mono}` | — |
| `type_web.body` 17/27.5 | `$font-size-base: 1.0625rem; $line-height-base: 1.62` | — | — |
| `type_print.body` 10.5/14.5 | — | `\documentclass[10.5pt]` + `\setstretch` via `setspace` | — |
| `type_print.figure_text` 8.5 | — | — | `font.size: 8.5`, `axes.labelsize: 9`, `xtick.labelsize: 8`, `legend.fontsize: 8` |
| `layout.measure_ch` 68 | `$content-max-width: 40rem` (Quarto `.page-columns` override) | `\setlength{\textwidth}{4.5in}` (geometry) | — |
| `layout.web.margin_column` 200 | `$margin-column-width` | `\setlength{\marginparwidth}{1.15in}` | — |
| `layout.figure_width.text` | `.figure-text { width: 640px; max-width: 100% }` | `\includegraphics[width=4.5in]` | `figure.figsize: 4.5, 2.6` |
| `layout.figure_width.full` | `.figure-full { width: 960px }` | `\includegraphics[width=6.0in]` | `figure.figsize: 6.0, 2.4` |
| `layout.space.*` | `$spacer` scale 4→64 px | `\smallskip`/`\medskip`/`\bigskip` remapped to 6/12/18 pt | — |
| `code_tokens.*` | Pandoc `.theme` JSON (`warmfolio.theme`) | `\lstdefinestyle` / `tcolorbox` listing style | — |
| `figure_style.*` | — | — | direct mplstyle keys (see §4) |

## 3. Quarto wiring

- `_quarto.yml`: `format.html.theme: [cosmo, styles/book.scss]`, `format.html.highlight-style: styles/warmfolio.theme`, `format.pdf.include-in-header: styles/book.tex`, `format.pdf.documentclass: scrbook`, `format.pdf.geometry` from `layout.print`.
- Content blocks: eight fenced divs (`::: {.definition}` … `::: {.exercise}`) + one Lua filter (`filters/blocks.lua`) for numbering (`chapter.n`) and cross-references (`@asm-recursive` → "Assumption 5.1"). The filter emits `<div class="block block-assumption">` in HTML and `\begin{assumptionblock}` in LaTeX.
- Exercise solutions: plain `<details><summary>Show solution</summary>` in HTML; in print the filter flattens to a `\paragraph{Solution.}` in a smaller size.
- Tabsets, citation hover previews, footnotes, margin notes (`.column-margin`), search, prev/next: all Quarto-native, no custom code.

## 4. matplotlib.mplstyle — the values that matter

```
font.family: sans-serif
font.sans-serif: Source Sans 3
font.serif: EB Garamond
font.size: 8.5
axes.titlesize: 0            # titles live in the caption, never in the axes
axes.labelsize: 9
xtick.labelsize: 8
ytick.labelsize: 8
legend.fontsize: 8
legend.frameon: False
figure.facecolor: white
savefig.facecolor: white
savefig.transparent: False
savefig.dpi: 300
savefig.bbox: tight
axes.facecolor: white
axes.edgecolor: 6B5F52
axes.linewidth: 0.7
axes.spines.top: False
axes.spines.right: False
axes.grid: True
axes.grid.axis: y
grid.color: E7DAD0
grid.linewidth: 0.5
lines.linewidth: 1.1
axes.prop_cycle: cycler(color=['2A231D','3D647F','B0472A','5A7D43','9A7B2E','C9A98A'])
figure.figsize: 4.5, 2.6
mathtext.fontset: custom
mathtext.rm: EB Garamond
mathtext.it: EB Garamond:italic
```

`axes.titlesize: 0` is a reminder, not a mechanism — enforce "no in-axes titles" in review, since matplotlib has no switch for it.

## 5. Accessibility record

- Body text #2A231D on #FDFBF7 = 13.1:1. Muted text #6B5F52 = 5.5:1. Links #B0472A = 5.7:1, hover #8E3620 = 7.4:1. Borders #DED0C4 = 3.1:1 against the page (UI threshold).
- #4E6E38 is the darkened olive: the seed #5A7D43 fails 4.5:1 on the tint surface (4.09:1). Seed olive survives only inside charts, where the 3:1 graphical threshold applies.
- Seed `gold #9A7B2E` and `tint #F0E0D6` are kept for charts and surfaces only, never as text colour.
- Chart palettes separate by lightness, so deuteranopia and protanopia keep the ordering; shock series additionally cycle line style and marker, bands are monotone in lightness.

## 6. What cannot match between HTML and PDF — and the fallback chosen

1. **Math glyphs.** HTML renders through KaTeX (Quarto default), which cannot use Garamond-Math; PDF uses it via `unicode-math`. Fallback: self-host KaTeX's `Katex_Main` with `font-size-adjust: 0.52` so the x-height matches EB Garamond. Expect small differences in the case-brace of (5.3) and in large operators.
2. **Tabsets.** No print equivalent. Fallback: print emits both listings in order with run-in labels "From scratch (NumPy)." and "MacroPy."
3. **Collapsible solutions.** `<details>` has no print form. Fallback: solutions print in full, one size down, directly under the exercise. (Alternative if you prefer: an end-of-book solutions appendix — say which you want.)
4. **Citation hover previews.** HTML only; print has the bibliography.
5. **Margin notes.** HTML at ≤992 px collapses them into the flow (Quarto behaviour, kept); print pins them to the outer margin and never breaks them across pages.
6. **Justification and hyphenation.** Print justifies with `microtype` + LuaLaTeX hyphenation; HTML stays ragged-right (browser hyphenation is unreliable at this measure).
7. **Surface tints.** HTML #F7EDE5 / #F0E0D6 are screen values; print converts to 3 % / 5 % of the tint in CMYK, which reads slightly warmer on uncoated stock. Rule-only blocks (Result, Intuition, Pitfall, Exercise) are unaffected.
8. **Dark theme.** Not shipped. A dark theme would put every figure on a light plate inside a dark page, which reads as a patchwork at the density of these chapters; if you want it later, the plate approach is the only one I would sign off on.
9. **Figure fonts.** Figures embed Source Sans 3 as vector text in both outputs, so they match — provided HTML figures are served as SVG. PNG fallback at 2× for any figure with more than ~2000 path elements (the heatmap and the historical decomposition).

## 7. Elements that need custom HTML (flagged per the brief)

- The eight content blocks (fenced divs + Lua filter) — CSS only, no JavaScript.
- Landing-page chapter index in two columns (`::: {.chapter-index}`).
- Chapter-opener "Data used" panel (a table inside a styled div).
- Everything else — navigation, TOC, search, tabsets, footnotes, margin notes, prev/next — is stock Quarto.
