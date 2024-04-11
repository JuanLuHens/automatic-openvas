#!/bin/bash
sudo -v
echo "Definición directorios de instalación"
export PATH=$PATH:/usr/local/sbin && export INSTALL_PREFIX=/usr/local && \
export SOURCE_DIR=$HOME/source && \
export BUILD_DIR=$HOME/build && \
export INSTALL_DIR=$HOME/install

echo "Configuración servicio mosquitto"
sudo systemctl start mosquitto.service && \
sudo systemctl enable mosquitto.service && \
echo "mqtt_server_uri = localhost:1883" | sudo tee -a /etc/openvas/openvas.conf

echo "Creacion de los directorios faltantes"
sudo -v
sudo mkdir -p /var/lib/notus && \
sudo mkdir -p /run/notus-scanner && \
sudo mkdir -p /run/gvmd

echo "Añadir gvm al grupo de redis y permisos"
sudo -v
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

echo "ajustar permisos del feed"
sudo -v
sudo chown gvm:gvm /usr/local/bin/greenbone-nvt-sync && \
sudo chmod 740 /usr/local/sbin/greenbone-feed-sync && \
sudo chown gvm:gvm /usr/local/sbin/greenbone-*-sync && \
sudo chmod 740 /usr/local/sbin/greenbone-*-sync

echo "Validación feed"
sudo -v
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

echo "Permitir a los usuarios del grupo GVM poder lanzar openvas"
sudo -v
# allow users of the gvm group run openvas
sudo echo -e "gvm ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers


echo "Arrancamos postgresql"
sudo -v
sudo systemctl start postgresql@14-main.service

# Setup PostgreSQL
sudo -u postgres -H sh -c "createuser -DRS gvm ;\
createdb -O gvm gvmd ;\
psql -U postgres -c 'create role dba with superuser noinherit;' ;\
psql -U postgres -c 'grant dba to gvm;' ;\
psql -U postgres gvmd -c 'create extension \"uuid-ossp\";' ;\
psql -U postgres gvmd -c 'create extension \"pgcrypto\";' ;\
psql -U postgres gvmd -c 'create extension \"pg-gvm\";' "


echo "Recargamos loader cache dinamica"
sudo -v
sudo ldconfig

echo "Creamos usuario admin/admin"
sudo gvmd --create-user=admin --password=admin

## Retrieve our administrators uuid
#sudo gvmd --get-users --verbose
#admin 0279ba6c-391a-472f-8cbd-1f6eb808823b

## Set the value using the administrators uuid
#sudo gvmd --modify-setting 78eceaec-3385-11ea-b237-28d24461215b --value UUID_HERE
sudo gvmd --get-users --verbose | awk '{print $2}' | xargs -I {} sudo gvmd --modify-setting 78eceaec-3385-11ea-b237-28d24461215b --value {}
#read -p "Comprueba comando sudo gvmd --modify-setting 78eceaec-3385-11ea-b237-28d24461215b --value"
# NVT sync. This might take awhile.
echo "Actualizamos el feed"
sudo -v
sudo -u gvm greenbone-nvt-sync
sudo -v
# Update Greenbone Feed Sync (run the commands one by one as GVM user). This might take awhile.
sudo -u gvm greenbone-feed-sync --type GVMD_DATA
sudo -v
sudo -u gvm greenbone-feed-sync --type SCAP
sudo -v
sudo -u gvm greenbone-feed-sync --type CERT

echo "Generamos los certificados https"
sudo -v
sudo -u gvm gvm-manage-certs -a

