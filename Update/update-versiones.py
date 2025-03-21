import requests
import subprocess
import os, json
import sys, time, select
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import datetime
import smtplib

def write_log(mensaje, log):
    mensaje_tiempo=f"{datetime.datetime.now()} - {mensaje}\n"
    with open(log, "a") as archivo:
        archivo.write(mensaje_tiempo)
        print(mensaje_tiempo)
        
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

def email(file1, configuracion, cuerpoemail):
    smtp_server = configuracion.get('mailserver')
    smtp_user = configuracion.get('smtp_user')
    smtp_pass = configuracion.get('smtp_pass')
    smtp_port = 587  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    pais = configuracion.get('pais')
    subject = f'[{pais}]Openvas Updates finalizado'
    message = f"""<html>
    <head></head>
    <body>
    <p>Se han finalizado los updates. Revise el log adjunto.</p>
    <p>A continuacion resumen de la actualizacion:</p>
    <p></p>
    <p>{cuerpoemail}</p>
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
    # Adjuntar file1.txt
    file1_attachment = open(file1, 'rb')
    file1_mime = MIMEBase('application', 'octet-stream')
    file1_mime.set_payload(file1_attachment.read())
    encoders.encode_base64(file1_mime)
    file1_mime.add_header('Content-Disposition', f'attachment; filename=tasksend.txt')
    msg.attach(file1_mime)
    file1_attachment.close()
    #smtp = smtplib.SMTP(smtp_server, smtp_port)
    #smtp.sendmail(from_address, to_address, msg.as_string())
    #smtp.quit()
    try:
        # Establece la conexión con el servidor
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.ehlo()  # Identifícate con el servidor
        smtp.starttls()  # Inicia la conexión TLS
        smtp.ehlo()  # Vuelve a identificarse como una conexión segura
        smtp.login(smtp_user, smtp_pass)  # Inicia sesión en el servidor SMTP

        # Envía el correo
        smtp.sendmail(from_address, to_address, msg.as_string())
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    finally:
        # Cierra la conexión
        smtp.quit()

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

def actualizar(modulo, version, logupdate):
    if (modulo=='OPENVAS_SCANNER_VERSION'):
        salida = os.system("bash /home/redteam/gvm/Update/update-scanner.sh " + version)
        if(get_openvas_scanner_version(logupdate, nversion)==2):
            installok=1
        else:
            installok=0
        return installok


def compara(modulo, nversion, logupdate):
    switcher = {
        'OPENVAS_SCANNER_VERSION': get_openvas_scanner_version,
        'NOTUS_VERSION': get_notus_version,
    }
    func = switcher.get(modulo, default_case)
    if(func(logupdate, nversion)==1):
        return actualizar(modulo, nversion, logupdate)
    else:
        return 0

def get_notus_version(logupdate, nversion):
    return "No implementado"   

def default_case(logupdate, nversion):
    return "Invalid case."     

def get_openvas_scanner_version(logupdate, nversion):
    retorno=0
    try:
        result = subprocess.run(['openvas', '-V'], capture_output=True, text=True, check=True)
        output = result.stdout
        for line in output.split('\n'):
            print (line)
            if 'OpenVAS' in line:
                version = line.split()[1]
                write_log(f"OpenVAS Scanner Version: {version}", logupdate)
                if (nversion==version):
                    write_log("OpenVAS Scanner Version son la misma version", logupdate)
                    return 2
                else:
                    write_log("OpenVAS Scanner Version son versiones diferentes se procede a actualizar", logupdate)
                    return 1
        write_log("Version Openvas Scanner no encontrada.", logupdate)
        return 0
    except subprocess.CalledProcessError as e:
        write_log(f"Error ejecuntando openvas -V: {e}", logupdate)
        return 0
    except Exception as e:
        write_log(f"OpenVAS Scanner Version ha ocurrido un error: {e}", logupdate)
        return 0
    
def get_version_github(url, logupdate):
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
                write_log("No se localiza la versión", logupdate)
                return False
        else:
            print(f"Error en la solicitud. Código de estado: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
logupdate='/home/redteam/logupdates.txt'
versiones={}
configuracion = leer_configuracion()
#s3bucket = configuracion.get('s3bucket')
urls={'GVM_LIBS_VERSION':'https://github.com/greenbone/gvm-libs/releases','GVMD_VERSION':'https://github.com/greenbone/gvmd/releases','PG_GVM_VERSION':'https://github.com/greenbone/pg-gvm/releases','GSA_VERSION':'https://github.com/greenbone/gsa/releases/','GSAD_VERSION':'https://github.com/greenbone/gsad/releases/','OPENVAS_SMB_VERSION':'https://github.com/greenbone/openvas-smb/releases','OPENVAS_SCANNER_VERSION':'https://github.com/greenbone/openvas-scanner/releases','OSPD_OPENVAS_VERSION':'https://github.com/greenbone/ospd-openvas/releases','NOTUS_VERSION':'https://github.com/greenbone/notus-scanner/releases','REDIS_VERSION':'https://github.com/greenbone/openvas-scanner/releases'}
for key, url in urls.items():
    version=''
    print(f'obtenemos última versión de {key} en github')
    version=get_version_github(url, logupdate)
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
cuerpoemail=''
for key, nversion in versiones.items():
    if(key=='OPENVAS_SCANNER_VERSION'):#para testear la funcion
        if(compara(key, nversion, logupdate)):
            cuerpoemail+=f'La actualizacion de {key} a la version {nversion} ha sido correcta'
            write_log(f'La actualizacion de {key} a la version {nversion} ha sido correcta', logupdate)
        else:
            cuerpoemail+=f'ERROR. La actualizacion de {key} a la version {nversion} ha fallado'
            write_log(f'ERROR. La actualizacion de {key} a la version {nversion} ha fallado', logupdate)
print('Finalizadas las actualizaciones, se procede a enviar email')
email(logupdate,configuracion, cuerpoemail)
