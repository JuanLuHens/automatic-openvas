
#Installing boto3 pip3 install boto3
import boto3
import awscli
import os, json
from botocore.exceptions import ClientError
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import subprocess
import datetime

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


def write_log(mensaje, log):
    mensaje_tiempo=f"{datetime.datetime.now()} - {mensaje}\n"
    with open(log, "a") as archivo:
        archivo.write(mensaje_tiempo)
        print(mensaje_tiempo)

def awsResource(aws_access_key_id, aws_secret_access_key): 
    session = boto3.Session(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    return session

def awsConnect(aws_access_key_id, aws_secret_access_key):
    #global accessKey, secretKey
    awsconnect=boto3.client('s3',region_name='us-west-2',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    return awsconnect

def listbucket(s3bucket, tasklog, session):
    
    s3 = session.resource('s3')
    try:
        my_bucket = s3.Bucket(s3bucket)
        for my_bucket_object in my_bucket.objects.all():
            #print(my_bucket_object.key)
            for file_name in fileList:
                file=os.path.basename(file_name)
                if file in my_bucket_object.key:
                    write_log(f"El fichero '{file}' se encuentra en el objeto '{my_bucket_object.key}'", tasklog)
    except Exception as error:
        print (error)  


def uploadfile(s3bucket, filelist, tasklog, s3):
    for file_name in filelist:
        write_log(f"Subiendo fichero {file_name} ...", tasklog)
        try:
            test = s3.upload_file(file_name,s3bucket,"connectors/190/205/6d68d695-48f9-435a-90a7-8eada9b82f28/"+os.path.basename(file_name))
            write_log("Success", tasklog)    
        except Exception as error:
            print (error)
            
def email(file1, configuracion):
    file_name=os.path.basename(file1)
    smtp_user = configuracion.get('smtp_user')
    smtp_pass = configuracion.get('smtp_pass')
    smtp_server = configuracion.get('mailserver')
    smtp_port = 587  # Puerto 25 para autenticación anónima
    from_address = configuracion.get('from')
    to_address = configuracion.get('to')
    pais = configuracion.get('pais')

    subject = f'Openvas Scan {pais}'
    message = """<html>
    <head></head>
    <body>
    <p>Buenos dias,</p>
    <p>Finalizadas las subidas</p>
    <p>Se adjunta el log de subida a Balbix.</p>
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
    file1_mime.add_header('Content-Disposition', f'attachment; filename={file_name}')
    msg.attach(file1_mime)
    file1_attachment.close()
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


if __name__ == '__main__':

    #fileList2 = ["/home/redteam/gvm/Reports/exports/2024_02_07_15_19_CVE.csv"]
    fileList = sys.argv[1:]
    configuracion = leer_configuracion()
    s3bucket = configuracion.get('s3bucket')
    aws_access_key_id = configuracion.get('aws_access_key_id')
    aws_secret_access_key = configuracion.get('aws_secret_access_key')
    session = awsResource(aws_access_key_id, aws_secret_access_key)
    s3=awsConnect(aws_access_key_id, aws_secret_access_key)
    tasklog='/home/redteam/gvm/logbalbix.txt'
    if os.path.exists(tasklog):
        os.remove(tasklog)
    uploadfile(s3bucket, fileList, tasklog, s3)
    listbucket(s3bucket, tasklog, session)
    email(tasklog, configuracion)
    #email(fileList[0], fileList[1], configuracion)
    print("Borramos reportes y comenzamos de nuevo")
    #subprocess.run(["python3", "/home/redteam/gvm/Targets_Tasks/delete-files.py"])

