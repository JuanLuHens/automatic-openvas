import requests
import subprocess
import os, json
import sys, time, select
from bs4 import BeautifulSoup

def press_anykey(timeout=5):
    print("Presiona una tecla para continuar, o espera {} segundos...".format(timeout))
    start_time = time.time()
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], timeout):
            key = sys.stdin.read(1)
            break
        elif time.time() - start_time >= timeout:
            break
    else:
        print("Continuando automáticamente...")

def get_version_github(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            parser = BeautifulSoup(response.content, "html.parser")
            version= parser.find("span",class_="ml-1 wb-break-all")
            if version:
                soloversionconv=version.text.strip()
                if(soloversionconv.startswith("v")):
                    soloversion=soloversionconv[1:]
                else:
                    soloversion=soloversionconv
                return soloversion
            else:
                print("No se localiza la versión")
                return False
        else:
            print(f"Error en la solicitud. Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")

#press_anykey()
versiones={}
password = input("Introduce la contraseña del usuario RedTeam: ")
urls={'GVM_LIBS_VERSION':'https://github.com/greenbone/gvm-libs/releases','GVMD_VERSION':'https://github.com/greenbone/gvmd/releases','PG_GVM_VERSION':'https://github.com/greenbone/pg-gvm/releases','GSA_VERSION':'https://github.com/greenbone/gsa/releases/','GSAD_VERSION':'https://github.com/greenbone/gsad/releases/','OPENVAS_SMB_VERSION':'https://github.com/greenbone/openvas-smb/releases','OPENVAS_SCANNER_VERSION':'https://github.com/greenbone/openvas-scanner/releases','OSPD_OPENVAS_VERSION':'https://github.com/greenbone/ospd-openvas/releases','NOTUS_VERSION':'https://github.com/greenbone/notus-scanner/releases','REDIS_VERSION':'https://github.com/greenbone/openvas-scanner/releases'}
for key, url in urls.items():
    version=''
    print(f'obtenemos última versión de {key} en github')
    version=get_version_github(url)
    if(version):
        versiones[key]=version
    else:
        input('Se ha encontrado un error. Revise la conexión y vuelva a lanzar el script')
        sys.exit()

for key, nversion in versiones.items():
    print(f'{key}:{nversion}')
    
archivo_json = "/home/redteam/resultado.json"
with open(archivo_json, "w") as archivo_json:
    json.dump(versiones, archivo_json)
print("Archivo JSON creado correctamente.")
press_anykey()
print("Comienza instalación")
salida_preinstall = os.system(f'bash /home/redteam/gvm/install/pre-install.sh {password}')
print(salida_preinstall)
print("Modulo NodeJS y Yarn")
press_anykey()
salidanodejs = os.system(f'bash /home/redteam/gvm/install/install_nodejs.sh {password}')
print(salidanodejs)
for key, nversion in versiones.items():
    modulo = key.replace('_VERSION','')
    print(f'Modulo {modulo}')
    press_anykey()
    salida =os.system(f'bash /home/redteam/gvm/install/install_{modulo}.sh {nversion} {password}')
    print(salida)

print("Instalación finalizada. A continuación vamos a configurar los servicios y usuario GVM")
press_anykey()
salida_posinstall = os.system(f'bash /home/redteam/gvm/install/pos-install.sh {password}')
print(salida_posinstall)
print("Finalizamos configuracion servicios GVM.")
press_anykey()
