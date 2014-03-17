# http://avahi.org/wiki/PythonBrowseExample
import dbus, gobject, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop
import re


class ZeroconfClient:

    # HACK - ZeroconfClient should not have knowledge of app
    def __init__(self, app = None):
        self.app = app
        self.TYPE = "_http._tcp"
        self.available_clients = {}

    def listen_for_servers(self):
        loop = DBusGMainLoop()
        bus = dbus.SystemBus(mainloop=loop)
        self.server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, '/'),
                'org.freedesktop.Avahi.Server')
        sbrowser = dbus.Interface(
                bus.get_object(
                    avahi.DBUS_NAME,
                    self.server.ServiceBrowserNew(
                        avahi.IF_UNSPEC,
                        avahi.PROTO_UNSPEC,
                        self.TYPE,
                        'local',
                        dbus.UInt32(0)
                        )
                    ),
                avahi.DBUS_INTERFACE_SERVICE_BROWSER
                )
        sbrowser.connect_to_signal("ItemNew", self.myhandler)
        # HACK - Delete soon
        #gobject.MainLoop().run() # Doesn't look like we need this - perhaps implicit?

    # HACK - Needs a real cleanup
    def service_resolved(self, *args):
        service_name = args[2]
        hostname = args[5]
        address = args[7]
        port = args[8]
        client_identifier = str(hostname) + '~' +  str(address) + '~' + str(port)

        if service_name != 'FairdropService':
            return

        is_ip_address = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", address)

        if not is_ip_address:
            return

        self.available_clients[client_identifier] = {
           "hostname": hostname,
           "address": address,
           "port": port
        }

        self.app.destinationcomboboxtext.append_text(client_identifier)
        print 'service resolved'
        print 'hostname:', hostname
        print 'service_name:', service_name
        print 'address:', address
        print 'port:', port

    def print_error(self, *args):
        print 'error_handler'
        print args[0]

    def myhandler(self, interface, protocol, name, stype, domain, flags):
        print "Found service '%s' type '%s' domain '%s' " % (name, stype, domain)

        if flags & avahi.LOOKUP_RESULT_LOCAL:
            # local service, skip
            pass

        self.server.ResolveService(
                interface, protocol, name, stype, domain, avahi.PROTO_UNSPEC,
                dbus.UInt32(0), reply_handler=self.service_resolved, error_handler=self.print_error)

def test():
    client = ZeroconfClient()
    client.list_servers()

if __name__ == "__main__":
    test()
