import fileinput
import MySQLdb as mdb
import re
import subprocess as sub
import threading
import os

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
                print(line),

        except mdb.Error, e:
            # Do some exception handling concerning the database.
            conn.rollback()
            print "Error %d: %s" % (e.args[0],e.args[1])
        finally:
            if con:
                con.close()

class cmdListner(threading.Thread):
    """Listens for and issues commands to Minecraft server."""
    def run(self):
        print "Started cmdListner thread. (ID: %s)" % self.getName()
        # Path to pipe.
        self.pipePath = '/var/www/piper'
        # Attempt to remove pipe first, since  trying to create an already 
        # existing pipe will result in an error.
        try:
            os.unlink(self.pipePath)
        except:
            pass
        # Create pipe.
        os.mkfifo(self.pipePath)
        # Make pipe writeable.
        os.chmod(self.pipePath, 0666)
        # Open pipe for reading.
        pipe = open(self.pipePath,'r')
        while True:
            data = pipe.readline()
            if data != '':
                # If a command has been issued, send it to server.
                msm = sub.Popen(['msm', 'hallian', 'cmd', data],
                                shell = False, stdout = sub.PIPE)

if __name__ == "__main__":
    # Setup workers.
    db = dbWorker()
    msm = cmdListner()
    # Start workers.
    db.start()
    msm.start()
