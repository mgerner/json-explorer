#!/usr/bin/env python

import sys
import json

import main_app
import receive_data_app

def _load_file(fn):
    with open(fn) as f:
        return json.loads(f.read())

if __name__ == '__main__':
    if len(sys.argv) > 1:
        data = _load_file(sys.argv[1])
        main_app.MainApp(data).run()

    else:
        receive_data_app.ReceiveDataApp().mainloop()