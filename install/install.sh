#!/bin/bash
#
# Instalador de openvas 23/09/2024 para ubuntu 22.04.04
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
                                                    
sudo -v

# Install dependencies
sudo apt-get update && \
sudo apt-get -y upgrade && \
sudo apt-get install -y build-essential && \
sudo apt-get install -y pkg-config gcc-mingw-w64 \
libgnutls28-dev libxml2-dev libssh-gcrypt-dev libunistring-dev libcurl4-openssl-dev \
libldap2-dev libgcrypt20-dev libpcap-dev libglib2.0-dev libgpgme-dev libradcli-dev libjson-glib-dev \
libksba-dev libical-dev libpq-dev libsnmp-dev libpopt-dev libnet1-dev gnupg gnutls-bin \
libmicrohttpd-dev redis-server libhiredis-dev openssh-client xsltproc nmap \
bison postgresql postgresql-server-dev-all smbclient fakeroot sshpass wget \
heimdal-dev dpkg rsync zip rpm nsis socat libbsd-dev snmp uuid-dev curl gpgsm \
python3 python3-paramiko python3-lxml python3-defusedxml python3-pip python3-psutil python3-impacket \
python3-setuptools python3-packaging python3-wrapt python3-cffi python3-redis python3-gnupg \
xmlstarlet texlive-fonts-recommended texlive-latex-extra perl-base xml-twig-tools \
libpaho-mqtt-dev python3-paho-mqtt mosquitto xmltoman doxygen clang-format jq libcjson-dev libkrb5-dev

# Create GVM user and group
sudo useradd -r -M -U -G sudo -s /usr/sbin/nologin gvm && \
sudo usermod -aG gvm $USER

GVM_LIBS_VERSION=$(jq -r '.GVM_LIBS_VERSION' /home/redteam/resultado.json)
GVMD_VERSION=$(jq -r '.GVMD_VERSION' /home/redteam/resultado.json)
PG_GVM_VERSION=$(jq -r '.PG_GVM_VERSION' /home/redteam/resultado.json)
GSA_VERSION=$(jq -r '.GSA_VERSION' /home/redteam/resultado.json)
GSAD_VERSION=$(jq -r '.GSAD_VERSION' /home/redteam/resultado.json)
OPENVAS_SMB_VERSION=$(jq -r '.OPENVAS_SMB_VERSION' /home/redteam/resultado.json)
OPENVAS_SCANNER_VERSION=$(jq -r '.OPENVAS_SCANNER_VERSION' /home/redteam/resultado.json)
OSPD_OPENVAS_VERSION=$(jq -r '.OSPD_OPENVAS_VERSION' /home/redteam/resultado.json)
NOTUS_VERSION=$(jq -r '.NOTUS_VERSION' /home/redteam/resultado.json)
REDIS_VERSION=$(jq -r '.OPENVAS_SCANNER_VERSION' /home/redteam/resultado.json)
echo $GVM_LIBS_VERSION
echo $GVMD_VERSION
echo $PG_GVM_VERSION
echo $GSA_VERSION
echo $GSAD_VERSION
echo $OPENVAS_SMB_VERSION
echo $OPENVAS_SCANNER_VERSION
echo $OSPD_OPENVAS_VERSION
echo $NOTUS_VERSION
echo $REDIS_VERSION
# Define installation directories
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && mkdir -p $SOURCE_DIR && \
export BUILD_DIR=$HOME/build && mkdir -p $BUILD_DIR && \
export INSTALL_DIR=$HOME/install && mkdir -p $INSTALL_DIR
sleep 5
# Import GVM signing key to validate the integrity of the source files
curl -f -L https://www.greenbone.net/GBCommunitySigningKey.asc -o /tmp/GBCommunitySigningKey.asc && \
gpg --import /tmp/GBCommunitySigningKey.asc

# Edit GVM signing key to trust ultimately
echo "8AE4BE429B60A59B311C2E739823FAA60ED1E580:6:" > /tmp/ownertrust.txt && \
gpg --import-ownertrust < /tmp/ownertrust.txt

# Set GVM version
sudo -v
# Download and verify the GVM librarires

