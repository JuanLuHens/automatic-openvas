#!/bin/bash
sudo -v
print("Definición directorios de instalación")
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && \
export BUILD_DIR=$HOME/build && \
export INSTALL_DIR=$HOME/install

export GVM_VERSION=$1

print("Configuración de Redis " + $GVM_VERSION)
sudo cp $SOURCE_DIR/openvas-scanner-$GVM_VERSION/config/redis-openvas.conf /etc/redis/ && \
sudo chown redis:redis /etc/redis/redis-openvas.conf && \
echo "db_address = /run/redis-openvas/redis.sock" | sudo tee -a /etc/openvas/openvas.conf
print("Arrancamos servicios Redis")
sudo systemctl start redis-server@openvas.service && \
sudo systemctl enable redis-server@openvas.service