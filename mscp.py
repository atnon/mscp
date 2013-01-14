import MySQLdb as mdb
import re
import subprocess as sub
import threading
import os
import signal
import sys
import socket
import select

threadExit = False

class dbWorker(threading.Thread):
    """Reads log and insert lines into database."""
    def run(self):
        print "Started dbWorker thread. (ID: %s)" % self.getName()
        # RegEx for breaking log strings into its components.
        logPattern = re.compile("^(?P<date>\d{4}-\d{2}-\d{2})\s" +
                                "(?P<time>\d\d:\d\d:\d\d)\s" +
                                "\[(?P<level>.+?)\]\s(?P<message>.*)$",
                                re.M)
        con = None
        try:
            # Connect to database
            con = mdb.connect('localhost', 'mmc', 'mmc', 'mmc')
            cursor = con.cursor()
            print "Connected to db."
            # Run subprocess reading log.
            p = sub.Popen(
                    'tail -fn50 /opt/msm/servers/hallian/server.log',
                    shell = True, stdout = sub.PIPE)
            for line in iter(p.stdout.readline, ''):
                # Break logline into parts.
                r = logPattern.match(line)
                # Handle loglevels.
                if r:
                    if re.match('INFO|WARNING|SEVERE', r.group('level')):
                        level = r.group('level')
                    else:
                        level = 'UNKNOWN'
                    # Prepare db insertion and commit.
                    cursor.execute(
                        ''.join(["INSERT INTO log(date,time,level,message)",
                        "VALUES (%s, %s, %s, %s)"]),(r.group('date'),
                        r.group('time'), level, r.group('message')))
                    con.commit()
                # Output line to stdout
                #print(line),
                if threadExit:
                    break

        except mdb.Error, e:
            # Do some exception handling concerning the database.
            conn.rollback()
            print "Error %d: %s" % (e.args[0],e.args[1])
        finally:
            if con:
                con.close()
        #
        print "%s: Exit" % self.getName()

class cmdListner(threading.Thread):
    """Listens for and issues commands to Minecraft server."""
    def __init__(self):
        # Path to pipe.
        self.socketPath = '/var/www/piper'
        threading.Thread.__init__(self)

    def run(self):
        print "Started cmdListner thread. (ID: %s)" % self.getName()
        # Open pipe for reading.
        with createSocket(self.socketPath) as sock:
            while not threadExit:
                data = pipe.readline()
                if data != '':
                    # If a command has been issued, send it to server.
                    msm = sub.Popen(['msm', 'hallian', 'cmd', data],
                                shell = False, stdout = sub.PIPE)

class createSocket:
    """ Initializes a unix socket, binds and starts listening.
    """
    def __init__(self, socketPath):
        self.socketPath = socketPath
        self.buffer = None

    def __enter__(self):
        # Setup socket handler.
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        # Attempt to remove socket first, since trying to create an already 
        # existing socket will result in an error.
        try:
            os.unlink(self.socketPath)
        except:
            pass

        # Bind to socket.
        self.sock.bind(self.socketPath)
        self.sock.listen(1)
        # Make pipe writeable.
        #os.chmod(self.pipePath, 0666)
        return self.sock
    
    def readline(self):
        
    
    def __exit__(self, type, value, traceback):
        # Close socket.
        self.sock.close()
        # Clean up the pipe we created.
        os.unlink(self.pipePath)

def main():
    # Setup workers.
    db = dbWorker()
    msm = cmdListner()
    # Start workers.
    db.start()
    msm.start()


if __name__ == "__main__":
    # Setup handler for KeyboardInterrupt (Ctrl+C)
    def keyInt(signal, frame):
        print 'Exiting...'
        treadExit = True
        sys.exit()
    signal.signal(signal.SIGINT, keyInt)

    #Execute main program
    main()
