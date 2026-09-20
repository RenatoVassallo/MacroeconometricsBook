# Handoff: Warm Folio — visual system for *Applied Macroeconometrics with Python*

## Overview

Complete visual system for an open graduate textbook written in Quarto and rendered to two outputs: an HTML book (Bootstrap 5 book layout) and a LuaLaTeX PDF at 7 × 10 in trim, plus a single matplotlib style used by every figure in the book.

The implementation target is three files:

- `styles/book.scss` — Quarto HTML theme (Bootstrap 5 SCSS variables + rules)
- `styles/book.tex` — LaTeX preamble included in the PDF
- `styles/matplotlib.mplstyle` — every figure

Plus two support files the system needs: `styles/warmfolio.theme` (Pandoc syntax-highlight theme) and `filters/blocks.lua` (numbering and cross-references for the eight content blocks).

**Read `HANDOFF.md` first** — it holds the token → SCSS → LaTeX → mplstyle mapping table, exact font download sources, the mplstyle core, the accessibility record, the nine things that cannot match between HTML and PDF with the fallback chosen for each, and the list of elements that need custom HTML. `tokens.json` is the canonical value set; prefer it over any number read off a mockup.

## About the design files

The files in `mockups/` are **design references created in HTML** — prototypes showing intended look, density and behaviour. They are not production code to copy. They are written as streaming "Design Components" (`.dc.html` + `support.js`), which is an authoring format from the design tool, not a target framework: open them in a browser to view, but implement the design in Quarto/SCSS/LaTeX/mplstyle as described above, using Quarto's stock book template wherever possible.

Concretely: do not port the HTML structure. Port the values and the treatments.

## Fidelity

**High fidelity.** Colours, type pairings, both type scales, spacing, block treatments, figure geometry and print measures are final and contrast-checked. Two known approximations in the mockups themselves:

- Math is set with plain HTML `<em>/<sub>/<sup>`, not a math font. The shipped pairing is EB Garamond + Garamond-Math (see `HANDOFF.md` §1); judge the mockups' equation spacing, not their glyphs.
- The braced case distinction in equation (5.3) is faked in HTML. In the book it renders through Quarto's math pipeline.

## Files in this bundle

| File | What it is |
|---|---|
| `HANDOFF.md` | Implementation spec: mapping table, fonts, mplstyle, accessibility, HTML/PDF mismatches, custom-HTML flags |
| `tokens.json` | Canonical tokens: colour, chart palettes, fonts, web and print type scales, layout, code tokens, figure style |
| `mockups/Warm Folio — Tokens and Blocks.dc.html` | Token specimen: core colour with contrast ratios, per-block semantic colour, chart palettes (a)–(g) with grayscale strips, type pairing, both scales, layout and spacing, code tokens, the eight content blocks + grayscale print check |
| `mockups/Warm Folio — HTML Mockups.dc.html` | Landing, chapter opener, dense interior, chapter end at 1440 px; landing and interior at 390 px. Tabset and citation hover are live |
| `mockups/Warm Folio — Figure Specimen.dc.html` | All 11 required figures, drawn in point units at real output width (324 pt text, 432 pt full), type 8–9 pt |
| `mockups/Warm Folio — Print and Assets.dc.html` | 7 × 10 in two-page spread (verso chapter opener, recto dense interior), typographic cover, 1200 × 630 social card, favicon at 32/48/180 |
| `mockups/Textbook Directions (step 1, three options).dc.html` | The three low-fidelity directions from step 1. 1a (Warm Folio) was chosen; kept for context |
| `mockups/support.js` | Runtime the `.dc.html` files load. Needed only to view them |

## Screens and views

Every screen below is Quarto's stock book layout — left chapter sidebar, right "on this page" TOC, search, prev/next links, margin column. Only colour, type, blocks and figures are ours.

