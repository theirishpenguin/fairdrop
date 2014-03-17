#!/usr/bin/env python

from gi.repository import Gtk
import os
from avahi_server import ZeroconfService
from avahi_client import ZeroconfClient
import subprocess

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
        self.receiver_port = "7538"

    def get_widget_references(self):
        builder = Gtk.Builder()
        builder.add_from_file(self.gladefile)
        self.window = builder.get_object("mainwindow")
        self.filechooserbutton = builder.get_object("filechooserbutton")
        self.sendfilebutton = builder.get_object("sendfilebutton")
        self.destinationcomboboxtext = builder.get_object("destinationcomboboxtext")
        self.outputlogtextview = builder.get_object("outputlogtextview")

    def wireup_signals(self):
        self.window.connect("delete-event", self.close_app)
        self.filechooserbutton.connect("file-set", self.on_source_file_set)
        self.sendfilebutton.connect("clicked", self.on_send_file_button_clicked)

    # Handlers

    def on_send_file_button_clicked(self, button):
        self.send_file()
        # No longer using dialog - just look at the output area - delete soon
        #dialog = self.build_file_sent_info_dialog();
        #response = dialog.run()
        #dialog.destroy()
        #if response == Gtk.ResponseType.OK:
        #    return None

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

    # HACK - just one big hack!
    def send_file(self):
        #import pdb; pdb.set_trace()
        destination_text = self.destinationcomboboxtext.get_active_text()
        if len(destination_text) > 0:
            [destintation_hostname, destintation_address, destination_port] = destination_text.split('~')
            command = "pv \"" + self.source_file + "\" | nc -v " + destintation_address + " " + destination_port
            a_buffer = self.outputlogtextview.get_buffer()
            a_buffer.insert(a_buffer.get_end_iter(), "Running command: " + command + "\n")
            a_buffer.insert(a_buffer.get_end_iter(), "Check output at the console to see what happened\n")
            os.system(command)
            #for line in self.run_command(command):
             #   print(line)
             #   a_buffer.insert(a_buffer.get_end_iter(), line)
            #import pdb; pdb.set_trace()
        else:
            print "No destintation selected"

# HACK - not currently used
#    def run_command(self, command):
#        p = subprocess.Popen(command,
#            stdout=subprocess.PIPE,
#            stderr=subprocess.STDOUT)
#        return iter(p.stdout.readline, b'')

    def start_avahi_server(self):
        self.service = ZeroconfService(name="FairdropService", port=self.receiver_port)
        self.service.publish()

    def start_avahi_client(self):
        self.client = ZeroconfClient(app=self)
        self.client.listen_for_servers()

# Main

app = FairdropApp()
Gtk.main()
