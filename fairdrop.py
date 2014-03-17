#!/usr/bin/env python

from gi.repository import Gtk
import os
from avahi_server import ZeroconfService
from avahi_client import ZeroconfClient

class FairdropApp:
    def __init__(self):
        self.configure()
        self.get_widget_references()
        self.wireup_signals()
        self.start_avahi_server()
        self.start_avahi_client()
        self.window.show_all()

    def configure(self):
        self.gladefile = "fairdrop.glade"
        # HACK
        self.receiver_ip = "192.168.1.9"
        self.receiver_port = "7538"

    def get_widget_references(self):
        builder = Gtk.Builder()
        builder.add_from_file(self.gladefile)
        self.window = builder.get_object("mainwindow")
        self.filechooserbutton = builder.get_object("filechooserbutton")
        self.sendfilebutton = builder.get_object("sendfilebutton")

    def wireup_signals(self):
        self.window.connect("delete-event", self.close_app)
        self.filechooserbutton.connect("file-set", self.on_source_file_set)
        self.sendfilebutton.connect("clicked", self.on_send_file_button_clicked)

    # Handlers

    def on_send_file_button_clicked(self, button):
        self.send_file()
        dialog = self.build_file_sent_info_dialog();
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return None

    def on_source_file_set(self, button):
        self.source_file = self.filechooserbutton.get_filename()

    def close_app(self, event, user_data):
        self.service.unpublish()
        Gtk.main_quit()

    # Helpers

    def build_file_sent_info_dialog(self):
        return Gtk.MessageDialog(self.window,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK,
                "File sent")

    def send_file(self):
        command = "pv \"" + self.source_file + "\" | nc -v " + self.receiver_ip + " " + self.receiver_port
        print "Running command: " + command
        os.system(command)
        #nmap -p7538 192.168.1.*

    def start_avahi_server(self):
        self.service = ZeroconfService(name="FairdropService", port=self.receiver_port)
        self.service.publish()

    def start_avahi_client(self):
        self.client = ZeroconfClient()
        self.client.list_servers()

# Main

app = FairdropApp()
Gtk.main()