### Landing page
Purpose: state what the book is, who it is for, and give the three entry points (read, PDF, GitHub).
Layout: 54 px top bar (book title, three nav links, 180 px search field, PDF, GitHub); 270 px sidebar with the chapter list; content column max 900 px with 56/64 px padding.
Components: eyebrow 11 px / 700 / 0.16 em uppercase `#B0472A`; H1 EB Garamond 52/56 px 600, tracking −0.012 em, max 24 ch; subtitle EB Garamond 23 px `#6B5F52`; pitch paragraph EB Garamond 20/32 px, max 62 ch; author line 18 px + 14 px muted metadata; three links as 10/20 px rectangles — filled `#B0472A` with `#FDFBF7` text, outlined `#B0472A`, outlined `#DED0C4`; chapter index in two columns, each row a 12 px JetBrains Mono number `#B0472A` + 18 px EB Garamond title + 12.5 px muted description, separated by 1 px `#EFE6DE`.

### Chapter opener
Purpose: frame the chapter as an empirical problem before any model appears.
Layout: sidebar 270 / content / TOC 240; content padding 48/64/60.
Components: "Chapter 5" in JetBrains Mono 12.5 px 0.1 em uppercase `#B0472A`; H1 EB Garamond 44/49 px 600; the economic question in a 4 px `#B0472A` left rule block, label 11 px 700 uppercase `#8E3620`, question EB Garamond 23/34 px; "What you will learn" as 3–5 numbered rows (JetBrains Mono 12 px number + 18/27 px text, 1 px `#EFE6DE` separators); prerequisites as running prose with inline code chips (`#F4EAE2` fill, 1 px `#E7DAD0`); "Data used" panel on `#F7EDE5` with 1 px `#E0D0C2`, a two-column table (series / source · frequency · transformation) and a 12 px source note.

### Dense interior page
Purpose: the working page of the book — prose, numbered equations, all eight block types, code, figure, table.
Layout: sidebar 270 / content 640 (68 ch measure) / TOC 240 + margin notes under the TOC.
Components, in order: H2 Source Sans 3 27 px 600 with a 56 × 2 px ink underline; body EB Garamond 17/27.5 px; display equations centred with the number right-aligned in 13 px Source Sans 3 `#6B5F52`; cross-reference links underlined 1 px at 35 % primary; citation with hover preview (330 px white card, 1 px `#DED0C4`, 12 px shadow at 12 % ink); the eight blocks (below); a two-tab code tabset; a code cell with a text-output block; Figure 5.3 on a white plate with caption + source note; a booktabs table (1.6 pt top and bottom rules, 0.8 pt under the header, 0.4 pt `#E0D2C6` between rows, tabular numerals); a footnote separated by a 1 px rule; prev/next links.

### Chapter end
Purpose: consolidate.
Components: "Key takeaways" as four numbered rows; "Further reading" as a 200 px citation column + annotation; "Exercises" as rule-separated items with a `<details>` solution whose summary is 12.5 px 600 `#B0472A`.

### Print spread (7 × 10 in, 96 px/in in the mockup)
Type block 4.5 × 7.6 in. Margins: top 0.9, inner 0.85, outer 1.65, foot 1.0 in. Margin column 1.15 in, gutter 0.3 in. Running heads 9.5 pt 0.1 em uppercase `#6B5F52`: verso = folio then book title, recto = section then folio. Body justified with hyphenation. Margin notes ragged-right in the outer margin, anchored to their paragraph, never broken across pages. Figures at 4.5 in (text) or 6.0 in (full).

## The eight content blocks

Each is one styled div. Identity is carried by label and rule treatment, never by colour alone, so all eight survive a grayscale print. Assumption is deliberately the loudest treatment in the system because readers skip assumptions.

