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

def _filter(data, keys):
    if isinstance(data, list):
        res = [_filter(obj, keys) for obj in data]
        res = [obj for obj in res if obj]

        return res

    elif isinstance(data, dict):
        res = {}

        for k, v in data.iteritems():
            if k in keys:
                res[k] = v
            else:
                v = _filter(v, keys)
                if v:
                    res[k] = v

        return res

class MainApp(Tk):
    mappings = None
    cache = None
    filtered_data = None

    def __init__(self, data):
        Tk.__init__(self, None)

        # create first layout level (a frame and a text element)
        self.grid()

        f = Frame(self)

        self.text = Text(self)
        self.text.config(state=DISABLED)

        f.grid(row=0, column=0, sticky=NSEW)
        self.text.grid(row=0, column=1, sticky=NSEW)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create the layout of the frame
        self.tree = ttk.Treeview(f)
        self.tree.bind('<<TreeviewSelect>>', self.selected)

        self.filter_box = Entry(f)
        self.filter_box.bind('<Return>', self.filter)
        self.filter_box.pack()

        self.filter_box.grid(row=0, column=0, sticky=NSEW)
        self.tree.grid(row=1, column=0, sticky=NSEW)
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(0, weight=0)
        f.grid_rowconfigure(1, weight=1)

        # set the data that should be used, and trigger the population of the controls
        self.original_data = data
        self.filter(None)


    def filter(self, _event):
        if not self.filter_box.get().strip():
            self.filtered_data = self.original_data
            self.populate_views()
            return

        keys = self.filter_box.get().split(',')
        keys = [k.strip() for k in keys if k.strip()]

        self.filtered_data = _filter(self.original_data, keys)
        self.populate_views()

    def populate_views(self):
        if self.tree.exists('root'):
            self.tree.delete('root')

        self.tree.insert('', 'end', 'root', text='root', open=True)

        self.mappings = _add_items(self.tree, self.filtered_data, 'root')
        self.cache = {}

        self.tree.selection_set('root')

    def selected(self, _event):
        selected = self.tree.selection()[0]
        if selected not in self.cache:         
            self.cache[selected] = json.dumps(self.mappings[selected], indent=2)

        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.insert(END, self.cache[selected])
        self.text.config(state=DISABLED)

    def run(self):
        self.focus_force()
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        self.mainloop()

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

        if len(sys.argv) > 2:
            data = _filter(data, sys.argv[2].split(','))

        MainApp(data).run()

    else:
        ReceiveDataApp().mainloop()