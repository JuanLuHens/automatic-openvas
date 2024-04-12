#!/bin/bash
#
# Instalador de openvas 01/01/2024 para ubuntu 22.04.03
#  _____           _        _           _            
# |_   _|         | |      | |         | |           
#   | |  _ __  ___| |_ __ _| | __ _  __| | ___  _ __ 
#   | | | '_ \/ __| __/ _` | |/ _` |/ _` |/ _ \| '__|
#  _| |_| | | \__ \ || (_| | | (_| | (_| | (_) | |   
# |_____|_| |_|___/\__\__,_|_|\__,_|\__,_|\___/|_|   
#  / __ \              \ \    / /                    
# | |  | |_ __   ___ _ _\ \  / /_ _ ___              
# | |  | | '_ \ / _ \ '_ \ \/ / _` / __|             
# | |__| | |_) |  __/ | | \  / (_| \__ \             
#  \____/| .__/ \___|_|_|_|\/ \__,_|___/             
# |  __ \| |     | | |__   __|                       
# | |__) |_|_  __| |    | | ___  __ _ _ __ ___       
# |  _  // _ \/ _` |    | |/ _ \/ _` | '_ ` _ \      
# | | \ \  __/ (_| |    | |  __/ (_| | | | | | |     
# |_|  \_\___|\__,_|    |_|\___|\__,_|_| |_| |_|     Atento 2024
#
#
#                                                

password=$1
sudo_execute() {
    echo "$password" | sudo -S "$@"
}

sudo_execute -v
echo "Instalación de dependencias"
sudo_execute apt-get update && \
sudo_execute apt-get -y upgrade && \
sudo_execute apt-get install -y build-essential && \
sudo_execute apt-get install -y cmake pkg-config gcc-mingw-w64 \
libgnutls28-dev libxml2-dev libssh-gcrypt-dev libunistring-dev \
libldap2-dev libgcrypt20-dev libpcap-dev libglib2.0-dev libgpgme-dev libradcli-dev libjson-glib-dev \
libksba-dev libical-dev libpq-dev libsnmp-dev libpopt-dev libnet1-dev gnupg gnutls-bin \
libmicrohttpd-dev redis-server libhiredis-dev openssh-client xsltproc nmap \
bison postgresql postgresql-server-dev-all smbclient fakeroot sshpass wget \
heimdal-dev dpkg rsync zip rpm nsis socat libbsd-dev snmp uuid-dev curl gpgsm \
python3 python3-paramiko python3-lxml python3-defusedxml python3-pip python3-psutil python3-impacket \
python3-setuptools python3-packaging python3-wrapt python3-cffi python3-redis python3-gnupg \
xmlstarlet texlive-fonts-recommended texlive-latex-extra perl-base xml-twig-tools \
libpaho-mqtt-dev python3-paho-mqtt mosquitto xmltoman doxygen

echo "Creacion usuario y grupo GVM"
sudo_execute useradd -r -M -U -G sudo_execute -s /usr/sbin/nologin gvm && \
echo "$password" | sudo_execute passwd --stdin gvm && \
sudo_execute usermod -aG gvm $USER && su $USER

echo "Importar la clave de firma GVM para validar la integridad de los archivos de origen"
curl -f -L https://www.greenbone.net/GBCommunitySigningKey.asc -o /tmp/GBCommunitySigningKey.asc && \
gpg --import /tmp/GBCommunitySigningKey.asc

echo "Editar la clave de firma GVM para confiar en última instancia"
echo "8AE4BE429B60A59B311C2E739823FAA60ED1E580:6:" > /tmp/ownertrust.txt && \
gpg --import-ownertrust < /tmp/ownertrust.txt