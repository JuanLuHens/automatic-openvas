import requests
import json
import subprocess
def get_version_github(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            version = json_data.get("version")
            if version:
                return version
            else:
                print("No se encontró la clave 'version' en el JSON.")
        else:
            print(f"Error en la solicitud. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
        
def leer_configuracion():
    try:
        with open('/home/redteam/gvm/Config/config_example.json', 'r') as archivo:
            configuracion = json.load(archivo)
            return configuracion
    except FileNotFoundError:
        print("El archivo 'config.json' no se encontró.")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

url_github = "https://raw.githubusercontent.com/JuanLuHens/automatic-openvas/main/Config/config_example.json"
version_github = get_version_github(url_github)
configuracion = leer_configuracion()
version_local = configuracion.get('version')

if(version_github==version_local):
    print("Misma version")
else:
    print("Diferente version")
    subprocess.run(["git","pull"], cwd='/home/redteam/gvm/')