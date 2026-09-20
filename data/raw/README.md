# Datos crudos

Los archivos de esta carpeta no se editan nunca. Todo lo que el libro usa se
reconstruye a partir de ellos con los scripts de `code/python/`, que escriben en
`data/processed/`.

| Archivo | Qué es | Lo usa |
|:--------|:-------|:-------|
| `SW2001_Data.xlsx` | Muestra trimestral de Stock y Watson (2001): inflación, desempleo y tasa de fondos federales, 1960Q1 a 2000Q4. | @sec-svar, @sec-bvar |
| `BQ1989_Data.xlsx` | Muestra trimestral de Blanchard y Quah (1989): crecimiento del PBI y desempleo. | @sec-svar |
| `Uhlig2005_Data.xlsx` | Muestra mensual de Uhlig (2005): PBI real interpolado, deflactor, precios de materias primas, reservas y tasa de fondos, 1965M1 a 2003M12. | @sec-datos |
| `peru_mensual_bcrp.csv` | Series mensuales del BCRP: PBI desestacionalizado (`PN01773AM`), IPC de Lima (`PN38705PM`), tipo de cambio (`PN01210PM`) y tasa de referencia (`PD04722MM`). | @sec-datos |
| `database_peru.xlsx` | Base trimestral del BCRP, **no versionada** por su tamaño (11 MB). | @sec-var |

Los tres primeros vienen de los materiales de replicación de cada artículo. Los
dos últimos se descargan de la API del BCRP; la celda de descarga del capítulo 1
muestra cómo, y `code/python/build_peru_data.py` documenta los códigos de serie.

`data/processed/` sí se versiona: son CSV pequeños que permiten compilar el libro
sin los archivos crudos, incluida la base peruana de 11 MB que queda fuera.

Para reconstruirlos:

```bash
uv run python code/python/build_us_data.py
uv run python code/python/build_peru_data.py
```
