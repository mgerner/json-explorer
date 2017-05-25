import json
from Tkinter import *
import ttk

import conf

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

        self.title(conf.TITLE)

        # create first layout level (a frame and a text element)
        self.grid()

        f = Frame(self)
        f.grid(row=0, column=0, sticky=NSEW)

        self.text = Text(self)
        if not conf.EDITOR_ENABLED:
            self.text.config(state=DISABLED)

        self.text.grid(row=0, column=1, sticky=NSEW)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create the layout of the frame
        self.tree = ttk.Treeview(f)
        self.tree.grid(row=1, column=0, sticky=NSEW)
        self.tree.bind('<<TreeviewSelect>>', self.selected)
        self.tree.bind('<Control-Key-c>', self.copy_node)
        self.tree.bind('<Command-Key-c>', self.copy_node)

        self.filter_box = Entry(f)
        self.filter_box.pack()
        self.filter_box.grid(row=0, column=0, sticky=NSEW)
        self.filter_box.bind('<Return>', self.filter)

        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(0, weight=0)
        f.grid_rowconfigure(1, weight=1)

        # set the data that should be used, and trigger the population of the controls
        self.original_data = data
        self.filter(None)

        # set global keyboard shortcuts
        self.bind_all('<Control-Key-n>', self.new_window)
        self.bind_all('<Command-Key-n>', self.new_window)
        self.bind_all('<Control-Key-f>', self.set_filter_focus)
        self.bind_all('<Command-Key-f>', self.set_filter_focus)

    def new_window(self, _event):
        import receive_data_app
        receive_data_app.ReceiveDataApp().run()
    
    def copy_node(self, _event):
        self.clipboard_clear()
        self.clipboard_append(self.text.get("1.0", END))

    def set_filter_focus(self, _event):
        self.filter_box.focus()
        self.filter_box.select_range(0, END)
        self.filter_box.icursor(END)

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

        if not conf.EDITOR_ENABLED:
            self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.insert(END, self.cache[selected])
        if not conf.EDITOR_ENABLED:
            self.text.config(state=DISABLED)

    def run(self):
        self.focus_force()
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        self.mainloop()