echo "Creamos servicio gvmd"
sudo -v
echo W1VuaXRdCkRlc2NyaXB0aW9uPUdyZWVuYm9uZSBWdWxuZXJhYmlsaXR5IE1hbmFnZXIgZGFlbW9uIChndm1kKQpBZnRlcj1uZXR3b3JrLnRhcmdldCBuZXR3b3JraW5nLnNlcnZpY2UgcG9zdGdyZXNxbC5zZXJ2aWNlIG9zcGQtb3BlbnZhcy5zZXJ2aWNlCldhbnRzPXBvc3RncmVzcWwuc2VydmljZSBvc3BkLW9wZW52YXMuc2VydmljZQpEb2N1bWVudGF0aW9uPW1hbjpndm1kKDgpCkNvbmRpdGlvbktlcm5lbENvbW1hbmRMaW5lPSFyZWNvdmVyeQoKW1NlcnZpY2VdClR5cGU9Zm9ya2luZwpVc2VyPWd2bQpHcm91cD1ndm0KUElERmlsZT0vcnVuL2d2bWQvZ3ZtZC5waWQKUnVudGltZURpcmVjdG9yeT1ndm1kClJ1bnRpbWVEaXJlY3RvcnlNb2RlPTI3NzUKRXhlY1N0YXJ0PS91c3IvbG9jYWwvc2Jpbi9ndm1kIC0tb3NwLXZ0LXVwZGF0ZT0vcnVuL29zcGQvb3NwZC1vcGVudmFzLnNvY2sgLS1saXN0ZW4tZ3JvdXA9Z3ZtClJlc3RhcnQ9YWx3YXlzClRpbWVvdXRTdG9wU2VjPTEwCgpbSW5zdGFsbF0KV2FudGVkQnk9bXVsdGktdXNlci50YXJnZXQK | base64 -d > $BUILD_DIR/gvmd.service

sudo cp $BUILD_DIR/gvmd.service /etc/systemd/system/

## GSAD systemd
echo "Creamos servicio GSAD"
sudo -v
echo W1VuaXRdCkRlc2NyaXB0aW9uPUdyZWVuYm9uZSBTZWN1cml0eSBBc3Npc3RhbnQgZGFlbW9uIChnc2FkKQpEb2N1bWVudGF0aW9uPW1hbjpnc2FkKDgpIGh0dHBzOi8vd3d3LmdyZWVuYm9uZS5uZXQKQWZ0ZXI9bmV0d29yay50YXJnZXQgZ3ZtZC5zZXJ2aWNlCldhbnRzPWd2bWQuc2VydmljZQoKW1NlcnZpY2VdClR5cGU9Zm9ya2luZwpVc2VyPWd2bQpHcm91cD1ndm0KUnVudGltZURpcmVjdG9yeT1nc2FkClJ1bnRpbWVEaXJlY3RvcnlNb2RlPTI3NzUKUElERmlsZT0vcnVuL2dzYWQvZ3NhZC5waWQKRXhlY1N0YXJ0PS91c3IvbG9jYWwvc2Jpbi9nc2FkIC1mIC0tZHJvcC1wcml2aWxlZ2VzPWd2bSAgLS1saXN0ZW49Q0FNQklBIC0tcG9ydD00NDMKUmVzdGFydD1vbi1mYWlsdXJlClRpbWVvdXRTdG9wU2VjPTEwClJlc3RhcnRTZWM9Mm1pbgpLaWxsTW9kZT1wcm9jZXNzCktpbGxTaWduYWw9U0lHSU5UCkd1ZXNzTWFpblBJRD1ubwpQcml2YXRlVG1wPXRydWUKCltJbnN0YWxsXQpXYW50ZWRCeT1tdWx0aS11c2VyLnRhcmdldApBbGlhcz1ncmVlbmJvbmUtc2VjdXJpdHktYXNzaXN0YW50LnNlcnZpY2UK | base64 -d | sed "s/CAMBIA/$(hostname -I)/g" > $BUILD_DIR/gsad.service

sudo cp $BUILD_DIR/gsad.service /etc/systemd/system/

