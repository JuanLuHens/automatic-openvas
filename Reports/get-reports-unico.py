import pandas as pd
import getpass
import xml.etree.ElementTree as ET
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.xml import pretty_print
import untangle
import base64
import csv, json
import os, glob
import datetime
import subprocess
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ipaddress
import argparse

parser = argparse.ArgumentParser(description="Para extraer un solo reporte")
parser.add_argument("name", type=str, help="Pasa el ID de la task o el nombre completo ")

# Función para leer la configuración
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

# Función para enviar correo electrónico
def email(configuracion):
    smtp_server = configuracion.get('mailserver')
    smtp_user = configuracion.get('smtp_user')
    smtp_pass = configuracion.get('smtp_pass')
    site = configuracion.get('site')
    smtp_port = 587  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    pais = configuracion.get('pais')
    subject = f'[{pais}-{site}]Openvas Exteno Reportes generados'
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

# Función para obtener la contraseña
def get_pass():
    password = getpass.getpass(prompt="Enter password: ")
    return password

# Función para conectarse a GVM
def connect_gvm():
    path = "/run/gvmd/gvmd.sock"
    connection = UnixSocketConnection(path=path, timeout=600)
    return connection

# Función para preparar el reporte
def ready_report(connection, user, password, reportformat, host, reporte):
    export = "/home/redteam/gvm/Reports/exports"
    files = []
    with Gmp(connection=connection) as gmp:
        response = gmp.get_version()
        root = ET.fromstring(response)
        status = root.get("status")
        version = root.find("version").text
        print(f"Status: {status}")
        print(f"Version: {version}")
        gmp.authenticate(user, password)
        respuesta = gmp.get_reports(filter_string=f'~{reporte} rows=1000')
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
                filter_string="apply_overrides=1 min_qod=70 severity>0",
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
        if files:
            delete_duplicates(files, export, host)
        else:
            print("No hay ficheros que unificar")

# Función para comprobar si un fichero existe
def noexiste(fichero):
    if os.path.exists(fichero):
        print("ya existe")
        return False
    else:
        return True

# Función para guardar datos en un fichero
def guardar(fichero, data):
    with open(fichero, "w") as f:
        f.write(data)

# Función para eliminar duplicados y unificar archivos
def delete_duplicates(files, export, host):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    nombre_archivo = f"{export}/{year:04d}_{month:02d}_{day:02d}_{hour:02d}_{minute:02d}.csv"
    dataframes = []
    for file in files:
        dataframes.append(pd.read_csv(file))
    columnas = ["IP", "Hostname", "Port", "Port Protocol", "CVSS", "NVT Name", "Summary", "Specific Result", "CVEs", "Solution"]
    dataframe = pd.concat(dataframes, ignore_index=True)[columnas]
    dataframe = dataframe.drop_duplicates()
    dataframe.to_csv(nombre_archivo, index=False)
    file_unif = vulns_ip(nombre_archivo, host)
    #solo para la externa
    #print("Lanzamos subida a balbix")
    #subprocess.run(["python3", "/home/redteam/gvm/Reports/upload-reports.py"] + [file_unif])
    #fin externa
    separar_cve(file_unif)

# Función para separar CVEs y misconfiguraciones
def separar_cve(nombre_archivo):
    try:
        df = pd.read_csv(nombre_archivo)
        con_info = df[df['CVEs'].notnull()]
        sin_info = df[df['CVEs'].isnull()]
        con_info.to_csv(nombre_archivo.replace('.csv', '_CVE.csv'), index=False)
        sin_info.to_csv(nombre_archivo.replace('.csv', '_Misconfigs.csv'), index=False)
        ficheros = [nombre_archivo.replace('.csv', '_CVE.csv'), nombre_archivo.replace('.csv', '_Misconfigs.csv')]
        #print("Ya no sube a Balbix, se mantiene para la subida a Valbix")
        #subprocess.run(["python3", "/home/redteam/gvm/Reports/upload-reports.py"] + ficheros)
    except pd.errors.ParserError as pe:
        print(f"Error de análisis al procesar el archivo CSV: {pe}")
    except Exception as e:
        print(f"Error general al procesar el archivo CSV: {e}")

# Función para obtener el formato de reporte
def get_reportformat(connection, username, password):
    with Gmp(connection=connection) as gmp:
        gmp.authenticate(username, password)
        report_format = gmp.get_report_formats()
        report_root = ET.fromstring(report_format)
        reportsformat = report_root.findall(".//report_format")
        for report in reportsformat:
            id = report.get("id")
            name = report.find("name").text
            if name == "CSV Results":
                return id

