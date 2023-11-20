import pytz

from datetime import datetime

from icalendar import Calendar, Event
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

for i in range(1,31):
    cal = Calendar()
    

    cal.add('prodid', '-//Foo Bar//')
    cal.add('version', '2.0')

    event = Event()
    event.add('dtstamp', datetime.now(tz=pytz.UTC))
    #year, month, day
    event.add('dtstart', datetime(2023, 11, i, hour=23, minute=00,tzinfo=pytz.utc))
    event.add('rrule', {"freq": "monthly"})

    cal.add_component(event)
    # using the with statement to automatically connect and disconnect to gvmd
    with Gmp(connection=connection) as gmp:
        response = gmp.get_version()
        print(response)
        gmp.authenticate(user,password)
        respuesta=gmp.create_schedule(
            name="Dia {0}".format(i),
            icalendar=cal.to_ical(),
            timezone='UTC'
        )
        print(respuesta)
    del cal