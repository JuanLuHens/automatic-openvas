#!/bin/bash
sudo -v
echo "Definición directorios de instalación"
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && \
export BUILD_DIR=$HOME/build && \
export INSTALL_DIR=$HOME/install

export GVM_VERSION=$1

echo "Descarga y verificacion de GVMD $GVM_VERSION"

export GVMD_VERSION=$GVM_VERSION && \
curl -f -L https://github.com/greenbone/gvmd/archive/refs/tags/v$GVMD_VERSION.tar.gz -o $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gvmd/releases/download/v$GVMD_VERSION/gvmd-$GVMD_VERSION.tar.gz.asc -o $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz.asc $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz

echo "Extraer, compilar e instalar"
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/gvmd && cd $BUILD_DIR/gvmd && \
cmake $SOURCE_DIR/gvmd-$GVMD_VERSION \
-DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
-DCMAKE_BUILD_TYPE=Release \
-DLOCALSTATEDIR=/var \
-DSYSCONFDIR=/etc \
-DGVM_DATA_DIR=/var \
-DOPENVAS_DEFAULT_SOCKET=/run/ospd/ospd-openvas.sock \
-DGVM_FEED_LOCK_PATH=/var/lib/gvm/feed-update.lock \
-DSYSTEMD_SERVICE_DIR=/lib/systemd/system \
-DPostgreSQL_TYPE_INCLUDE_DIR=/usr/include/postgresql \
-DLOGROTATE_DIR=/etc/logrotate.d && \
make DESTDIR=$INSTALL_DIR install && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*