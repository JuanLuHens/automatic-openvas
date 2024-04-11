import pandas as pd
import getpass
import xml.etree.ElementTree as ET
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.xml import pretty_print
import untangle
import base64
import csv, json
from os import path
import datetime

def get_pass():
    password = getpass.getpass(prompt="Enter password: ")
    return password


def connect_gvm():
    # path to unix socket
    path = "/run/gvmd/gvmd.sock"
    connection = UnixSocketConnection(path=path, timeout=600)
    return connection


def ready_report(connection, user, password, reportformat):
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
        respuesta = gmp.get_reports(filter_string='rows=1500')
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
            delete_duplicates(files,export)
        else:
            print("No hay ficheros que unificar")


def noexiste(fichero):
    if path.exists(fichero):
        print("ya existe")
        return False
    else:
        return True


def guardar(fichero, data):
    with open(fichero, "w") as f:
        f.write(data)


def delete_duplicates(files, export):
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
    separar_cve(nombre_archivo)
    
def separar_cve(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    con_info = df[df['CVEs'].notnull()]
    sin_info = df[df['CVEs'].isnull()]
    con_info.to_csv(nombre_archivo.replace('.csv', '_CVE.csv'),index=False)
    sin_info.to_csv(nombre_archivo.replace('.csv', '_Misconfigs.csv'),index=False)


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


if __name__ == "__main__":
    username = "admin"
    password = get_pass()
    connection = connect_gvm()
    reportformat = get_reportformat(connection, username, password)
    ready_report(connection, username, password, reportformat)
    