curl -f -L https://github.com/greenbone/gvm-libs/archive/refs/tags/v$GVM_LIBS_VERSION.tar.gz -o $SOURCE_DIR/gvm-libs-$GVM_LIBS_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gvm-libs/releases/download/v$GVM_LIBS_VERSION/gvm-libs-v$GVM_LIBS_VERSION.tar.gz.asc -o $SOURCE_DIR/gvm-libs-$GVM_LIBS_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gvm-libs-$GVM_LIBS_VERSION.tar.gz.asc $SOURCE_DIR/gvm-libs-$GVM_LIBS_VERSION.tar.gz

# Extract, build and install
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/gvm-libs-$GVM_LIBS_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/gvm-libs && cd $BUILD_DIR/gvm-libs && \
cmake $SOURCE_DIR/gvm-libs-$GVM_LIBS_VERSION \
  -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
  -DCMAKE_BUILD_TYPE=Release \
  -DSYSCONFDIR=/etc \
  -DLOCALSTATEDIR=/var && \
make DESTDIR=$INSTALL_DIR install && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*
sudo -v
# Set version, Download and verify GVMD

curl -f -L https://github.com/greenbone/gvmd/archive/refs/tags/v$GVMD_VERSION.tar.gz -o $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gvmd/releases/download/v$GVMD_VERSION/gvmd-$GVMD_VERSION.tar.gz.asc -o $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz.asc $SOURCE_DIR/gvmd-$GVMD_VERSION.tar.gz

# Extract, build and install
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

# pg-gvm

curl -f -L https://github.com/greenbone/pg-gvm/archive/refs/tags/v$PG_GVM_VERSION.tar.gz -o $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/pg-gvm/releases/download/v$PG_GVM_VERSION/pg-gvm-$PG_GVM_VERSION.tar.gz.asc -o $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz.asc $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz

tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/pg-gvm && cd $BUILD_DIR/pg-gvm && \
cmake $SOURCE_DIR/pg-gvm-$PG_GVM_VERSION \
  -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
  -DCMAKE_BUILD_TYPE=Release \
  -DPostgreSQL_TYPE_INCLUDE_DIR=/usr/include/postgresql && \
make DESTDIR=$INSTALL_DIR install && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*
sudo -v
# Install NodeJS v18.x
# Obtener la distribución
DISTRIBUTION="$(lsb_release -s -c)"
echo $DISTRIBUTION
# Comprobar si la distribución es Kali
if echo "$DISTRIBUTION" | grep -q "kali"; then
    echo "kali"
    sudo apt update && \
    sudo apt install -y nodejs npm
else
    echo "ubuntu"
    export NODE_VERSION=node_18.x && \
    export KEYRING=/usr/share/keyrings/nodesource.gpg && \
    export DISTRIBUTION="$(lsb_release -s -c)" && \
    #curl -fsSL https://deb.nodesource.com/gpgkey/nodesource.gpg.key | gpg --dearmor | sudo tee "$KEYRING" >/dev/null && \
    #gpg --no-default-keyring --keyring "$KEYRING" --list-keys && \
    #echo "deb [signed-by=$KEYRING] https://deb.nodesource.com/$NODE_VERSION $DISTRIBUTION main" | sudo tee /etc/apt/sources.list.d/nodesource.list && \
    #echo "deb-src [signed-by=$KEYRING] https://deb.nodesource.com/$NODE_VERSION $DISTRIBUTION main" | sudo tee -a /etc/apt/sources.list.d/nodesource.list && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
    sudo apt update && \
    sudo apt install -y nodejs
fi
# install yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - && \
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list && \
sudo apt update && \
sudo apt install -y yarn

# GSA

curl -f -L https://github.com/greenbone/gsa/archive/refs/tags/v$GSA_VERSION.tar.gz -o $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gsa/releases/download/v$GSA_VERSION/gsa-$GSA_VERSION.tar.gz.asc -o $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz.asc $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz

