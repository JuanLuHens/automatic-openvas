from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
import xml.etree.ElementTree as ET
import getpass

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
    respuesta=gmp.get_port_lists()
    root = ET.fromstring(respuesta)
    port_lists = root.findall('.//port_list')
    for port_list in port_lists:
        id = port_list.get('id')
        name = port_list.find('name').text
        print(f'ID: {id}')
        print(f'Name: {name}')
        print(f'------')
