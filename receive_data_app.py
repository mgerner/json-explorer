import json
from Tkinter import *
import ttk

import main_app
import conf

class ReceiveDataApp(Tk):
    def __init__(self):
        Tk.__init__(self, None)

        self.title(conf.TITLE)

        self.grid()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        button = Button(self, text='OK', command=self.parse)
        button.grid(row=1, column=0, sticky=NSEW)
        
        self.text = Text(self)
        self.text.grid(row=0, column=0, sticky=NSEW)

        self.bind_all('<Control-Key-Return>', self.parse)
        self.bind_all('<Command-Key-Return>', self.parse)

    def parse(self, _event=None):
        data = json.loads(self.text.get(1.0, END))
        main_app.MainApp(data).run()
        self.destroy()

    def run(self):
        self.focus_force()
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        self.mainloop()