# extract build and install GSA (this may take awhile)
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/gsa-$GSA_VERSION.tar.gz && \
cd $SOURCE_DIR/gsa-$GSA_VERSION && rm -rf build && \
npm install && npm run build && \
sudo mkdir -p $INSTALL_PREFIX/share/gvm/gsad/web/ && \
sudo cp -r build/* $INSTALL_PREFIX/share/gvm/gsad/web/
sudo -v
# Set version, Download and verify GSAD

curl -f -L https://github.com/greenbone/gsad/archive/refs/tags/v$GSAD_VERSION.tar.gz -o $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/gsad/releases/download/v$GSAD_VERSION/gsad-$GSAD_VERSION.tar.gz.asc -o $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz.asc $SOURCE_DIR/gsad-$GSAD_VERSION.tar.gz

# extract build and install GSAD
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
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*
sudo -v
# Set version download and verify OpenVAS-SMB

curl -f -L https://github.com/greenbone/openvas-smb/archive/refs/tags/v$OPENVAS_SMB_VERSION.tar.gz -o $SOURCE_DIR/openvas-smb-$OPENVAS_SMB_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/openvas-smb/releases/download/v$OPENVAS_SMB_VERSION/openvas-smb-v$OPENVAS_SMB_VERSION.tar.gz.asc -o $SOURCE_DIR/openvas-smb-$OPENVAS_SMB_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/openvas-smb-$OPENVAS_SMB_VERSION.tar.gz.asc $SOURCE_DIR/openvas-smb-$OPENVAS_SMB_VERSION.tar.gz

# extract build and install openvas-smb
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/openvas-smb-$OPENVAS_SMB_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/openvas-smb && cd $BUILD_DIR/openvas-smb && \
cmake $SOURCE_DIR/openvas-smb-$OPENVAS_SMB_VERSION \
  -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
  -DCMAKE_BUILD_TYPE=Release && \
make DESTDIR=$INSTALL_DIR install && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*
#por aqui
# Download and verify openvas-scanner

curl -f -L https://github.com/greenbone/openvas-scanner/archive/refs/tags/v$OPENVAS_SCANNER_VERSION.tar.gz -o $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/openvas-scanner/releases/download/v$OPENVAS_SCANNER_VERSION/openvas-scanner-v$OPENVAS_SCANNER_VERSION.tar.gz.asc -o $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION.tar.gz.asc $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION.tar.gz
sudo -v
# extract build and install openvas-scanner
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION.tar.gz && \
mkdir -p $BUILD_DIR/openvas-scanner && cd $BUILD_DIR/openvas-scanner && \
cmake $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION \
  -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX \
  -DCMAKE_BUILD_TYPE=Release \
  -DSYSCONFDIR=/etc \
  -DLOCALSTATEDIR=/var \
  -DOPENVAS_FEED_LOCK_PATH=/var/lib/openvas/feed-update.lock \
  -DOPENVAS_RUN_DIR=/run/ospd && \
make DESTDIR=$INSTALL_DIR install && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*

# ospd-openvas

curl -f -L https://github.com/greenbone/ospd-openvas/archive/refs/tags/v$OSPD_OPENVAS_VERSION.tar.gz -o $SOURCE_DIR/ospd-openvas-$OSPD_OPENVAS_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/ospd-openvas/releases/download/v$OSPD_OPENVAS_VERSION/ospd-openvas-v$OSPD_OPENVAS_VERSION.tar.gz.asc -o $SOURCE_DIR/ospd-openvas-$OSPD_OPENVAS_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/ospd-openvas-$OSPD_OPENVAS_VERSION.tar.gz.asc $SOURCE_DIR/ospd-openvas-$OSPD_OPENVAS_VERSION.tar.gz

# extract, build and install
# Test to replace $INSTALL_PREFIX with specified path --prefix=/usr/local + remove --root=$INSTALL_DIR
# Using sudo and defining the --prefix /usr works so far but not the best approach
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/ospd-openvas-$OSPD_OPENVAS_VERSION.tar.gz && \
cd $SOURCE_DIR/ospd-openvas-$OSPD_OPENVAS_VERSION && \
sudo python3 -m pip install . --prefix /usr --no-warn-script-location --no-dependencies && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*
# notus-scanner

curl -f -L https://github.com/greenbone/notus-scanner/archive/refs/tags/v$NOTUS_VERSION.tar.gz -o $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz && \
curl -f -L https://github.com/greenbone/notus-scanner/releases/download/v$NOTUS_VERSION/notus-scanner-v$NOTUS_VERSION.tar.gz.asc -o $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz.asc && \
gpg --verify $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz.asc $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz
sudo -v
# extract, build and install
# Test to replace $INSTALL_PREFIX with specified path --prefix=/usr/local
# Using sudo and defining the --prefix /usr works so far but not the best approach
tar -C $SOURCE_DIR -xvzf $SOURCE_DIR/notus-scanner-$NOTUS_VERSION.tar.gz && \
cd $SOURCE_DIR/notus-scanner-$NOTUS_VERSION && \
sudo python3 -m pip install . --prefix /usr --no-warn-script-location --no-dependencies && \
sudo cp -rv $INSTALL_DIR/* / && \
rm -rf $INSTALL_DIR/*

# tomli module (required for notus-scanner)
sudo python3 -m pip install python-gnupg==0.5.2 --break-system-packages
sudo python3 -m pip install tomli --break-system-packages

# gvm-tools (Installing gvm-tools system-wide)
# Test to replace $INSTALL_PREFIX with specified path --prefix=/usr/local
# Using sudo and defining the --prefix /usr works so far but not the best approach
sudo python3 -m pip install --prefix /usr --no-warn-script-location --no-dependencies gvm-tools && \

# Configure Redis
sudo cp $SOURCE_DIR/openvas-scanner-$OPENVAS_SCANNER_VERSION/config/redis-openvas.conf /etc/redis/ && \
sudo chown redis:redis /etc/redis/redis-openvas.conf && \
echo "db_address = /run/redis-openvas/redis.sock" | sudo tee -a /etc/openvas/openvas.conf

sudo systemctl start redis-server@openvas.service && \
sudo systemctl enable redis-server@openvas.service
sudo -v
# Set up the Mosquitto broker
sudo systemctl start mosquitto.service && \
sudo systemctl enable mosquitto.service && \
echo "mqtt_server_uri = localhost:1883" | sudo tee -a /etc/openvas/openvas.conf

# add req. dirs
sudo mkdir -p /var/lib/notus && \
sudo mkdir -p /run/notus-scanner && \
sudo mkdir -p /run/gvmd

# add gvm to redis group and adjust permissions
sudo usermod -aG redis gvm && \
sudo chown -R gvm:gvm /var/lib/gvm && \
sudo chown -R gvm:gvm /var/lib/openvas && \
sudo chown -R gvm:gvm /var/lib/notus && \
sudo chown -R gvm:gvm /var/log/gvm && \
sudo chown -R gvm:gvm /run/gvmd && \
sudo chown -R gvm:gvm /run/notus-scanner && \
sudo chmod -R g+srw /var/lib/gvm && \
sudo chmod -R g+srw /var/lib/openvas && \
sudo chmod -R g+srw /var/log/gvm && \
sudo chown gvm:gvm /usr/local/sbin/gvmd && \
sudo chmod 6750 /usr/local/sbin/gvmd
sudo -v
# adjust permissions for feed syncs
# sudo chown gvm:gvm /usr/local/bin/greenbone-nvt-sync && \
# sudo chmod 740 /usr/local/sbin/greenbone-feed-sync && \
# sudo chown gvm:gvm /usr/local/sbin/greenbone-*-sync && \
# sudo chmod 740 /usr/local/sbin/greenbone-*-sync
sudo python3 -m pip install greenbone-feed-sync --break-system-packages


# Feed validation
export GNUPGHOME=/tmp/openvas-gnupg && \
mkdir -p $GNUPGHOME && \
gpg --import /tmp/GBCommunitySigningKey.asc && \
echo "8AE4BE429B60A59B311C2E739823FAA60ED1E580:6:" > /tmp/ownertrust.txt && \
gpg --import-ownertrust < /tmp/ownertrust.txt && \
export OPENVAS_GNUPG_HOME=/etc/openvas/gnupg && \
sudo mkdir -p $OPENVAS_GNUPG_HOME && \
sudo cp -r /tmp/openvas-gnupg/* $OPENVAS_GNUPG_HOME/ && \
sudo chown -R gvm:gvm $OPENVAS_GNUPG_HOME

# visudo
#sudo visudo

# Allow members of group sudo to execute any command
#%sudo   ALL=(ALL:ALL) ALL
sudo -v
# allow users of the gvm group run openvas
#sudo echo -e "gvm ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
sudo sh -c 'echo "gvm ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers'

# Start PostgreSQL
# Obtener la distribución
DISTRIBUTION="$(lsb_release -s -c)"
echo $DISTRIBUTION
# Comprobar si la distribución es Kali
if echo "$DISTRIBUTION" | grep -q "kali"; then
    echo "kali"
    sudo systemctl start postgresql.service
else
    echo "ubuntu"
    sudo systemctl start postgresql@16-main.service
fi


# Setup PostgreSQL
sudo -u postgres -H sh -c "createuser -DRS gvm ;\
createdb -O gvm gvmd ;\
psql -U postgres -c 'create role dba with superuser noinherit;' ;\
psql -U postgres -c 'grant dba to gvm;' ;\
psql -U postgres gvmd -c 'create extension \"uuid-ossp\";' ;\
psql -U postgres gvmd -c 'create extension \"pgcrypto\";' ;\
psql -U postgres gvmd -c 'create extension \"pg-gvm\";' "
sudo -v

# Reload dynamic loader cache
sudo ldconfig

# Create GVM admin
sudo gvmd --create-user=admin --password=admin

## Retrieve our administrators uuid
#sudo gvmd --get-users --verbose
#admin 0279ba6c-391a-472f-8cbd-1f6eb808823b
sudo -v
## Set the value using the administrators uuid
#sudo gvmd --modify-setting 78eceaec-3385-11ea-b237-28d24461215b --value UUID_HERE
sudo gvmd --get-users --verbose | awk '{print $2}' | xargs -I {} sudo gvmd --modify-setting 78eceaec-3385-11ea-b237-28d24461215b --value {}
#read -p "Comprueba comando sudo gvmd --modify-setting 78eceaec-3385-11ea-b237-28d24461215b --value"
# NVT sync. This might take awhile.
sudo -v
sudo -u gvm greenbone-nvt-sync

# Update Greenbone Feed Sync (run the commands one by one as GVM user). This might take awhile.
sudo -u gvm greenbone-feed-sync --type GVMD_DATA -vvv
sudo -u gvm greenbone-feed-sync --type SCAP -vvv
sudo -u gvm greenbone-feed-sync --type CERT -vvv
sudo -u gvm greenbone-feed-sync --type nvt -vvv

# Generate GVM certificates for HTTPS
sudo -v
sudo -u gvm gvm-manage-certs -a

## GVMD systemd
echo W1VuaXRdCkRlc2NyaXB0aW9uPUdyZWVuYm9uZSBWdWxuZXJhYmlsaXR5IE1hbmFnZXIgZGFlbW9uIChndm1kKQpBZnRlcj1uZXR3b3JrLnRhcmdldCBuZXR3b3JraW5nLnNlcnZpY2UgcG9zdGdyZXNxbC5zZXJ2aWNlIG9zcGQtb3BlbnZhcy5zZXJ2aWNlCldhbnRzPXBvc3RncmVzcWwuc2VydmljZSBvc3BkLW9wZW52YXMuc2VydmljZQpEb2N1bWVudGF0aW9uPW1hbjpndm1kKDgpCkNvbmRpdGlvbktlcm5lbENvbW1hbmRMaW5lPSFyZWNvdmVyeQoKW1NlcnZpY2VdClR5cGU9Zm9ya2luZwpVc2VyPWd2bQpHcm91cD1ndm0KUElERmlsZT0vcnVuL2d2bWQvZ3ZtZC5waWQKUnVudGltZURpcmVjdG9yeT1ndm1kClJ1bnRpbWVEaXJlY3RvcnlNb2RlPTI3NzUKRXhlY1N0YXJ0PS91c3IvbG9jYWwvc2Jpbi9ndm1kIC0tb3NwLXZ0LXVwZGF0ZT0vcnVuL29zcGQvb3NwZC1vcGVudmFzLnNvY2sgLS1saXN0ZW4tZ3JvdXA9Z3ZtClJlc3RhcnQ9YWx3YXlzClRpbWVvdXRTdG9wU2VjPTEwCgpbSW5zdGFsbF0KV2FudGVkQnk9bXVsdGktdXNlci50YXJnZXQK | base64 -d > $BUILD_DIR/gvmd.service

sudo cp $BUILD_DIR/gvmd.service /etc/systemd/system/

## GSAD systemd

#echo W1VuaXRdCkRlc2NyaXB0aW9uPUdyZWVuYm9uZSBTZWN1cml0eSBBc3Npc3RhbnQgZGFlbW9uIChnc2FkKQpEb2N1bWVudGF0aW9uPW1hbjpnc2FkKDgpIGh0dHBzOi8vd3d3LmdyZWVuYm9uZS5uZXQKQWZ0ZXI9bmV0d29yay50YXJnZXQgZ3ZtZC5zZXJ2aWNlCldhbnRzPWd2bWQuc2VydmljZQoKW1NlcnZpY2VdClR5cGU9Zm9ya2luZwpVc2VyPWd2bQpHcm91cD1ndm0KUnVudGltZURpcmVjdG9yeT1nc2FkClJ1bnRpbWVEaXJlY3RvcnlNb2RlPTI3NzUKUElERmlsZT0vcnVuL2dzYWQvZ3NhZC5waWQKRXhlY1N0YXJ0PS91c3IvbG9jYWwvc2Jpbi9nc2FkIC1mIC0tZHJvcC1wcml2aWxlZ2VzPWd2bSAgLS1saXN0ZW49Q0FNQklBIC0tcG9ydD00NDMKUmVzdGFydD1vbi1mYWlsdXJlClRpbWVvdXRTdG9wU2VjPTEwClJlc3RhcnRTZWM9Mm1pbgpLaWxsTW9kZT1wcm9jZXNzCktpbGxTaWduYWw9U0lHSU5UCkd1ZXNzTWFpblBJRD1ubwpQcml2YXRlVG1wPXRydWUKCltJbnN0YWxsXQpXYW50ZWRCeT1tdWx0aS11c2VyLnRhcmdldApBbGlhcz1ncmVlbmJvbmUtc2VjdXJpdHktYXNzaXN0YW50LnNlcnZpY2UK | base64 -d | sed "s/CAMBIA/$(hostname -I)/g" > $BUILD_DIR/gsad.service
echo W1VuaXRdCkRlc2NyaXB0aW9uPUdyZWVuYm9uZSBTZWN1cml0eSBBc3Npc3RhbnQgZGFlbW9uIChnc2FkKQpEb2N1bWVudGF0aW9uPW1hbjpnc2FkKDgpIGh0dHBzOi8vd3d3LmdyZWVuYm9uZS5uZXQKQWZ0ZXI9bmV0d29yay50YXJnZXQgZ3ZtZC5zZXJ2aWNlCldhbnRzPWd2bWQuc2VydmljZQoKW1NlcnZpY2VdClR5cGU9Zm9ya2luZwpVc2VyPWd2bQpHcm91cD1ndm0KUnVudGltZURpcmVjdG9yeT1nc2FkClJ1bnRpbWVEaXJlY3RvcnlNb2RlPTI3NzUKUElERmlsZT0vcnVuL2dzYWQvZ3NhZC5waWQKRXhlY1N0YXJ0PS91c3IvbG9jYWwvc2Jpbi9nc2FkIC0tbGlzdGVuPUNBTUJJQSAtLXBvcnQ9OTM5MgpSZXN0YXJ0PW9uLWZhaWx1cmUKVGltZW91dFN0b3BTZWM9MTAKUmVzdGFydFNlYz0ybWluCktpbGxNb2RlPXByb2Nlc3MKS2lsbFNpZ25hbD1TSUdJTlQKR3Vlc3NNYWluUElEPW5vClByaXZhdGVUbXA9dHJ1ZQoKW0luc3RhbGxdCldhbnRlZEJ5PW11bHRpLXVzZXIudGFyZ2V0CkFsaWFzPWdyZWVuYm9uZS1zZWN1cml0eS1hc3Npc3RhbnQuc2VydmljZQ== | base64 -d | sed "s/CAMBIA/$(hostname -I)/g" > $BUILD_DIR/gsad.service
sudo cp $BUILD_DIR/gsad.service /etc/systemd/system/

## ospd-openvas systemd
echo W1VuaXRdCkRlc2NyaXB0aW9uPU9TUGQgV3JhcHBlciBmb3IgdGhlIE9wZW5WQVMgU2Nhbm5lciAob3NwZC1vcGVudmFzKQpEb2N1bWVudGF0aW9uPW1hbjpvc3BkLW9wZW52YXMoOCkgbWFuOm9wZW52YXMoOCkKQWZ0ZXI9bmV0d29yay50YXJnZXQgbmV0d29ya2luZy5zZXJ2aWNlIHJlZGlzLXNlcnZlckBvcGVudmFzLnNlcnZpY2UKV2FudHM9cmVkaXMtc2VydmVyQG9wZW52YXMuc2VydmljZQpDb25kaXRpb25LZXJuZWxDb21tYW5kTGluZT0hcmVjb3ZlcnkKCltTZXJ2aWNlXQpUeXBlPWZvcmtpbmcKVXNlcj1ndm0KR3JvdXA9Z3ZtClJ1bnRpbWVEaXJlY3Rvcnk9b3NwZApSdW50aW1lRGlyZWN0b3J5TW9kZT0yNzc1ClBJREZpbGU9L3J1bi9vc3BkL29zcGQtb3BlbnZhcy5waWQKRXhlY1N0YXJ0PS91c3IvbG9jYWwvYmluL29zcGQtb3BlbnZhcyAtLXVuaXgtc29ja2V0IC9ydW4vb3NwZC9vc3BkLW9wZW52YXMuc29jayAtLXBpZC1maWxlIC9ydW4vb3NwZC9vc3BkLW9wZW52YXMucGlkIC0tbG9nLWZpbGUgL3Zhci9sb2cvZ3ZtL29zcGQtb3BlbnZhcy5sb2cgLS1sb2NrLWZpbGUtZGlyIC92YXIvbGliL29wZW52YXMgLS1zb2NrZXQtbW9kZSAwbzc3MCAtLW1xdHQtYnJva2VyLWFkZHJlc3MgbG9jYWxob3N0IC0tbXF0dC1icm9rZXItcG9ydCAxODgzIC0tbm90dXMtZmVlZC1kaXIgL3Zhci9saWIvbm90dXMvYWR2aXNvcmllcwpTdWNjZXNzRXhpdFN0YXR1cz1TSUdLSUxMClJlc3RhcnQ9YWx3YXlzClJlc3RhcnRTZWM9NjAKCltJbnN0YWxsXQpXYW50ZWRCeT1tdWx0aS11c2VyLnRhcmdldAo= | base64 -d > $BUILD_DIR/ospd-openvas.service

sudo cp $BUILD_DIR/ospd-openvas.service /etc/systemd/system/

# notus-scanner systemd
echo W1VuaXRdCkRlc2NyaXB0aW9uPU5vdHVzIFNjYW5uZXIKRG9jdW1lbnRhdGlvbj1odHRwczovL2dpdGh1Yi5jb20vZ3JlZW5ib25lL25vdHVzLXNjYW5uZXIKQWZ0ZXI9bW9zcXVpdHRvLnNlcnZpY2UKV2FudHM9bW9zcXVpdHRvLnNlcnZpY2UKQ29uZGl0aW9uS2VybmVsQ29tbWFuZExpbmU9IXJlY292ZXJ5CgpbU2VydmljZV0KVHlwZT1mb3JraW5nClVzZXI9Z3ZtClJ1bnRpbWVEaXJlY3Rvcnk9bm90dXMtc2Nhbm5lcgpSdW50aW1lRGlyZWN0b3J5TW9kZT0yNzc1ClBJREZpbGU9L3J1bi9ub3R1cy1zY2FubmVyL25vdHVzLXNjYW5uZXIucGlkCkV4ZWNTdGFydD0vdXNyL2xvY2FsL2Jpbi9ub3R1cy1zY2FubmVyIC0tcHJvZHVjdHMtZGlyZWN0b3J5IC92YXIvbGliL25vdHVzL3Byb2R1Y3RzIC0tbG9nLWZpbGUgL3Zhci9sb2cvZ3ZtL25vdHVzLXNjYW5uZXIubG9nClN1Y2Nlc3NFeGl0U3RhdHVzPVNJR0tJTEwKUmVzdGFydD1hbHdheXMKUmVzdGFydFNlYz02MAoKW0luc3RhbGxdCldhbnRlZEJ5PW11bHRpLXVzZXIudGFyZ2V0Cg== | base64 -d > $BUILD_DIR/notus-scanner.service

sudo cp $BUILD_DIR/notus-scanner.service /etc/systemd/system/

## Reload the system daemon to enable the startup scripts
sudo -v
sudo systemctl daemon-reload
sudo systemctl enable notus-scanner
sudo systemctl enable ospd-openvas
sudo systemctl enable gvmd
sudo systemctl enable gsad
sudo systemctl start notus-scanner
sudo systemctl start ospd-openvas
sudo systemctl start gvmd
sudo systemctl start gsad
sudo -v
# check status
sudo systemctl status notus-scanner
sudo systemctl status ospd-openvas.service
sudo systemctl status gvmd.service
sudo systemctl status gsad.service
