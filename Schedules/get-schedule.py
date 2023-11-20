import pytz

from datetime import datetime

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
    respuesta = gmp.get_schedule('04f2fbdf-e664-4486-b527-80dfc7663c3c')
    print(respuesta)