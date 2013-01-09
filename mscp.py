import fileinput
import MySQLdb as mdb
import re
import subprocess as sub
import threading
import os

con = None

# The following pattern will match the different parts of the log strings.
logPattern = re.compile("^(?P<date>\d{4}-\d{2}-\d{2})\s(?P<time>\d\d:\d\d:\d\d)\s\[(?P<level>.+?)\]\s(?P<message>.*)$", re.M)

class dbWorker(threading.Thread):
	def run(self):
		print "Started dbWorker thread. (ID: %s)" % self.getName()
		try:
		        con = mdb.connect('localhost', 'mmc', 'mmc', 'mmc')
		        cursor = con.cursor()
		        print "Connected to db..."
		        p = sub.Popen('tail -fn50 /opt/msm/servers/hallian/server.log', shell = True, stdout = sub.PIPE)
		        for line in iter(p.stdout.readline, ''):
		                r = logPattern.match(line)
		                if r:
		                        if re.match('INFO|WARNING|SEVERE', r.group('level')):
		                                level = r.group('level')
		                        else:
		                                level = 'UNKNOWN'
		                        cursor.execute("INSERT INTO log(date,time,level,message) VALUES (%s, %s, %s, %s)",(r.group('date'), r.group('time'), level, r.group('message')))
		                        con.commit()
		                print(line),
			
		except mdb.Error, e:
			conn.rollback()
			print "Error %d: %s" % (e.args[0],e.args[1])
		finally:
			if con:
				con.close()

class cmdListner(threading.Thread):
	def run(self):
		self.pipePath = '/var/www/piper'
		try:
			os.unlink(self.pipePath)
		except:
			pass
		os.mkfifo(self.pipePath)
		pipe = open(self.pipePath,'rw')
		while True:
			data = pipe.readline()
			if data != '':
		        	msm = sub.Popen(['msm', 'hallian', 'cmd', data], shell = False, stdout = sub.PIPE)
				
			
				
				
db = dbWorker()
msm = cmdListner()
db.start()
msm.start()



"""try:
	con = mdb.connect('localhost', 'mmc', 'mmc', 'mmc')
	cursor = con.cursor()
	print "Connected to db..."
	p = sub.Popen('tail -fn50 /opt/msm/servers/hallian/server.log', shell = True, stdout = sub.PIPE)
	for line in iter(p.stdout.readline, ''):
		r = logPattern.match(line)
		if r:
			if re.match('INFO|WARNING|SEVERE', r.group('level')):
				level = r.group('level')
			else:
				level = 'UNKNOWN'
			cursor.execute("INSERT INTO log(date,time,level,message) VALUES (%s, %s, %s, %s)",(r.group('date'), r.group('time'), level, r.group('message')))
			con.commit()
		print(line),
except mdb.Error, e:
	conn.rollback()
	print "Error %d: %s" % (e.args[0],e.args[1])
	sys.exit(1)

finally:
	if con:
		con.close()
"""
