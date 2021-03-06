from __future__ import print_function
import sys, os, time, atexit
from signal import SIGTERM
from portela.shared import Color as c

class Daemon:
    '''
    A generic daemon class.
    
    Usage: subclass the Daemon class and override the run() method
    '''
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def get_PID(self):
        ''' reads process ID from PID file '''

        try:
            with open(self.pidfile) as file:
                pid = file.read()  
            return int(pid)

        except IOError:
            return None
    
    def daemonize(self):
        '''
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        '''
        try:
            pid = os.fork()
        
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
    
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'w+')
        se = open(self.stderr, 'w+')
        
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        pid_file = open(self.pidfile, 'w+')
        pid_file.write(pid)
        pid_file.close()
        

    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        ''' Start the daemon '''
       
        pid = self.get_PID()

        if pid:
            message = c.GREEN + "Portela is already running. Pidfile: %s\n" + c.END
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
               
        # Start the daemon
        sys.stderr.write(c.TEAL + "starting Portela as daemon.\n" + c.END)
        self.daemonize()
        self.run()

 
    def stop(self):
        ''' Stop the daemon '''
        
        pid = self.get_PID()
        
        if not pid:
            message = c.YELLOW + "Portela is stopped.\n" + c.END
            sys.stderr.write(message)
            return # not an error in a restart
 
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)
        
        message = c.YELLOW + "Portela is stopped.\n" + c.END
        sys.stderr.write(message)
        return # not an error in a restart

    def restart(self):
        ''' Restart the daemon '''
        
        self.stop()
        self.start()

    def status(self):
        ''' get status of daemon '''
    
        pid = self.get_PID()

        if pid:
            message = c.GREEN + "Portela is running on PID: %s.\n" + c.END
            sys.stderr.write(message % pid)
            return
        else:
            message = c.GRAY + "Portela is not running.\n" + c.END
            sys.stderr.write(message)
            return

    def run(self):
        '''
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        '''