import requests
import json
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def email(version, configuracion, resultado):
    smtp_server = configuracion.get('mailserver')
    smtp_user = configuracion.get('smtp_user')
    smtp_pass = configuracion.get('smtp_pass')
    smtp_port = 587  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    pais = configuracion.get('pais')
    subject = f'[{pais}]Script automatizado de Openvas actualizado {version}'
    message = f'''<html>
    <head></head>
    <body>
    <p>El script automatizado de openvas se ha actualizado con el siguiente resultado:</p>
    <p>{resultado}</p>
    </body>
    </html>
    '''
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'html'))
#    smtp = smtplib.SMTP(smtp_server, smtp_port)
#    smtp.sendmail(from_address, to_address, msg.as_string())
#    smtp.quit()
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
                return 0
        else:
            print(f"Error en la solicitud. Código de estado: {response.status_code}")
            return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0
        
def leer_configuracion(fichero):
    try:
        with open(fichero, 'r') as archivo:
            configuracion = json.load(archivo)
            return configuracion
    except FileNotFoundError:
        print("El archivo 'config.json' no se encontró.")
        return 0
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")
        return 0
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return 0

url_github = "https://raw.githubusercontent.com/JuanLuHens/automatic-openvas/main/Config/config_example.json"
version_github = get_version_github(url_github)
configuracion = leer_configuracion('/home/redteam/gvm/Config/config_example.json')
version_local = configuracion.get('version')
if(version_github == 0 or version_local == 0):
    print("No se puede comprobar la version")
else:
    if(version_github==version_local):
        print("Misma version")
    else:
        print("Diferente version")
        config = leer_configuracion('/home/redteam/gvm/Config/config.json')
        resultado = subprocess.run(["git","pull"], cwd='/home/redteam/gvm/', capture_output=True, text=True)
        email(version_github, config, resultado)
    
