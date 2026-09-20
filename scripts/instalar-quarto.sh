#!/usr/bin/env bash
# Instala Quarto dentro de un contenedor Linux (amd64 o arm64).
#
#   bash scripts/instalar-quarto.sh            # última versión probada
#   bash scripts/instalar-quarto.sh 1.11.5     # una versión concreta
#
# Variables opcionales:
#   QUARTO_DEST  carpeta de instalación (por defecto /opt/quarto)
#   SYMLINK=0    no crear el enlace en /usr/local/bin

set -euo pipefail

VERSION="${1:-1.11.5}"
DEST="${QUARTO_DEST:-/opt/quarto}"
SYMLINK="${SYMLINK:-1}"

case "$(uname -m)" in
  x86_64|amd64)  ARCH=amd64 ;;
  aarch64|arm64) ARCH=arm64 ;;
  *) echo "Arquitectura no contemplada: $(uname -m)" >&2; exit 1 ;;
esac

URL="https://github.com/quarto-dev/quarto-cli/releases/download/v${VERSION}/quarto-${VERSION}-linux-${ARCH}.tar.gz"
echo "Descargando Quarto ${VERSION} (${ARCH})"
mkdir -p "$DEST"
curl -fsSL "$URL" | tar -xz --strip-components=1 -C "$DEST"

if [ "$SYMLINK" = "1" ]; then
  ln -sf "$DEST/bin/quarto" /usr/local/bin/quarto
fi

"$DEST/bin/quarto" --version
echo
echo "Listo. Para el PDF, una vez:  quarto install tinytex"
