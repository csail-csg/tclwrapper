import subprocess
import random
import time
import string
import os
import sys
import warnings
import fcntl
from tclwrapper.tclutil import tclstring_to_list

class TCLWrapperException(Exception):
    """Base class for TCLWrapper exceptions."""
    pass

class TCLWrapperError(TCLWrapperException):
    """tcl command failed."""
    def __init__(self, command, error_message, stderr = ''):
        self.command = command
        self.error_message = error_message.strip()
        self.stderr = stderr
        super().__init__(self.__str__())
    def __str__(self):
        msg = 'TCLWrapperError raised while executing the command "%s"\n error_message: "%s"' % (self.command, self.error_message)
        if self.stderr:
            msg += '\n stderr: %s' % (self.stderr)
        return msg

class TCLWrapperInstanceError(TCLWrapperException):
    """tcl process is in an unexpected state."""
    pass

class TCLWrapper:
    """Python interface for executing tcl commands in a specified tcl-based tool.

    You can use this class in two ways:

    1) Create an instance of TCLWrapper and strart the desired tcl background
    process by calling the start method. When you are done executing tcl code,
    stop the tcl background process by calling the stop method.

    Example:
    >> btcl = TCLWrapper('bluetcl')
    >> btcl.start()
    >> btcl.eval('Bluetcl::bpackage load mypackagename')
    >> btcl.stop()

    2) Use with notation to create a TCLWrapper instance. This will start the
    tcl background process automatically and stop it when the with block is
    exited.

    Example:
    >> with TCLWrapper('bluetcl') as btcl:
    >>     btcl.eval('Bluetcl::bpackage load mypackagename')
    """

    reserved_variable_name = 'reservedtcloutputvar'

    def __init__(self, tcl_exe = 'tclsh', *tcl_exe_args):
        """Creates a TCLWrapper for the specified tcl executable."""
        self._process = None
        self.last_stderr = None
        self.tcl_exe = tcl_exe
        self.tcl_exe_args = tcl_exe_args

    def start(self):
        """Start the tcl background process."""
        if self._process:
            raise TCLWrapperInstanceError('tcl instance already running.')
        self._process = subprocess.Popen(
            [self.tcl_exe] + list(self.tcl_exe_args),
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)
        # set stdout and stderr nonblocking to avoid possible deadlock
        def set_as_nonblocking(fd):
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            flags = flags | os.O_NONBLOCK
            fcntl.fcntl(fd, fcntl.F_SETFL, flags)
        set_as_nonblocking(self._process.stdout)
        set_as_nonblocking(self._process.stderr)

    def stop(self):
        """Stop the tcl background process."""
        if not self._process:
            raise ('no tcl instance running.')
        try:
            # calling exit from eval would cause an exception,
            # so just write it to stdin directly
            self._process.stdin.write(b'exit\n')
            self._process.communicate(timeout = 1)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.communicate()
        del self._process
        self._process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def eval(self, command, to_list = False):
        """Execute a single command in tcl and return the output string.
        
        If a script containing multiple commands is passed in, the output
        string from the last command is returned.

        This method requires start to be called before it is called.

        If the to_list argument is set to true, eval parses tcl lists and
        returns them as python lists of strings instead of a single string.
        For more complex output parsing, see the functions defined in tclutil.
        """

        if not self._process:
            raise TCLWrapperInstanceError('no tcl instance running.')

        # unique strings for identifying where output from commands start and finish
        key_string_length = 16
        def gen_unique_string(length = key_string_length):
            return ''.join([ random.choice(string.ascii_letters + string.digits) for x in range(length) ]).encode('ascii')
        stdout_start_key = gen_unique_string()
        stdout_done_key = gen_unique_string()
        stderr_start_key = gen_unique_string()
        stderr_delimiter_key = gen_unique_string()
        stderr_done_key = gen_unique_string()

        main_tcl_code = '\n'.join(['if { [ catch {',
                command,
                '} %s ] } {' % TCLWrapper.reserved_variable_name,
                '    puts -nonewline stderr ' + stderr_delimiter_key.decode('ascii'),
                '    puts -nonewline stderr $' + TCLWrapper.reserved_variable_name,
                '    puts -nonewline stderr ' + stderr_delimiter_key.decode('ascii'),
                '} else {',
                '    puts -nonewline stdout $' + TCLWrapper.reserved_variable_name,
                '}\n'])

        self._process.stdin.write(b'puts -nonewline stdout "' + stdout_start_key + b'"\n')
        self._process.stdin.write(b'puts -nonewline stderr "' + stderr_start_key + b'"\n')
        self._process.stdin.write(bytearray(main_tcl_code, 'utf-8'))
        self._process.stdin.write(b'puts -nonewline stdout "' + stdout_done_key + b'"\n')
        self._process.stdin.write(b'puts -nonewline stderr "' + stderr_done_key + b'"\n')
        self._process.stdin.write(b'flush stdout\nflush stderr\n')
        self._process.stdin.flush()

        stdout = b''
        stderr = b''

        fetching_stdout = True
        fetching_stderr = True
        try:
            while fetching_stdout or fetching_stderr:
                return_code = self._process.poll()
                if return_code is not None:
                    raise TCLWrapperInstanceError('tcl process finished unexpectedly with return code %d' % return_code)
                if fetching_stdout:
                    try:
                        # nonblocking reads raise an IOError if there is nothing to read
                        stdout += self._process.stdout.read1(1)
                    except IOError:
                        pass
                if fetching_stderr:
                    try:
                        # nonblocking reads raise an IOError if there is nothing to read
                        stderr += self._process.stderr.read1(1)
                    except IOError:
                        pass
                if stdout.endswith(stdout_done_key):
                    fetching_stdout = False
                if stderr.endswith(stderr_done_key):
                    fetching_stderr = False
        except KeyboardInterrupt as e:
            print("KeyboardInterrupt raised while trying to read from stdout and stderr in TCLWrapper('%s')" % self.tcl_exe)
            print('command = ' + repr(command))
            print('stdout = ' + repr(stdout.decode('utf-8')))
            print('stderr = ' + repr(stderr.decode('utf-8')))
            raise e

        # remove start keys and done keys
        stdout_start_key_loc = stdout.find(stdout_start_key)
        stderr_start_key_loc = stderr.find(stderr_start_key)
        stdout = stdout[stdout_start_key_loc + len(stdout_start_key):-len(stdout_done_key)].decode('utf-8')
        stderr = stderr[stderr_start_key_loc + len(stderr_start_key):-len(stderr_done_key)].decode('utf-8')
        stderr_split = stderr.split(stderr_delimiter_key.decode('utf-8'))
        if len(stderr_split) == 3:
            # The tcl command returned a non-zero exit code
            cmd_stderr = stderr_split[0]
            error_message = stderr_split[1]
            unexpected_stderr = stderr_split[2]
            if cmd_stderr:
                warnings.warn('tcl command "%s" generated stderr message %s' % (command, repr(cmd_stderr)), stacklevel = 2)
            if unexpected_stderr:
                # This shouldn't happen
                raise RuntimeError('tcl command "%s" produced unexpected stderr message %s' % (command, repr(unexpected_stderr)))
            raise TCLWrapperError(command, error_message, cmd_stderr)
        elif len(stderr_split) != 1:
            # This also shouldn't happen
            raise RuntimeError('tcl command "%s" produced stderr with an unexpected number of stderr delimiter keys. Full stderr message: %s' % (command, repr(stderr)))
        else:
            if stderr:
                warnings.warn('tcl command "%s" generated stderr message %s' % (command, repr(stderr)), stacklevel = 2)
        self.last_stderr = stderr
        if to_list:
            stdout = tclstring_to_list(stdout)
        return stdout 
