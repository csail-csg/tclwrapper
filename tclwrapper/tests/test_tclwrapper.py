import unittest
import shutil

from tclwrapper import tclwrapper

class TestTCLWrapper(unittest.TestCase):

    def test_tclwrapper_hello_world(self):
        tcl = tclwrapper.TCLWrapper()
        tcl.start()
        ret = tcl.eval('puts "Hello, World!"')
        self.assertEqual(ret, "Hello, World!\n")
        tcl.stop()

    def test_tclwrapper_hello_world_with(self):
        with tclwrapper.TCLWrapper() as tcl:
            ret = tcl.eval('puts "Hello, World!"')
            self.assertEqual(ret, "Hello, World!\n")

    def test_tclwrapper_vars(self):
        tcl = tclwrapper.TCLWrapper()
        tcl.start()

        x_tclstring = tcl.eval('set x 3')
        self.assertEqual(int(x_tclstring), 3)

        y_tclstring = tcl.eval('set y 7')
        self.assertEqual(int(y_tclstring), 7)

        expr_tclstring = tcl.eval('expr $x + $y')
        self.assertEqual(int(expr_tclstring), 10)

        z_tclstring = tcl.eval('set z [expr $x + $y]')
        self.assertEqual(int(z_tclstring), 10)

        s_tclstring = tcl.eval('set s "$x + $y = $z"')
        self.assertEqual(s_tclstring, '3 + 7 = 10')

        tcl.stop()

    def test_tclwrapper_block(self):
        tcl = tclwrapper.TCLWrapper()
        tcl.start()
        ret = tcl.eval('''
            set primes {2 3 5 7 11 13}
            set sum 0
            foreach prime $primes {
                set sum [ expr $sum + $prime ]
            }
            puts $sum''')
        self.assertEqual(int(ret), 41)
        tcl.stop()

    @unittest.skipIf(shutil.which('wish') is None, "test requires wish to be in the path")
    def test_tclwrapper_wish(self):
        # this test just makes sure that tclwrapper can work with a program
        # other than tclsh

        with tclwrapper.TCLWrapper() as tcl:
            try:
                # this won't work since tclsh doesn't support wm commands
                tcl.eval('wm withdraw .')
            except tclwrapper.TCLWrapperError as e:
                # this is expected
                pass
            else:
                self.fail('"wm withdraw ." should fail with a TCLWrapperError in normal tclsh')

        with tclwrapper.TCLWrapper('wish') as wish:
            try:
                wish.eval('wm withdraw .')
            except:
                self.fail('"wm withdraw ." should not raise an exception in wish')

    @unittest.skipIf(shutil.which('gtkwave') is None, "test requires gtkwave to be in the path")
    def test_tclwrapper_gtkwave(self):
        # gtkwave requires the -W flag to get tcl commands from stdin
        with tclwrapper.TCLWrapper('gtkwave', '-W') as tcl:
            font_height = int(tcl.eval('gtkwave::getFontHeight'))
            self.assertGreater(font_height, 0)

