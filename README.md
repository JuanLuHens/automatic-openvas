# Automatic OpenVAS Installation and Configuration

Este proyecto automatiza la instalación y configuración de OpenVAS, así como la gestión de tareas y objetivos. A continuación se detallan los pasos necesarios para instalar y configurar el sistema.

## Instalación

```bash
# Clonar el repositorio desde GitHub:
git clone https://github.com/JuanLuHens/automatic-openvas

# Renombrar la carpeta a "gvm":
mv automatic-openvas gvm

# Ingresar al directorio "gvm" y configurar el entorno virtual:
cd gvm
python3 -m venv gvm
source gvm/bin/activate

# Si no existe `python3.10-venv`, instalar según la versión:
sudo apt install python3.10-venv

# Instalar dependencias:
pip3 install -r requirements.txt

# Ingresar al directorio "install" y ejecutar el script de instalación:
cd install
chmod +x install.sh
./install.sh

```
Si despues de la instalación, el servicio gsad.service da error, modificar el fichero
/etc/systemd/system/multi-user.target.wants/gsad.service
Y borrar de ExecStart:
```
-f --drop-privileges=gvm
```
Y ejecutamos:
```
sudo systemctl daemon-reload
sudo service gsad restart
```
#### Para cambiar la contraseña de gvmd:
```
gvmd --user=admin --new-password=
```
## Configuración
Si existieran tasks o targets anteriores, borrarlos.
#### Configuración de Targets y Tasks