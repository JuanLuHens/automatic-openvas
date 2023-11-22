from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
import xml.etree.ElementTree as ET
import getpass
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def get_pass():
    password = getpass.getpass(prompt="Enter password: ")
    return password

def write_log(mensaje, log):
    mensaje_tiempo=f"{datetime.datetime.now()} - {mensaje}\n"
    with open(log, "a") as archivo:
        archivo.write(mensaje_tiempo)
        print(mensaje_tiempo)
        
def email(file1, file2):
    smtp_server = 'SERVIDOR CORREO'
    smtp_port = 25  # Puerto 25 para autenticación anónima
    from_address = 'FROM'
    to_address = 'DESTINER'
    subject = '[REGION]Openvas tasks finalizadas'
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
    file1_mime.add_header('Content-Disposition', f'attachment; filename=file1.txt')
    msg.attach(file1_mime)
    file1_attachment.close()

    # Adjuntar file2.txt
    file2_attachment = open(file2, 'rb')
    file2_mime = MIMEBase('application', 'octet-stream')
    file2_mime.set_payload(file2_attachment.read())
    encoders.encode_base64(file2_mime)
    file2_mime.add_header('Content-Disposition', f'attachment; filename=file2.txt')
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


def start_task(connection, user, password):
    informacion_tareas = []
    logfinal='/home/redteam/gvm/tasksend.txt'
    tasklog='/home/redteam/gvm/taskslog.txt'
    with Gmp(connection=connection) as gmp:
        gmp.authenticate(user,password)
        respuesta = gmp.get_tasks(filter_string='rows=1000')
        root = ET.fromstring(respuesta)
        for task_elem in root.findall(".//task"):
            task_id = task_elem.get("id")
            name = task_elem.findtext("name")
            status = task_elem.findtext("status")
            if(status=='Running' or status=='Requested' or status=='Queued'):
                write_log("La tarea {0} con id {1} está corriendo aun. Finalizamos script.".format(name,task_id),tasklog)
                return 1
            elif(status=='New'):
                write_log("Arrancamos la tarea {0} con id {1}".format(name,task_id),tasklog)
                starttask=gmp.start_task(task_id)
                write_log(starttask)
                return 2
            else:
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
        with open(logfinal, "w") as archivo:
            for informacion_tarea in informacion_tareas:
                archivo.write(str(informacion_tarea) + "\n")
        print("Todas las tareas finalizadas")
        #enviar email una vez finalizado con los logs y los reportes.
        #email(logfinal, tasklog)
        return 0


user = 'admin'
password = get_pass()
connection = connect_gvm()
resultado=start_task(connection,user,password)
if(resultado==0):
    print("Finalizamos sin lanzar")
elif(resultado==1):
    print("Ya hay una corriendo")
elif(resultado==2):
    print("Arrancamos una nueva")

