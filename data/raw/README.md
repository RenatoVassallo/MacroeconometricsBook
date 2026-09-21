# Datos crudos

Los archivos de esta carpeta no se editan nunca. Todo lo que el libro usa se
reconstruye a partir de ellos con los scripts de `code/python/`, que escriben en
`data/processed/`.

| Archivo | Qué es | Lo usa |
|:--------|:-------|:-------|
| `SW2001_Data.xlsx` | Muestra trimestral de Stock y Watson (2001): inflación, desempleo y tasa de fondos federales, 1960Q1 a 2000Q4. | @sec-svar, @sec-bvar |
| `BQ1989_Data.xlsx` | Muestra trimestral de Blanchard y Quah (1989): crecimiento del PBI y desempleo. | @sec-svar |
| `Uhlig2005_Data.xlsx` | Muestra mensual de Uhlig (2005): PBI real interpolado, deflactor, precios de materias primas, reservas y tasa de fondos, 1965M1 a 2003M12. | reservada para las restricciones de signo |
| `peru_mensual_bcrp.csv` | Series mensuales del BCRP: PBI desestacionalizado (`PN01773AM`), IPC de Lima (`PN38705PM`), tipo de cambio (`PN01210PM`) y tasa de referencia (`PD04722MM`). | @sec-datos |
| `peru_trimestral_bcrp.csv` | PBI real trimestral del BCRP (`PN02538AQ`), en millones de soles de 2007, sin desestacionalizar, 1996T1 a 2026T2. | @sec-datos |
| `fred_DEXUSEU.csv` | Tipo de cambio diario, dólares por euro (FRED `DEXUSEU`); los feriados vienen vacíos. | @sec-datos |
| `fred_HOUSTNSA.csv` | Inicios de construcción de viviendas en EE.UU., miles de unidades, sin desestacionalizar (FRED `HOUSTNSA`). | @sec-datos |
| `fred_FEDFUNDS.csv` | Tasa efectiva de fondos federales, promedio mensual, en por ciento (FRED `FEDFUNDS`). | @sec-datos |
| `fred_ND000334Q.csv` | PBI real de EE.UU., miles de millones de dólares encadenados de 2017, sin desestacionalizar ni anualizar (FRED `ND000334Q`). | @sec-datos |
| `database_peru.xlsx` | Base trimestral del BCRP, **no versionada** por su tamaño (11 MB). | @sec-var |

Los tres primeros vienen de los materiales de replicación de cada artículo. Los
archivos `fred_*.csv` son el CSV que sirve FRED, tal cual
(`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<CÓDIGO>`, sin registro), y
las series del BCRP se descargan de su API; la celda de descarga del capítulo 1
muestra cómo, y los scripts de `code/python/` documentan códigos y unidades.

`data/processed/` sí se versiona: son CSV pequeños que permiten compilar el libro
sin los archivos crudos, incluida la base peruana de 11 MB que queda fuera.

Para reconstruirlos:

```bash
uv run python code/python/build_us_data.py
uv run python code/python/build_peru_data.py
```