echo "Creamos servicio ospd-openvas"
sudo -v
echo W1VuaXRdCkRlc2NyaXB0aW9uPU9TUGQgV3JhcHBlciBmb3IgdGhlIE9wZW5WQVMgU2Nhbm5lciAob3NwZC1vcGVudmFzKQpEb2N1bWVudGF0aW9uPW1hbjpvc3BkLW9wZW52YXMoOCkgbWFuOm9wZW52YXMoOCkKQWZ0ZXI9bmV0d29yay50YXJnZXQgbmV0d29ya2luZy5zZXJ2aWNlIHJlZGlzLXNlcnZlckBvcGVudmFzLnNlcnZpY2UKV2FudHM9cmVkaXMtc2VydmVyQG9wZW52YXMuc2VydmljZQpDb25kaXRpb25LZXJuZWxDb21tYW5kTGluZT0hcmVjb3ZlcnkKCltTZXJ2aWNlXQpUeXBlPWZvcmtpbmcKVXNlcj1ndm0KR3JvdXA9Z3ZtClJ1bnRpbWVEaXJlY3Rvcnk9b3NwZApSdW50aW1lRGlyZWN0b3J5TW9kZT0yNzc1ClBJREZpbGU9L3J1bi9vc3BkL29zcGQtb3BlbnZhcy5waWQKRXhlY1N0YXJ0PS91c3IvbG9jYWwvYmluL29zcGQtb3BlbnZhcyAtLXVuaXgtc29ja2V0IC9ydW4vb3NwZC9vc3BkLW9wZW52YXMuc29jayAtLXBpZC1maWxlIC9ydW4vb3NwZC9vc3BkLW9wZW52YXMucGlkIC0tbG9nLWZpbGUgL3Zhci9sb2cvZ3ZtL29zcGQtb3BlbnZhcy5sb2cgLS1sb2NrLWZpbGUtZGlyIC92YXIvbGliL29wZW52YXMgLS1zb2NrZXQtbW9kZSAwbzc3MCAtLW1xdHQtYnJva2VyLWFkZHJlc3MgbG9jYWxob3N0IC0tbXF0dC1icm9rZXItcG9ydCAxODgzIC0tbm90dXMtZmVlZC1kaXIgL3Zhci9saWIvbm90dXMvYWR2aXNvcmllcwpTdWNjZXNzRXhpdFN0YXR1cz1TSUdLSUxMClJlc3RhcnQ9YWx3YXlzClJlc3RhcnRTZWM9NjAKCltJbnN0YWxsXQpXYW50ZWRCeT1tdWx0aS11c2VyLnRhcmdldAo= | base64 -d > $BUILD_DIR/ospd-openvas.service

sudo cp $BUILD_DIR/ospd-openvas.service /etc/systemd/system/

echo "Creamos servicio notus"
sudo -v
echo W1VuaXRdCkRlc2NyaXB0aW9uPU5vdHVzIFNjYW5uZXIKRG9jdW1lbnRhdGlvbj1odHRwczovL2dpdGh1Yi5jb20vZ3JlZW5ib25lL25vdHVzLXNjYW5uZXIKQWZ0ZXI9bW9zcXVpdHRvLnNlcnZpY2UKV2FudHM9bW9zcXVpdHRvLnNlcnZpY2UKQ29uZGl0aW9uS2VybmVsQ29tbWFuZExpbmU9IXJlY292ZXJ5CgpbU2VydmljZV0KVHlwZT1mb3JraW5nClVzZXI9Z3ZtClJ1bnRpbWVEaXJlY3Rvcnk9bm90dXMtc2Nhbm5lcgpSdW50aW1lRGlyZWN0b3J5TW9kZT0yNzc1ClBJREZpbGU9L3J1bi9ub3R1cy1zY2FubmVyL25vdHVzLXNjYW5uZXIucGlkCkV4ZWNTdGFydD0vdXNyL2xvY2FsL2Jpbi9ub3R1cy1zY2FubmVyIC0tcHJvZHVjdHMtZGlyZWN0b3J5IC92YXIvbGliL25vdHVzL3Byb2R1Y3RzIC0tbG9nLWZpbGUgL3Zhci9sb2cvZ3ZtL25vdHVzLXNjYW5uZXIubG9nClN1Y2Nlc3NFeGl0U3RhdHVzPVNJR0tJTEwKUmVzdGFydD1hbHdheXMKUmVzdGFydFNlYz02MAoKW0luc3RhbGxdCldhbnRlZEJ5PW11bHRpLXVzZXIudGFyZ2V0Cg== | base64 -d > $BUILD_DIR/notus-scanner.service

sudo cp $BUILD_DIR/notus-scanner.service /etc/systemd/system/

echo "Activamos servicios"
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

echo "Comprobamos status de los servicios"
sudo systemctl status notus-scanner
sudo systemctl status ospd-openvas.service
sudo systemctl status gvmd.service
sudo systemctl status gsad.service

echo "Configuramos Cron"
chmod +x /home/redteam/gvm/Cron/*.ssh
sudo -v
sudo cp /home/redteam/gvm/Cron/actualiza_gvm.sh /usr/bin/
sudo cp /home/redteam/gvm/Cron/cron-update.sh /usr/bin/

echo "0 22 * * 6 /usr/bin/actualiza_gvm.sh" | sudo crontab -e
echo "0 23 * * 6 /usr/bin/cron-update.sh" | sudo crontab -e



