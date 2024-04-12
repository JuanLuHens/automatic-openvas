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

echo "Descarga y verificacion de GSA $GVM_VERSION"
export GSA_VERSION=$GVM_VERSION && \
curl -f -L https://github.com/greenbone/gsa/archive/refs/tags/v$GSA_VERSION.tar.gz -o $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gsa/releases/download/v$GSA_VERSION/gsa-$GSA_VERSION.tar.gz.asc -o $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz.asc $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz

echo "Extraer, compilar e instalar"
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz && \
cd $SOURCE_DIR/gsa-$GSA_VERSION && rm -rf build && \
yarn && yarn build && \
sudo_execute mkdir -p $INSTALL_PREFIX/share/gvm/gsad/web/ && \
sudo_execute cp -r build/* $INSTALL_PREFIX/share/gvm/gsad/web/