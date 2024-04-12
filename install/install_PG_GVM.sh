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
sudo_execute cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*

echo "Instalación de nodejs14.x"
export NODE_VERSION=node_14.x && \
export KEYRING=/usr/share/keyrings/nodesource.gpg && \
export DISTRIBUTION="$(lsb_release -s -c)" && \
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor | sudo_execute tee "$KEYRING" >/dev/null && \
gpg --no-default-keyring --keyring "$KEYRING" --list-keys && \
echo "deb [signed-by=$KEYRING] https://deb.nodesource.com/$NODE_VERSION $DISTRIBUTION main" | sudo_execute tee /etc/apt/sources.list.d/nodesource.list && \
echo "deb-src [signed-by=$KEYRING] https://deb.nodesource.com/$NODE_VERSION $DISTRIBUTION main" | sudo_execute tee -a /etc/apt/sources.list.d/nodesource.list && \
sudo_execute apt update && \
sudo_execute apt install -y nodejs


echo "Instalación de yarn"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo_execute apt-key add - && \
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo_execute tee /etc/apt/sources.list.d/yarn.list && \
sudo_execute apt update && \
sudo_execute apt install -y yarn