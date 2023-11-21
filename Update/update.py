import requests
import subprocess
import os
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def email(version):
    smtp_server = 'SERVIDOR CORREO'
    smtp_port = 25  # Puerto 25 para autenticación anónima
    from_address = 'FROM'
    to_address = 'DESTINER'
    subject = f'[EMEA]OpenVas Scanner actualizado {version} xxxxxx'
    message = """<html>
    <head></head>
    <body>
    <p>El OpenVas Scanner de EMEA se ha actualizado.</p>
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