from Tkinter import Tk, Label, Button, Entry, IntVar, END, W, E
from collections import namedtuple
import threading

ThermostatGuiMessage = namedtuple('ThermostatGuiMessage', 'temp humidity thermostat')

class ThermostatGui:

    def __init__(self, gui_message):
        self.master = Tk()
        self.master.title("Thermostat Control Panel")

        self.temp = gui_message.temp
        self.humidity = gui_message.humidity
        self.thermostat = gui_message.thermostat

        self.entered_value = 0

        self.temp_label_text = IntVar()
        self.temp_label_text.set(self.temp)
        self.temp_label = Label(self.master, textvariable=self.temp_label_text)
        self.humidity_label_text = IntVar()
        self.humidity_label_text.set(self.humidity)
        self.humidity_label = Label(self.master, textvariable=self.humidity_label_text)
        self.thermostat_label_text = IntVar()
        self.thermostat_label_text.set(self.thermostat)
        self.thermostat_label = Label(self.master, textvariable=self.thermostat_label_text)

        self.temp_label_static = Label(self.master, text="Temperature:")
        self.humidity_label_static = Label(self.master, text="Humidity:")
        self.thermostat_label_static = Label(self.master, text="Thermostat:")

        # LAYOUT

        self.temp_label_static.grid(row=0, column=0, sticky=W)
        self.temp_label.grid(row=0, column=1, columnspan=2, sticky=E)
        self.humidity_label_static.grid(row=1, column=0, sticky=W)
        self.humidity_label.grid(row=1, column=1, columnspan=2, sticky=E)
        self.thermostat_label_static.grid(row=2, column=0, sticky=W)
        self.thermostat_label.grid(row=2, column=1,  columnspan=2, sticky=E)

    def start(self):
        self.gui_thread = threading.Thread(target=self.master.mainloop())
        self.gui_thread.start()

    def validate(self, new_text):
        if not new_text: # the field is being cleared
            self.entered_value = self.entered_value
            return True
        try:
            self.entered_value = int(new_text)
            return True
        except ValueError:
            return False

    def update(self, gui_message):
        self.temp = gui_message.temp
        self.humidity = gui_message.humidity
        self.thermostat = gui_message.thermostat

        self.temp_label_text.set(self.temp)
        self.humidity_label_text.set(self.humidity)
        self.thermostat_label_text.set(self.thermostat)