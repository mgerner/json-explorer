import sys
import json
from Tkinter import *
import ttk

def load_file(fn):
    with open(fn) as f:
        return json.loads(f.read())

def _add_items(w, data, parent=''):
    res = {}

    if parent:
        res[parent] = data

    if isinstance(data, list):
        for i, obj in enumerate(data):
            cid = w.insert(parent, 'end', text='[%i]' % i)
            res.update(_add_items(w, obj, cid))
    elif isinstance(data, dict):
        for k, v in data.iteritems():
            cid = w.insert(parent, 'end', text=k)
            res.update(_add_items(w, v, cid))
    
    return res

class MainApp(Tk):
    def __init__(self, data):
        Tk.__init__(self, None)

        self.grid()

        self.tree = ttk.Treeview(self)
        self.tree.bind('<<TreeviewSelect>>', self.selected)
        self.mappings = _add_items(self.tree, data)
        self.cache = {}

        self.text = Text(self)
        self.text.config(state=DISABLED)

        self.tree.grid(row=0, column=0, sticky=NSEW)
        self.text.grid(row=0, column=1, sticky=NSEW)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def selected(self, _event):
        selected = self.tree.selection()[0]
        if selected not in self.cache:         
            self.cache[selected] = json.dumps(self.mappings[selected], indent=2)

        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.insert(END, self.cache[selected])
        self.text.config(state=DISABLED)

class ReceiveDataApp(Tk):
    def __init__(self):
        Tk.__init__(self, None)

        self.grid()
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        button = Button(self, text='OK', command=self.clicked)
        button.grid(row=1, column=0, sticky=NSEW)
        
        self.text = Text(self)
        self.text.grid(row=0, column=0, sticky=NSEW)

    def clicked(self):
        data = json.loads(self.text.get(1.0, END))
        MainApp(data).mainloop()
        self.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        data = load_file(sys.argv[1])
        MainApp(data).mainloop()

    else:
        ReceiveDataApp().mainloop()