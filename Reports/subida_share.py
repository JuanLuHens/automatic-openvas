import argparse
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import os, json

def leer_configuracion():
    try:
        with open('/home/redteam/gvm/Config/config.json', 'r') as archivo:
            configuracion = json.load(archivo)
            return configuracion
    except FileNotFoundError:
        print("El archivo 'config.json' no se encontró.")
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

def get_sharepoint_context_using_user():
    configuracion = leer_configuracion()
    username = configuracion.get('smtp_user')
    password = configuracion.get('smtp_pass')
    sharepoint_url = 'https://atentoglobal.sharepoint.com/sites/RedTeam/'
    user_credentials = UserCredential(username, password)  
    ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)
    return ctx

def upload_file_to_sharepoint(file_path, pais, automatizacion):
    ctx = get_sharepoint_context_using_user()
    folder_url = f"/sites/RedTeam/Shared Documents/General/Subidas/{pais}/{automatizacion}"
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    ctx.load(folder)
    ctx.execute_query()
    with open(file_path, 'rb') as content_file:
        upload_file = folder.upload_file(file_path.split('/')[-1], content_file.read()).execute_query()
    print(f"Fichero subido a: {upload_file.serverRelativeUrl}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subir  a SharePoint.")
    parser.add_argument("-f", "--file", required=True, type=str, help="Ruta del archivo a subir")
    parser.add_argument("-p", "--pais", required=True, type=str, help="Nombre del pais")
    parser.add_argument("-a", "--automatizacion", required=True, type=str, help="Nombre de la automatización")
    args = parser.parse_args()
    upload_file_to_sharepoint(args.file, args.pais, args.automatizacion)
