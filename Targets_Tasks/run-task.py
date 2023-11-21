from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
import xml.etree.ElementTree as ET
import getpass
import datetime

def get_pass():
    password = getpass.getpass(prompt="Enter password: ")
    return password

def write_log(mensaje, log="/home/redteam/gvm/taskslog.txt"):
    mensaje_tiempo=f"{datetime.datetime.now()} - {mensaje}\n"
    with open(log, "a") as archivo:
        archivo.write(mensaje_tiempo)
        print(mensaje_tiempo)

def connect_gvm():
    # path to unix socket
    path = "/run/gvmd/gvmd.sock"
    connection = UnixSocketConnection(path=path)
    return connection


def start_task(connection, user, password):
    informacion_tareas = []
    logfinal='/home/redteam/gvm/tasksend.txt'
    with Gmp(connection=connection) as gmp:
        gmp.authenticate(user,password)
        respuesta = gmp.get_tasks()
        root = ET.fromstring(respuesta)
        for task_elem in root.findall(".//task"):
            task_id = task_elem.get("id")
            name = task_elem.findtext("name")
            status = task_elem.findtext("status")
            if(status=='Running' or status=='Requested' or status=='Queued'):
                write_log("La tarea {0} con id {1} está corriendo aun. Finalizamos script.".format(name,task_id))
                return 1
            elif(status=='New'):
                write_log("Arrancamos la tarea {0} con id {1}".format(name,task_id))
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
# using the with statement to automatically connect and disconnect to gvmd
