from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
import xml.etree.ElementTree as ET
import getpass
import datetime
import smtplib
import os, json
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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

def get_pass():
    password = getpass.getpass(prompt="Enter password: ")
    return password

def write_log(mensaje, log):
    mensaje_tiempo=f"{datetime.datetime.now()} - {mensaje}\n"
    with open(log, "a") as archivo:
        archivo.write(mensaje_tiempo)
        print(mensaje_tiempo)
        
def email(file1, file2, configuracion):
    smtp_server = configuracion.get('mailserver')
    smtp_port = 25  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    region = configuracion.get('region')
    subject = f'[{region}]Openvas tasks finalizadas'
    message = """<html>
    <head></head>
    <body>
    <p>Se han finalizado las tasks de la region. Recuerde exportar los reportes.</p>
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

    # Adjuntar file2.txt
    file2_attachment = open(file2, 'rb')
    file2_mime = MIMEBase('application', 'octet-stream')
    file2_mime.set_payload(file2_attachment.read())
    encoders.encode_base64(file2_mime)
    file2_mime.add_header('Content-Disposition', f'attachment; filename=taskslog.txt')
    msg.attach(file2_mime)
    file2_attachment.close()
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.sendmail(from_address, to_address, msg.as_string())
    smtp.quit()

def connect_gvm():
    # path to unix socket
    path = "/run/gvmd/gvmd.sock"
    connection = UnixSocketConnection(path=path)
    return connection


def start_task(connection, user, password, configuracion):
    informacion_tareas = []
    logfinal='/home/redteam/gvm/tasksend.txt'
    tasklog='/home/redteam/gvm/taskslog.txt'
    with Gmp(connection=connection) as gmp:
        gmp.authenticate(user,password)
        respuesta = gmp.get_tasks(filter_string='status="Running" status="Requested" status="Queued"')
        root = ET.fromstring(respuesta)
        for task_elem in root.findall(".//task"):
            task_id = task_elem.get("id")
            name = task_elem.findtext("name")
            status = task_elem.findtext("status")
            if(status=='Running' or status=='Requested' or status=='Queued'):
                write_log("La tarea {0} con id {1} está corriendo aun. Finalizamos script.".format(name,task_id),tasklog)
                return 1
        respuesta = gmp.get_tasks(filter_string='status="New"')
        root = ET.fromstring(respuesta)
        for task_elem in root.findall(".//task"):
            task_id = task_elem.get("id")
            name = task_elem.findtext("name")
            status = task_elem.findtext("status")
            if(status=='New'):
                write_log("Arrancamos la tarea {0} con id {1}".format(name,task_id),tasklog)
                starttask=gmp.start_task(task_id)
                write_log(starttask, tasklog)
                return 2
        respuesta = gmp.get_tasks(filter_string='rows=-1')
        root = ET.fromstring(respuesta)
        for task_elem in root.findall(".//task"):
            task_id = task_elem.get("id")
            name = task_elem.findtext("name")
            status = task_elem.findtext("status")
            current_report_elem = task_elem.find(".//last_report/report")
            if current_report_elem is not None:
                report_id = current_report_elem.get("id")
                timestamp = current_report_elem.findtext("timestamp")
                scan_start = current_report_elem.findtext("scan_start")
                scan_end = current_report_elem.findtext("scan_end")
                print("Task ID:", task_id)
                print("Name:", name)
                print("Status:", status)
                print("Report ID:", report_id)
                print("Timestamp:", timestamp)
                print("Scan Start:", scan_start)
                print("Scan End:", scan_end)
                print("-----------------------------")
                informacion_tarea = {
                        "report_id": report_id,
                        "name": name,
                        "status": status,
                        "timestamp": timestamp,
                        "scan_start": scan_start,
                        "scan_end": scan_end
                }
                informacion_tareas.append(informacion_tarea)
        if os.path.exists(logfinal):
            return 0
        else:
            #enviar email una vez finalizado con los logs y los reportes.
            with open(logfinal, "w") as archivo:
                for informacion_tarea in informacion_tareas:
                    archivo.write(str(informacion_tarea) + "\n")
            print("Todas las tareas finalizadas")
            email(logfinal, tasklog, configuracion)
            print("Exportamos las tasks")
            subprocess.run(["python3", "/home/redteam/gvm/Reports/get-reports-test.py"])
        return 0

configuracion = leer_configuracion()
user = configuracion.get('user')
password = configuracion.get('password')
connection = connect_gvm()
resultado=start_task(connection,user,password,configuracion)
if(resultado==0):
    print("Finalizamos sin lanzar")
elif(resultado==1):
    print("Ya hay una corriendo")
elif(resultado==2):
    print("Arrancamos una nueva")

