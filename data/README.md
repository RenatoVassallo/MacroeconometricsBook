# Datos

Dos carpetas y una regla.

- `raw/`: los archivos tal como llegan de la fuente (API del BCRP, FRED,
  descargas manuales). **No se editan nunca a mano.** Cada archivo debería poder
  volver a descargarse con un script de `code/python/`.
- `processed/`: las series construidas (agregaciones, transformaciones, paneles
  listos para estimar). Todo lo de aquí se reconstruye desde `raw/`.

Ninguna de las dos se versiona en Git, salvo este archivo y los `.gitkeep`: los
datos se rehacen, no se guardan. Si una fuente deja de estar disponible, el
script que la descarga debe guardar una copia fechada y documentarla aquí.

## Registro de fuentes

| Serie | Código | Fuente | Frecuencia | Descarga |
|:------|:-------|:-------|:-----------|:---------|
| Índice de precios de exportación | `PN38915BM` | BCRP | mensual | por escribir |
| PBI real | `PN02538AQ` | BCRP | trimestral | por escribir |
| Ingresos corrientes del gobierno general | `PN38689FM` | BCRP | mensual | por escribir |
