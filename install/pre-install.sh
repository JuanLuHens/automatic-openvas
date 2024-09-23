#!/bin/bash

echo "Eliminando la versión anterior de CMake..."
sudo apt-get purge -y cmake

echo "Actualizando los repositorios..."
sudo apt-get update

echo "Instalando software-properties-common..."
sudo apt-get install -y software-properties-common

echo "Añadiendo el repositorio PPA de deadsnakes..."
sudo add-apt-repository -y ppa:deadsnakes/ppa

echo "Actualizando los repositorios tras añadir el PPA..."
sudo apt-get update

echo "Instalando la nueva versión de CMake..."
sudo apt-get install -y cmake

echo "Instalación de la nueva versión de CMake completada."


echo "Buscando la ruta de pkgconfig..."
ruta_pkgconfig=$(find /usr/local/lib /usr/lib -name "pkgconfig*" 2>/dev/null | head -n 1)

if [ -z "$ruta_pkgconfig" ]; then
    echo "No se encontró ningún directorio 'pkgconfig'."
    exit 1
else
    echo "Directorio 'pkgconfig' encontrado en: $ruta_pkgconfig"
fi

echo "Exportando la ruta a PKG_CONFIG_PATH..."
export PKG_CONFIG_PATH=$ruta_pkgconfig:$PKG_CONFIG_PATH

echo "PKG_CONFIG_PATH ha sido configurado como: $PKG_CONFIG_PATH"

