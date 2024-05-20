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
            email(soloversion, configuracion)
        else:
            f.write(versionanterior)
            
awscli==1.32.36
bcrypt==4.1.2
beautifulsoup4==4.12.2
boto3==1.34.36
botocore==1.34.36
bs4==0.0.1
certifi==2023.7.22
cffi==1.16.0
charset-normalizer==3.3.1
colorama==0.4.4
cryptography==41.0.7
defusedxml==0.7.1
docutils==0.16
icalendar==5.0.11
idna==3.4
jmespath==1.0.1
lxml==5.1.0
numpy==1.26.3
pandas==2.1.1
paramiko==3.4.0
pyasn1==0.5.1
pycparser==2.21
PyNaCl==1.5.0
python-dateutil==2.8.2
python-gvm==23.10.0
pytz==2023.3.post1
PyYAML==6.0.1
requests==2.31.0
rsa==4.7.2
s3transfer==0.10.0
six==1.16.0
soupsieve==2.5
tzdata==2023.4
untangle==1.2.1
urllib3==2.0.7
