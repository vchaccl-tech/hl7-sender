#!/bin/bash

# Script para crear el icono .icns para macOS

ICON_SOURCE="icon.png"
ICON_DIR="icon.iconset"

# Crear directorio para iconset
mkdir -p "$ICON_DIR"

# Crear diferentes tamaños usando sips (herramienta nativa de macOS)
sips -z 16 16     "$ICON_SOURCE" --out "${ICON_DIR}/icon_16x16.png"
sips -z 32 32     "$ICON_SOURCE" --out "${ICON_DIR}/icon_16x16@2x.png"
sips -z 32 32     "$ICON_SOURCE" --out "${ICON_DIR}/icon_32x32.png"
sips -z 64 64     "$ICON_SOURCE" --out "${ICON_DIR}/icon_32x32@2x.png"
sips -z 128 128   "$ICON_SOURCE" --out "${ICON_DIR}/icon_128x128.png"
sips -z 256 256   "$ICON_SOURCE" --out "${ICON_DIR}/icon_128x128@2x.png"
sips -z 256 256   "$ICON_SOURCE" --out "${ICON_DIR}/icon_256x256.png"
sips -z 512 512   "$ICON_SOURCE" --out "${ICON_DIR}/icon_256x256@2x.png"
sips -z 512 512   "$ICON_SOURCE" --out "${ICON_DIR}/icon_512x512.png"
sips -z 1024 1024 "$ICON_SOURCE" --out "${ICON_DIR}/icon_512x512@2x.png"

# Convertir a .icns
iconutil -c icns "$ICON_DIR" -o icon.icns

# Limpiar
rm -rf "$ICON_DIR"

echo "✅ Icono creado: icon.icns"
