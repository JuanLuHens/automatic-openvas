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