import tkinter

# use tkinter because it already has some functions to parse tcl output
_tcl = tkinter.Tk(useTk = 0)

def tclstring_to_list(tclstring):
    ret = _tcl.tk.splitlist(tclstring)
    # always return the result as a tuple
    if isinstance(ret, str):
        if ret == '':
            return ()
        else:
            return (ret,)
    else:
        return ret

def tclstring_to_nested_list(tclstring, levels = None):
    if levels is None:
        # use split from _tkinter
        ret = _tcl.tk.split(tclstring)
        # always return the result as a tuple
        if isinstance(ret, str):
            if ret == '':
                return ()
            else:
                return (ret,)
        else:
            return ret
    else:
        if levels == 0:
            return tclstring
        else:
            return tuple([tclstring_to_nested_list(x, levels-1) for x in tclstring_to_list(tclstring)])

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
