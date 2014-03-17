# http://avahi.org/wiki/PythonBrowseExample
import dbus, gobject, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop


class ZeroconfClient:

    def __init__(self):
        self.TYPE = "_http._tcp"

    def list_servers(self):
        #loop = DBusGMainLoop()
        #bus = dbus.SystemBus(mainloop=loop)
        bus = dbus.SystemBus()
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
        gobject.MainLoop().run()

    def service_resolved(self, *args):
        print 'service resolved'
        print 'name:', args[2]
        print 'address:', args[7]
        print 'port:', args[8]

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
