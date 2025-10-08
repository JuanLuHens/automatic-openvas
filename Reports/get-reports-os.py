import pandas as pd
import getpass
import xml.etree.ElementTree as ET
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.xml import pretty_print
import untangle
import base64
import csv, json
import os
import datetime
import subprocess
import shutil
import smtplib
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
        
def email(configuracion):
    smtp_server = configuracion.get('mailserver')
    smtp_port = 25  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    region = configuracion.get('region')
    subject = f'[{region}]Openvas Reportes generados'
    message = """<html>
    <head></head>
    <body>
    <p>Se han generado los reportes. Se procede a subirlos a balbix.</p>
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

def get_pass():
    password = getpass.getpass(prompt="Enter password: ")
    return password


def connect_gvm():
    # path to unix socket
    path = "/run/gvmd/gvmd.sock"
    connection = UnixSocketConnection(path=path, timeout=600)
    return connection


def ready_report(connection, user, password, reportformat,host):
    export = "/home/redteam/gvm/Reports/exports"
    files = []
    # using the with statement to automatically connect and disconnect to gvmd
    with Gmp(connection=connection) as gmp:
        # get the response message returned as a utf-8 encoded string
        response = gmp.get_version()
        root = ET.fromstring(response)
        status = root.get("status")
        version = root.find("version").text
        print(f"Status: {status}")
        print(f"Version: {version}")
        gmp.authenticate(user, password)
        respuesta = gmp.get_reports(filter_string='rows=1000')
        result_dict = {}
        root = ET.fromstring(respuesta)
        reports = root.findall(".//report")
        for report in reports:
            report_id = report.get("id")
            task = report.find(".//task")
            task_id = task.get("id")
            task_name = task.find("name").text
            result_dict[report_id] = {
                "report_id": report_id,
                "task_id": task_id,
                "task_name": task_name,
            }
        for key, value in result_dict.items():
            print("Report ID:", value["report_id"])
            print("Task ID:", value["task_id"])
            print("Task Name:", value["task_name"])
            print("\n")
            reportID = value["report_id"]
            name = value["task_name"]
            reportFormatID = reportformat
            print("########{0}-{1}########".format(reportID, name))
            reportscv = gmp.get_report(
                report_id=reportID,
                report_format_id=reportFormatID,
                filter_string="apply_overrides=0 min_qod=70 severity>0",
                ignore_pagination=True,
                details=True,
            )
            obj = untangle.parse(reportscv)
            resultID = obj.get_reports_response.report["id"]
            base64CVSData = obj.get_reports_response.report.cdata
            data = str(base64.b64decode(base64CVSData), "utf-8")
            fichero = "{0}/{1}.csv".format(export, resultID)
            if noexiste(fichero):
                guardar(fichero, data)
                files.append(fichero)
        if(files):
            delete_duplicates(files,export,host)
        else:
            print("No hay ficheros que unificar")
        


def noexiste(fichero):
    if os.path.exists(fichero):
        print("ya existe")
        return False
    else:
        return True


def guardar(fichero, data):
    with open(fichero, "w") as f:
        f.write(data)


def delete_duplicates(files, export,host):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    nombre_archivo = f"{export}/{year:04d}_{month:02d}_{day:02d}_{hour:02d}_{minute:02d}.csv"
    dataframes=[]
    for file in files:
        dataframes.append(pd.read_csv(file))
    columnas = ["IP", "Hostname", "Port", "Port Protocol", "CVSS", "NVT Name", "Summary", "Specific Result", "CVEs"]
    dataframe = pd.concat(dataframes,ignore_index=True)[columnas]
    dataframe = dataframe.drop_duplicates()
    dataframe.to_csv(nombre_archivo,index=False)
    file_unif= vulns_ip(nombre_archivo,host)
    separar_cve(file_unif)
    
def separar_cve(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    con_info = df[df['CVEs'].notnull()]
    sin_info = df[df['CVEs'].isnull()]
    con_info.to_csv(nombre_archivo.replace('.csv', '_CVE.csv'),index=False)
    sin_info.to_csv(nombre_archivo.replace('.csv', '_Misconfigs.csv'),index=False)
    ficheros=[nombre_archivo.replace('.csv', '_CVE.csv'), nombre_archivo.replace('.csv', '_Misconfigs.csv')]
    print("Lanzamos subida a balbix")
    subprocess.run(["python3", "/home/redteam/gvm/Reports/upload-reports.py"] + ficheros)

def get_reportformat(connection, username, password):
    with Gmp(connection=connection) as gmp:
        # reporformat=""
        gmp.authenticate(username, password)
        report_format = gmp.get_report_formats()
        report_root = ET.fromstring(report_format)
        reportsformat = report_root.findall(".//report_format")
        for report in reportsformat:
            id = report.get("id")
            name = report.find("name").text
            if name == "CSV Results":
                return id

def get_hosts(origen,destino):
    # Solicitar la contraseña de sudo
    if os.path.exists(origen):
        comando=f'sudo rm {origen}'
        subprocess.run(comando, shell=True)
    if os.path.exists(destino):
        os.remove(destino)
    comando_postgresql = f"""
    sudo -u postgres -H sh -c "psql -U postgres -d gvmd -c \
    '\\copy (SELECT DISTINCT hosts.name AS IP, oss.name AS sistema_operativo \
    FROM host_oss \
    JOIN hosts ON host_oss.host = hosts.id \
    JOIN oss ON host_oss.os = oss.id) TO '{origen}' WITH CSV HEADER;'"
    """
    subprocess.run(comando_postgresql, shell=True)
    shutil.copyfile(origen,destino)

def vulns_ip(vulns,host):
    export = '/home/redteam/gvm/Reports/exports/vulns_host'
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    nombre_archivo_csv = f"{export}/{year:04d}_{month:02d}_{day:02d}_{hour:02d}_{minute:02d}.csv"
    nombre_archivo_xlsx = f"{export}/{year:04d}_{month:02d}_{day:02d}_{hour:02d}_{minute:02d}.xlsx"
    df_ips = pd.read_csv(vulns)
    df_sistemas = pd.read_csv(host)
    sistemas_operativos = []
    for ip in df_ips['IP']:
        sistema = df_sistemas[df_sistemas['ip'] == ip]['sistema_operativo'].values
        if len(sistema) > 0:
            sistemas_operativos.append(sistema[0])
        else:
            sistemas_operativos.append('No encontrado')
    df_ips['sistema_operativo'] = sistemas_operativos
    df_ips.to_csv(nombre_archivo_csv, index=False)
    df_ips.to_excel(nombre_archivo_xlsx, index=False)
    return nombre_archivo_csv

if __name__ == "__main__":
    origen='/tmp/hosts.csv'
    destino='/home/redteam/gvm/Reports/hosts.csv'
    configuracion = leer_configuracion()
    username = configuracion.get('user')
    password = configuracion.get('password')
    connection = connect_gvm()
    get_hosts(origen,destino)
    reportformat = get_reportformat(connection, username, password)
    ready_report(connection, username, password, reportformat,destino)
    #email(configuracion)
    
