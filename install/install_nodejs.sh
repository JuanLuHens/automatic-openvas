#!/bin/bash

echo "Definición directorios de instalación"
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && \
export BUILD_DIR=$HOME/build && \
export INSTALL_DIR=$HOME/install
password=$1
sudo_execute() {
    echo "$password" | sudo -S "$@"
}
echo "Instalación de nodejs14.x"
export NODE_VERSION=node_14.x && \
export KEYRING=/usr/share/keyrings/nodesource.gpg && \
export DISTRIBUTION="$(lsb_release -s -c)" && \
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor > /tmp/nodesource.gpg && \
sudo_execute cp /tmp/nodesource.gpg "$KEYRING" && \
rm /tmp/nodesource.gpg && \
gpg --no-default-keyring --keyring "$KEYRING" --list-keys && \
echo "deb [signed-by=$KEYRING] https://deb.nodesource.com/$NODE_VERSION $DISTRIBUTION main" | tee /tmp/nodesource.list && \
echo "deb-src [signed-by=$KEYRING] https://deb.nodesource.com/$NODE_VERSION $DISTRIBUTION main" | tee -a /tmp/nodesource.list && \
sudo_execute mv /tmp/nodesource.list /etc/apt/sources.list.d/nodesource.list && \
sudo_execute apt update && \
sudo_execute apt install -y nodejs

echo "Instalación de yarn"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor > /tmp/yarnpkg.gpg && \
sudo_execute cp /tmp/yarnpkg.gpg /usr/share/keyrings/yarnpkg.gpg && \
rm /tmp/yarnpkg.gpg && \
echo "deb [signed-by=/usr/share/keyrings/yarnpkg.gpg] https://dl.yarnpkg.com/debian/ stable main" | tee /tmp/yarnpkg.list && \
sudo_execute mv /tmp/yarnpkg.list /etc/apt/sources.list.d/yarn.list && \
sudo_execute apt update && \
sudo_execute apt install -y yarn