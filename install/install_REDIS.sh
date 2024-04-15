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
echo "Configuración de Redis $GVM_VERSION"
sudo_execute -v
sudo_execute cp $SOURCE_DIR/openvas-scanner-$GVM_VERSION/config/redis-openvas.conf /etc/redis/ && \
sudo_execute chown redis:redis /etc/redis/redis-openvas.conf && \
echo "db_address = /run/redis-openvas/redis.sock" | sudo tee -a /etc/openvas/openvas.conf
echo "Arrancamos servicios Redis"
sudo_execute systemctl start redis-server@openvas.service && \
sudo_execute systemctl enable redis-server@openvas.service