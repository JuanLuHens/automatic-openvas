#!/bin/bash
sudo -v
echo "Definición directorios de instalación"
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && \
export BUILD_DIR=$HOME/build && \
export INSTALL_DIR=$HOME/install

export GVM_VERSION=$1

echo "Descarga y verificacion de PG-GVM $GVM_VERSION"
export PG_GVM_VERSION=$GVM_VERSION
curl -f -L https://github.com/greenbone/pg-gvm/archive/refs/tags/v$PG_GVM_VERSION.tar.gz -o $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/pg-gvm/releases/download/v$PG_GVM_VERSION/pg-gvm-$PG_GVM_VERSION.tar.gz.asc -o $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz.asc $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz
echo "Extraer, compilar e instalar"
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/pg-gvm && cd $BUILD_DIR/pg-gvm && \
cmake $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION \
-DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
-DCMAKE_BUILD_TYPE=Release \
-DPostgreSQL_TYPE_INCLUDE_DIR=/usr/include/postgresql && \
make DESTDIR=$INSTALL_DIR install && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*