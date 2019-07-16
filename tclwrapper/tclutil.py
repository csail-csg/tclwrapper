import tkinter as tk

# use tkinter because it already has some functions to parse tcl output
_tcl = tk.Tk(useTk = 0)

tclstring_to_list = _tcl.tk.splitlist
tclstring_to_nested_list = _tcl.tk.split
def tclstring_to_flat_list(tclstring):
    return tclstring.replace('{', ' ').replace('}', ' ').split()
def list_to_tclstring(in_list):
    cleaned_up_list = []
    for entry in in_list:
        if ' ' in entry:
            cleaned_up_list.append('{' + entry + '}')
        else:
            cleaned_up_list.append(entry)
    return ' '.join(cleaned_up_list)
def nested_list_to_tclstring(nested_list):
    items = []
    for item in nested_list:
        if isinstance(item, str):
            if ' ' in item:
                items.append('{' + item + '}')
            else:
                items.append(item)
        else:
            items.append('{' + nested_list_to_tclstring(item) + '}')
    return ' '.join(items)