| Block | Web treatment | Print treatment |
|---|---|---|
| Assumption (numbered) | `#F0E0D6` fill, 4 px `#B0472A` left bar, 1 px `#DCC4B5` other sides, label 11.5 px 700 0.13 em uppercase `#8E3620` | keeps a 5 % tint, 3 pt left bar |
| Definition (numbered) | `#F7EDE5` fill, 1 px `#E0D0C2`, label uppercase ink | keeps a 3 % tint |
| Result (numbered) | no fill; 2.5 px ink top rule + 1 px ink bottom rule; statement italic | same, rule-only |
| Algorithm (numbered steps) | `#FBF6F1` fill, 1 px `#E7DAD0`, 3 px double `#6B5F52` left rule; step numbers JetBrains Mono 12 px `#B0472A` | same |
| Example / Empirical application | white fill, 1 px `#CFC2B6`, label `#3D647F` preceded by an 8 px filled square | same |
| Intuition | no fill, 2 px dotted `#4E6E38` left rule, label `#4E6E38` | same, rule-only |
| Pitfall | no fill, 1 px `#8E3620` top rule + 4 px double `#8E3620` left rule, label `#8E3620` | same, rule-only |
| Exercise (numbered) | 1 px `#DED0C4` top and bottom rules, label JetBrains Mono 11 px uppercase muted, `<details>` solution | solution prints in full one size down under the exercise |

Implementation: eight fenced divs (`::: {.assumption}` … `::: {.exercise}`) plus `filters/blocks.lua` for automatic numbering per chapter and cross-references (`@asm-recursive` → "Assumption 5.1"). The filter emits `<div class="block block-assumption">` in HTML and `\begin{assumptionblock}` in LaTeX. This is custom HTML — Quarto callouts cannot produce eight distinct treatments — but it needs no JavaScript.

## Interactions and behaviour

- **Tabset** ("From scratch (NumPy)" / "MacroPy"): Quarto-native `::: {.panel-tabset}`. Active tab = `#FBF6F1` fill, 1 px `#E7DAD0` on three sides, ink label 600; inactive = transparent, muted label 400. Body is a code block with no top border.
- **Citation hover preview**: Quarto-native. 330 px card, white, 1 px `#DED0C4`, 12 px shadow at 12 % ink, 12.5/19 px Source Sans 3.
- **Exercise solution**: `<details>`/`<summary>`, no animation.
- **Links**: `#B0472A`, hover `#8E3620` with underline; in prose an underline at 35 % primary, 1 px.
- **Responsive**: single Quarto breakpoint behaviour, unchanged. At ≤992 px the margin column collapses into the flow; margin notes keep their tint and rule so they stay separable from body text. At 390 px the measure holds by dropping to one column; equations and code scroll horizontally rather than shrinking.
- No animation, no transition, no JavaScript widget anywhere in this system.

## State management

None beyond what Quarto ships (sidebar collapse, tabset selection, search, `<details>` open state). The mockups' tab and hover state exist only to demonstrate the target appearance.

## Design tokens

Use `tokens.json`. Summary: text `#2A231D`, muted `#6B5F52`, background `#FDFBF7`, surfaces `#F7EDE5` / `#F0E0D6` / `#FBF6F1`, borders `#DED0C4` / `#E7DAD0`, primary `#B0472A`, primary dark `#8E3620`, accent `#4E6E38`, info `#3D647F`. Chart palettes: observed greys, primary estimate, `#1F3D5C` realized markers, a 4-step band ramp, 6 lightness-ordered shock colours with fixed line styles and markers, a 7-step diverging ramp, two episode shadings. Body 17/27.5 px web and 10.5/14.5 pt print; figure text 8–9 pt. Spacing 4 → 64 px (3 → 48 pt). No border radius and no shadows anywhere except the citation hover card. Measure 68 ch.

Note: the seed olive `#5A7D43` was darkened to `#4E6E38` for text use because it fails 4.5:1 on the tint surface; the seed value survives inside charts, where the 3:1 graphical threshold applies.

## Assets

- Fonts: EB Garamond, Garamond-Math, Source Sans 3, JetBrains Mono — all SIL OFL, sources in `HANDOFF.md` §1. Place OTF/TTF in `styles/fonts/`.
- Cover, social card and favicon are typographic plus one abstract motif derived from the fan chart (its 68/90/95 % bands and median path). No stock imagery, no illustration, no gradient.
- No institutional branding of any kind — no university, school or central-bank names, logos or colours.
- All figure data in the mockups is synthetic; the real figures come from `code/ch*.py` reading `data/processed/`.