# Función para obtener los hosts
def get_hosts(origen, destino):
    if os.path.exists(origen):
        comando = f'sudo rm {origen}'
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
    shutil.copyfile(origen, destino)

# Función para cargar rangos de IP y países desde un archivo CSV
def cargar_rangos_ip(archivo):
    rangos_ip = []
    with open(archivo, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Saltar el encabezado
        for row in reader:
            rango = ipaddress.ip_network(row[1], strict=False)
            pais = row[2]
            rangos_ip.append((rango, pais))
    return rangos_ip

# Función para consultar el país de una IP
def consultar_pais(ip, rangos_ip):
    ip_address = ipaddress.ip_address(ip.strip())
    for rango, pais in rangos_ip:
        if ip_address in rango:
            return pais
    return 'Desconocido'

# Función para determinar la severidad basada en el CVSS
def determinar_severidad(cvss):
    try:
        cvss = float(cvss)
        if cvss >= 9:
            return 'Critical'
        elif cvss >= 7:
            return 'High'
        elif cvss >= 4:
            return 'Medium'
        elif cvss >= 1:
            return 'Low'
        else:
            return 'Info'
    except ValueError:
        return 'Info'

def vulns_ip(vulns, host):
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
    #rangos_ip = cargar_rangos_ip('/home/redteam/gvm/Targets_Tasks/openvas_externa.csv')  # Cambia esta ruta al archivo CSV con los rangos de IP y países
    paises = []
    severidades = []
    regiones = []
    #esto es para la externa
    pais_region_map = {
            'COLOMBIA': 'SUR',
            'PERU': 'SUR',
            'ARGENTINA': 'SUR',
            'CHILE': 'SUR',
            'BAAGRI': 'NORTE',
            'EMEA': 'EMEA',
            'USNS': 'NORTE',
            'MEXICO': 'NORTE',
            'GUATEMALA': 'NORTE',
            'EL_SALVADOR': 'NORTE',
            'PUERTO_RICO': 'NORTE',
            'INTERFILE': 'BRASIL',
            'BRASIL': 'BRASIL'
        }
    #fin de regiones de la externa
    for ip, cvss in zip(df_ips['IP'], df_ips['CVSS']):
        sistema = df_sistemas[df_sistemas['ip'] == ip]['sistema_operativo'].values
        if len(sistema) > 0:
            sistemas_operativos.append(sistema[0])
        else:
            sistemas_operativos.append('No encontrado')
        #pais = consultar_pais(ip, rangos_ip)
        #pais = pais.strip()
        pais = configuracion.get('pais')
        paises.append(pais)
        severidad = determinar_severidad(cvss)
        severidades.append(severidad)
        regiones.append(pais_region_map[pais.upper()])
    
    df_ips['sistema_operativo'] = sistemas_operativos
    df_ips['Region'] = configuracion.get('region')
    df_ips['Country'] = configuracion.get('pais')
    df_ips['Scope'] = configuracion.get('scope')
    df_ips['Process'] = 'redteam-scan'
    df_ips['Owner'] = ''
    df_ips['solucion_propuesta'] = df_ips['Solution']
    df_ips['issue_type_severity'] = severidades
    df_ips = df_ips.drop(columns=['Solution'])
    df_ips.to_csv(nombre_archivo_csv, index=False)
    df_ips.to_excel(nombre_archivo_xlsx, index=False)
    return nombre_archivo_csv

if __name__ == "__main__":
    args = parser.parse_args()
    dir_csv = '/home/redteam/gvm/Reports/exports/'
    csv_files = glob.glob(os.path.join(dir_csv, '*.csv'))
    for csv_file in csv_files:
        try:
            os.remove(csv_file)
            print(f'Se ha borrado el archivo: {csv_file}')
        except OSError as e:
            print(f'Error al borrar el archivo {csv_file}: {e.strerror}')
    origen = '/tmp/hosts.csv'
    destino = '/home/redteam/gvm/Reports/hosts.csv'
    configuracion = leer_configuracion()
    username = configuracion.get('user')
    password = configuracion.get('password')
    connection = connect_gvm()
    get_hosts(origen, destino)
    reportformat = get_reportformat(connection, username, password)
    ready_report(connection, username, password, reportformat, destino, args.name)
    print("Finalizado, informe en /home/redteam/gvm/Reports/exports/exports/vulns_host")
    #email(configuracion)
