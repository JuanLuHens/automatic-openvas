#!/usr/bin/env python3
import sys
import argparse
import os
from pathlib import Path
import requests
import msal
import os, json

def lee_config(dato):
    try:
        with open("/home/redteam/gvm/Config/config.json", 'r') as archivo:
            configuracion = json.load(archivo)
            return str(configuracion.get(dato, "SITE_NO_DEFINIDO"))
    except FileNotFoundError:
        return "ERROR_NO_FILE"
    except json.JSONDecodeError:
        return "ERROR_JSON"
    except Exception:
        return "ERROR_DESCONOCIDO"



# ==== CONFIGURACIÓN ====

SITE = (lee_config("site"))
TENANT_ID = (lee_config("tenant_id"))
CLIENT_ID = (lee_config("client_id"))
CLIENT_SECRET = (lee_config("client_secret"))

SITE_HOSTNAME = "atentoglobal.sharepoint.com"
SITE_PATH = "/sites/RedTeam"   # Ruta de tu sitio


def informa(msg):
    print (Color.GREEN + "[" + Color.RED + "+" + Color.GREEN + "] " +  msg)

# ==== AUTENTICACIÓN ====
def get_token():
    """Obtiene un access_token con Client Credentials Flow"""
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}"
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        print(f"[ERROR] No se pudo obtener token: {result}", file=sys.stderr)
        sys.exit(1)

    #print("Access_Token : " + result["access_token"])
    return result["access_token"]

# ==== GRAPH HELPERS ====
def get_site_id(token):
    """Obtiene el site-id del sitio RedTeam"""
    url = f"https://graph.microsoft.com/v1.0/sites/{SITE_HOSTNAME}:{SITE_PATH}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        print(f"[ERROR] No se pudo obtener site-id: {resp.text}", file=sys.stderr)
        sys.exit(1)
    #print("Site_ID : " + resp.json()["id"])
    return resp.json()["id"]

def get_drive_id(token, site_id):
    """Obtiene el drive-id de la biblioteca Documents"""
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        print(f"[ERROR] No se pudo obtener drives: {resp.text}", file=sys.stderr)
        sys.exit(1)

    drives = resp.json().get("value", [])
    for d in drives:
        if d.get("name") in ["Documents"]:
            return d["id"]

    print("[ERROR] No se encontró la biblioteca 'Documents'", file=sys.stderr)
    sys.exit(1)
 

def upload_file(token, site_id, drive_id, local_path, remote_path, overwrite=False):
    """Sube archivo a SharePoint usando Graph API"""
    file_name = Path(local_path).name
    with open(local_path, "rb") as f:
        data = f.read()

    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{remote_path}/{file_name}:/content"

    if not overwrite:
        url += "?@microsoft.graph.conflictBehavior=fail"
    else:
        url += "?@microsoft.graph.conflictBehavior=replace"

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.put(url, headers=headers, data=data)

    if resp.status_code not in (200, 201):
        print(f"[ERROR] Falló subida: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] Archivo subido: {resp.json()['webUrl']}")

# ==== MAIN ====
def main():
    parser = argparse.ArgumentParser(description="Subida a SharePoint con Graph API (App-Only Auth)")
    parser.add_argument("-f", "--file", required=True, help="Ruta local del archivo a subir")
    parser.add_argument("-p", "--pais", required=True, help="Nombre del país para carpeta")
    parser.add_argument("-a", "--automatizacion", required=True, help="Nombre de la automatización para carpeta")
    #parser.add_argument("--overwrite", action="store_true", help="Sobrescribir archivo si existe")

    args = parser.parse_args()
    lp = Path(args.file)
    if not lp.is_file():
        print(f"[ERROR] Archivo no encontrado: {lp}", file=sys.stderr)
        sys.exit(1)

    # Construir ruta de destino en SharePoint
    remote_path = f"General/Subidas/{args.pais}/{args.automatizacion}/{SITE}"

    # Obtener token y site/drive ids
    token = get_token()
    site_id = get_site_id(token)
    drive_id = get_drive_id(token, site_id)

    #print(f"[INFO] Subiendo {lp} a {remote_path} (site={site_id}, drive={drive_id})")
    upload_file(token, site_id, drive_id, str(lp), remote_path, overwrite=True)

if __name__ == "__main__":
    main()
 
