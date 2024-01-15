import requests
import subprocess
import os, json
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def email(version, configuracion):
    smtp_server = configuracion.get('mailserver')
    smtp_port = 25  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    region = configuracion.get('region')
    subject = f'[{region}]OpenVas Scanner actualizado {version}'
    message = """<html>
    <head></head>
    <body>
    <p>El OpenVas Scanner se ha actualizado.</p>
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.sendmail(from_address, to_address, msg.as_string())
    smtp.quit()

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

configuracion = leer_configuracion()
url="https://github.com/greenbone/openvas-scanner/releases"
response = requests.get(url)
parser = BeautifulSoup(response.content, "html.parser")
version= parser.find("span",class_="ml-1 wb-break-all")
control=0
if version:
    soloversionconv=version.text.strip()
    if(soloversionconv.startswith("v")):
        soloversion=soloversionconv[1:]
    else:
        soloversion=soloversionconv
    print(soloversion)
    control=1
else:
    control=0
    print("no encuentro")

with open("/home/redteam/gvm/Update/version.txt", "r") as f:
    versionanterior = f.read()
if (control==1):
    with open("/home/redteam/gvm/Update/version.txt","w") as f:
        if(versionanterior != soloversion):
            print(versionanterior)
            f.write(soloversion)
            salida = os.system("bash /home/redteam/gvm/Update/update-scanner.sh " + soloversion)
            print(salida)
            email(soloversion)
        else:
            f.write(versionanterior)