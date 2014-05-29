import os
import threading
import pyinotify
import socket
from collections import deque

notification_queue = deque()

from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
path="/home/madhu/trials/ishani/"
moved_from_flag	=	0
moved_from_name =	''
moved_from_loc	=	''


class myThread (threading.Thread):
    def __init__(self, threadID,name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
    	print "in thread"
	global notification_queue
	while  1:
		if notification_queue:
			print "hello"
			p=notification_queue.popleft()
			sock_send(p[0],p[1],p[2])
	

def sock_send(fname, floc, code):
	global moved_from_flag
	global moved_from_name
	global moved_from_loc

	if ((fname) and (fname[-1]!='~' and fname[0] !='.') ):
		
		if(code=="MOVED_TO" and moved_from_flag==1):
			code="RENAMEDIR"
		elif(moved_from_flag==1):
			moved_from_flag=0
			sock_send(moved_from_name, moved_from_loc,"RMDIR")

		HOST =  ''   # The remote host
		PORT = 12345# The same port as used by the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((HOST, PORT))
		sock.send(code)
		sock.close()

		HOST =  ''   # The remote host
		PORT = 12345# The same port as used by the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((HOST, PORT))
		fname=floc.replace(path, '')
		if(code=="RENAMEDIR"):
			sock.send(fname)
			sock.close()
			HOST =  ''   # The remote host
			PORT = 12345# The same port as used by the server
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.connect((HOST, PORT))
			prevfname=moved_from_loc.replace(path, '')
			sock.send(prevfname)
			sock.close()
			moved_from_flag=0
			moved_from_loc=''
			moved_from_name=''
		elif (code=="CREATE" or code=="MOVED_TO"):			
			sock.send(fname)
			sock.close()
			HOST =  ''   # The remote host
			PORT = 12345# The same port as used by the server
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.connect((HOST, PORT))
			fd = open(floc,'rb')
			dat = fd.read(1024)
			while dat:
				print "sending data"
				sock.send(dat)
				dat=fd.read(1024)
			sock.close()
			fd.close()
		elif code=="DELETE" or code=="MOVED_FROM" or code=="MKDIR" or code=="RMDIR":
			sock.send(fname)
			sock.close()
	
class MyProcessing(ProcessEvent):
	def __init__(self):
		pass
	def process_IN_CLOSE_WRITE(self, event):
		print "in close write ",event.pathname
		notification_queue.append((event.name, event.pathname, "CREATE"))
	def process_IN_DELETE(self, event):
		print "in delete ",event.pathname
		if(event.dir):
			notification_queue.append((event.name, event.pathname, "RMDIR"))
		else:
			notification_queue.append((event.name, event.pathname, "DELETE"))
	def process_IN_CREATE(self, event):
		print "in create ",event.pathname
		if(event.dir):
			notification_queue.append((event.name, event.pathname, "MKDIR"))
		else:
			notification_queue.append((event.name, event.pathname, "CREATE"))
	def process_IN_MOVED_FROM(self, event):
		print "in moved from of file ",event.pathname
		global moved_from_flag
		global moved_from_name
		global moved_from_loc
		if (event.dir):
			if(moved_from_flag==1):
				sock_send(moved_from_name, moved_from_loc, "RMDIR")
			moved_from_flag	=	1
			moved_from_name =	event.name
			moved_from_loc	=	event.pathname
		else:
			notification_queue.append((event.name, event.pathname, "MOVED_FROM"))
	def process_IN_MOVED_TO(self, event):
		print "in moved from of file ",event.pathname
		notification_queue.append((event.name, event.pathname, "MOVED_TO"))
	def process_default(self, event):
		print "in default ",event.pathname





wm = WatchManager()			#somethng which creates a manager like thing to look wat all folders are to take care of
mask = pyinotify.ALL_EVENTS	#wat all events r to be notified
wm.add_watch('/home/madhu/trials/ishani', mask, rec=True,auto_add=True)
notifier = Notifier(wm, MyProcessing())	# connecting d manager and methods to call
thread1=myThread(1,"ishani-thread")
thread1.start()
notifier.loop()	# start
print "thread started"
