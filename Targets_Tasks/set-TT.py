import pandas as pd
import getpass
import xml.etree.ElementTree as ET
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
from gvm.protocols.gmpv208.entities.hosts import HostsOrdering

def load_csv(file):
    df = pd.read_csv(file, delimiter=';')
    return df

def get_pass():
    password=getpass.getpass(prompt='Enter password: ')
    return password

def connect_gvm():
    # path to unix socket
    path = '/run/gvmd/gvmd.sock'
    connection = UnixSocketConnection(path=path)
    return connection

def ready_target(connection,user,password,df):
    rangos_duplicados = {}
    # using the with statement to automatically connect and disconnect to gvmd
    with Gmp(connection=connection) as gmp:
        # get the response message returned as a utf-8 encoded string
        response = gmp.get_version()
        root=ET.fromstring(response)
        status = root.get('status')
        version = root.find('version').text
        print(f'Status: {status}')
        print(f'Version: {version}')
        gmp.authenticate(user,password)
        for index, row in df.iterrows():
            titulo = row['Titulo']
            rango = row['Rango']
            desc = row['Desc']
            if titulo in rangos_duplicados:
                rangos_duplicados[titulo]['rangos'].append(rango)
            else:
                rangos_duplicados[titulo] = {'rangos': [rango], 'desc': desc}
        with open('log.txt','w+') as log_file:
            for titulo, datos in rangos_duplicados.items():
                desc = datos['desc']
                if (len(datos['rangos']) > 9):
                    j=0
                    for i in range(0,len(datos['rangos']),9 ):
                        rangos=datos['rangos'][i:i+9]
                        titulocontador = f'{titulo}_{j}'
                        create_target(titulocontador,rangos,desc,gmp,log_file)
                        j+=1
                else:
                    rangos=datos['rangos']
                    create_target(titulo,rangos,desc,gmp,log_file)
                    
def create_target(titulo, rangos, desc,gmp,log_file):
    print(f'[TARGET]Título: {titulo}, Rangos: {rangos}, Descripción: {desc}')
    response_create=gmp.create_target(name=titulo,hosts=rangos,comment=desc,port_list_id='4c647224-00d3-4563-afb8-f516fd396451')
    create_xml= ET.fromstring(response_create)
    status_target = create_xml.get('status')
    status_target_text = create_xml.get('status_text')
    id_target = create_xml.get('id')
    print(f'Status: {status_target}')
    print(f'Status Text: {status_target_text}')
    print(f'ID: {id_target}')
    log_file.write(f'[TARGET]Título: {titulo};Rangos: {rangos};Status: {status_target}; Status Text: {status_target_text};ID: {id_target}\n')
    if (status_target == '201'):
        create_task(titulo,id_target,desc,gmp,log_file)

def create_task(name,id,desc,gmp,log_file):
    task_preferences = {
        "max_checks": "2",
        "max_hosts": "5"
    }
    scan_order = HostsOrdering.RANDOM
    print(f'[TASK]Título: {name}, Descripción: {desc}')
    # config id for full and fast daba56c8-73ec-11df-a475-002264764cea
    configid = 'daba56c8-73ec-11df-a475-002264764cea'
    # scanner id for openvas default 08b69003-5fc2-4037-a479-93b440211c73
    scannerid = '08b69003-5fc2-4037-a479-93b440211c73'
    responsetask=gmp.create_task(name=name,config_id=configid,target_id=id,scanner_id=scannerid,comment=desc, hosts_ordering=scan_order, preferences=task_preferences)
    create_xml= ET.fromstring(responsetask)
    status_task = create_xml.get('status')
    status_task_text = create_xml.get('status_text')
    id_task = create_xml.get('id')
    print(f'Status: {status_task}')
    print(f'Status Text: {status_task_text}')
    print(f'ID: {id_task}')
    log_file.write(f'[TASK]Título: {name};Status: {status_task}; Status Text: {status_task_text};ID: {id_task}\n')

if __name__ == '__main__':
    username = 'admin'
    password = get_pass()
    file= "openvas.csv"
    df = load_csv(file)
    connection= connect_gvm()
    ready_target(connection,username,password,df)
