#!/bin/bash

echo "Definición directorios de instalación"
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && \
export BUILD_DIR=$HOME/build && \
export INSTALL_DIR=$HOME/install

export GVM_VERSION=$1
password=$2

sudo_execute() {
    echo "$password" | sudo -S "$@"
}

echo "Descarga y verificacion de Notus $GVM_VERSION"
export NOTUS_VERSION=$GVM_VERSION && \
curl -f -L https://github.com/greenbone/notus-scanner/archive/refs/tags/v$NOTUS_VERSION.tar.gz -o $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz
curl -f -L https://github.com/greenbone/notus-scanner/releases/download/v$NOTUS_VERSION/notus-scanner-$NOTUS_VERSION.tar.gz.asc -o $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz.asc $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz

echo "Extraer, compilar e instalar"
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz && \
cd $SOURCE_DIR/notus-scanner-$NOTUS_VERSION && \
sudo_execute python3 -m pip install . --prefix /usr --no-warn-script-location --no-dependencies && \
sudo_execute cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*
echo "Instalacion de Tomli module"
sudo_execute python3 -m pip install tomli
echo "Instalacion de gvm-tools"
sudo_execute python3 -m pip install --prefix /usr --no-warn-script-location --no-dependencies gvm-tools && \
sudo_execute cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*