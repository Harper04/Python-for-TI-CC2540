#!/usr/bin/env python

# Bluetooth low Energy Projekt -- Tom / Hagen

import pygtk
pygtk.require('2.0')
import gtk, gobject

# Zaehler fuer den oberen Balken
def progress_timeout(pbobj):
    if pbobj.activity_check.get_active():
        pbobj.pbar.pulse()
     
    else:
        # Calculate the value of the progress bar using the
        # value range set in the adjustment object
        new_val = pbobj.pbar.get_fraction() + 0.01
        if new_val > 1.0:
            new_val = 0.0
	
        # Set the new value
        pbobj.pbar.set_fraction(new_val)
        pbobj.xachse.set_fraction(0.5) 		#####################
	pbobj.yachse.set_fraction(0.75)		#####################
	pbobj.zachse.set_fraction(0.25)		#####################

    # As this is a timeout function, return TRUE so that it
    # continues to get called
    return True

#==========================================================
class Fenster:
    # Callback that toggles the text display within the progress
    # bar trough
    def toggle_show_text(self, widget, data=None):
        if widget.get_active():
            self.pbar.set_text("it is Working")
        else:
            self.pbar.set_text("")

    # Callback that toggles the activity mode of the progressbar

    def toggle_activity_mode(self, widget, data=None):
        if widget.get_active():
            self.pbar.pulse()
        else:
            self.pbar.set_fraction(0.0)

    # Clean up allocated memory and remove the timer
    def destroy_progress(self, widget, data=None):
        gobject.source_remove(self.timer)
        self.timer = 0
        gtk.main_quit()

#Erstellung des Fensters===================================
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(True)

        self.window.connect("destroy", self.destroy_progress)
        self.window.set_title("Bluetooth Low Energy")                   
        self.window.set_border_width(0)

        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(10)
        self.window.add(vbox)
        vbox.show()
  

        # ausrichtung/ zentrierung
        align = gtk.Alignment(0.5, 0.5, 1, 1)
        vbox.pack_start(align, False, False, 5)
        align.show()

        alignx = gtk.Alignment(0.5, 0.5, 0, 0)
        vbox.pack_start(alignx, False, False, 5)
        alignx.show()
        aligny = gtk.Alignment(0.5, 0.5, 0, 0)
        vbox.pack_start(aligny, False, False, 5)
        aligny.show()
        alignz = gtk.Alignment(0.5, 0.5, 0, 0)
        vbox.pack_start(alignz, False, False, 5)
        alignz.show()

        # Create the ProgressBar  for x, y, z achse
        self.pbar = gtk.ProgressBar()
	self.xachse = gtk.ProgressBar()
	self.yachse = gtk.ProgressBar()
	self.zachse = gtk.ProgressBar()
	self.xachse.set_text("X-Achse")
	self.yachse.set_text("Y-Achse")
	self.zachse.set_text("Z-Achse")

        align.add(self.pbar)
        self.pbar.show()
        alignx.add(self.xachse)
        self.xachse.show()
        aligny.add(self.yachse)
        self.yachse.show()
        alignz.add(self.zachse)
        self.zachse.show()





        # Add a timer callback to update the value of the progress bar
        self.timer = gobject.timeout_add (100, progress_timeout, self)

        separator = gtk.HSeparator()
        vbox.pack_start(separator, False, False, 0)
        separator.show()

        # rows, columns, homogeneous
        table = gtk.Table(3, 3, False)
        vbox.pack_start(table, False, True, 0)
        table.show()

        # Add a check button to select displaying of the trough text
        check = gtk.CheckButton("Show text")
        table.attach(check, 0, 1, 0, 1,
                     gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
                     5, 5)
        check.connect("clicked", self.toggle_show_text)
        check.show()

        # Add a check button to toggle activity mode
        self.activity_check = check = gtk.CheckButton("Activity mode")
        table.attach(check, 0, 1, 1, 2,
                     gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
                     5, 5)
        check.connect("clicked", self.toggle_activity_mode)
        check.show()



####################BUTTONS##################

	#Discover
	button1 = gtk.Button("search")
	button1.connect("clicked", self.destroy_progress)
        vbox.pack_start(button1, False, False, 0)

	#Establish
	button2 = gtk.Button("establish")
	button2.connect("clicked", self.destroy_progress)
        vbox.pack_start(button2, False, False, 0)
	
	#Terminate
	button3 = gtk.Button("terminate")
	button3.connect("clicked", self.destroy_progress)
        vbox.pack_start(button3, False, False, 0)
	
	#EXIT button
        button = gtk.Button("close")
        button.connect("clicked", self.destroy_progress)
        vbox.pack_start(button, False, False, 0)

        # This makes it so the button is the default.
        button.set_flags(gtk.CAN_DEFAULT)
        # This grabs this button to be the default button. Simply hitting
        # the "Enter" key will cause this button to activate.
        button.grab_default ()
        button.show() 

	button1.show()

        button2.show() 

	button3.show()

        self.window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    Fenster()
    main()


