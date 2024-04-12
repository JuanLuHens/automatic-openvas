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

echo "Descarga y verificacion de GSAD $GVM_VERSION"
export GSAD_VERSION=$GVM_VERSION && \
curl -f -L https://github.com/greenbone/gsad/archive/refs/tags/v$GSAD_VERSION.tar.gz -o $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gsad/releases/download/v$GSAD_VERSION/gsad-$GSAD_VERSION.tar.gz.asc -o $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz.asc $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz

echo "Extraer, compilar e instalar"
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/gsad && cd $BUILD_DIR/gsad && \
cmake $SOURCE_DIR/gsad-$GSAD_VERSION \
-DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
-DCMAKE_BUILD_TYPE=Release \
-DSYSCONFDIR=/etc \
-DLOCALSTATEDIR=/var \
-DGVMD_RUN_DIR=/run/gvmd \
-DGSAD_RUN_DIR=/run/gsad \
-DLOGROTATE_DIR=/etc/logrotate.d && \
make DESTDIR=$INSTALL_DIR install && \
sudo_execute cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*