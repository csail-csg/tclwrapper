TCLWrapper
==========

Python wrapper to interact with TCL command line interfaces. In most cases,
tkinter (with the send command) is enough but sometimes it is convenient to
interact directly with the tcl cli provided by applications.


Installing Non-Development Version
----------------------------------

If you want to just install the `tclwrapper` package, you should be able to using the following command:


    $ pip3 install tclwrapper


Usage
-----

As an example, here is some code that interfaces with GTKWave's TCL interface:

.. code:: python

    from tclwrapper import TCLWrapper
    with TCLWrapper('gtkwave', '-W') as tcl:
        tcl.eval('gtkwave::loadFile %s' % filename)
        tcl.eval('set num_facs [gtkwave::getNumFacs]')
        signals = tcl.eval('''
            set all_facs [list]
            for {set i 0} {$i < $num_facs} {incr i} {
                lappend all_facs [gtkwave::getFacName $i]
            }
            return $all_facs''', to_list = True)


Installing for Development
--------------------------

To install this package for development, you should use a virtual environment, and install the package in editable mode using pip.

To create a virtual environment for this project, run the command below.

    $ python3 -m venv path/to/new-venv-folder

To start using your new virtual environment, run the command below.
This needs to be run each time you open a new terminal.

    $ source path/to/new-venv-folder/bin/activate

At this point you are now using your new virtual environment.
Python packages you install in this environment will not be available outside your virtual environment.
If you want to stop using the virtual environment, just run `deactivate`.

To install the `tclwrapper` package in editable mode, inside the `tclwrapper` top git repository folder, run the command below.

    $ pip3 install -e .
