from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
import xml.etree.ElementTree as ET
import getpass
import os

def get_pass():
    password=getpass.getpass(prompt='Enter password: ')
    return password

user = 'admin'
password = get_pass()
# path to unix socket
path = '/run/gvmd/gvmd.sock'
connection = UnixSocketConnection(path=path)

# using the with statement to automatically connect and disconnect to gvmd
with Gmp(connection=connection) as gmp:
    response = gmp.get_version()
    print(response)
    gmp.authenticate(user,password)
    respuesta = gmp.get_reports(filter_string='rows=1500')
    root = ET.fromstring(respuesta)
    reports = root.findall(".//report")
    for report in reports:
        report_id = report.get("id")
        task = report.find(".//task")
        task_id = task.get("id")
        task_name = task.find("name").text
        print("Reporte a borrar")
        print("Report ID:", report_id)
        print("Task ID:", task_id)
        print("Task Name:", task_name)
        respuesta= gmp.delete_report(report_id)
        print(respuesta)
    if os.path.exists('/home/redteam/gvm/tasksend.txt'):
        os.remove('/home/redteam/gvm/tasksend.txt')
    if os.path.exists('/home/redteam/gvm/taskslog.txt'):
        os.remove('/home/redteam/gvm/taskslog.txt')
