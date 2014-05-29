import os
import threading
import pyinotify
import socket
from collections import deque

notification_queue = deque()

from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent


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
		HOST =  ''   # The remote host
		PORT = 12346# The same port as used by the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((HOST, PORT))
		sock.send(code)
		sock.close()

		HOST =  ''   # The remote host
		PORT = 12346# The same port as used by the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((HOST, PORT))
		
		if code=="CREATE" :
			sock.send(fname)
			sock.close()

			HOST =  ''   # The remote host
			PORT = 12346# The same port as used by the server
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
		elif code=="DELETE" :
			sock.send(fname)
			sock.close()
		elif code=="MOVED FROM" :
			sock.send(fname)
			sock.close()
		elif code=="MOVED TO" :
			sock.send(fname)
			sock.close()
		
class MyProcessing(ProcessEvent):
	def __init__(self):
		pass

	def process_IN_CLOSE_WRITE(self, event):
		print "in close write ",event.pathname
		fname=event.name.replace(' ','\ ')
		notification_queue.append((fname, event.pathname, "CREATE"))
		
	def process_IN_DELETE(self, event):
		print "in delete ",event.pathname
		fname=event.name.replace(' ','\ ')
		notification_queue.append((fname, event.pathname, "DELETE"))

	def process_IN_CREATE(self, event):
		print "in create ",event.pathname
		fname=event.name.replace(' ','\ ')		
		'''sock_send(fname, event.pathname, "ISDIR")'''

	def process_IN_MOVED_FROM(self, event):
		print "in moved from of file ",event.pathname
		fname=event.name.replace(' ','\ ')		
		notification_queue.append((fname, event.pathname, "MOVED FROM"))

	def process_IN_MOVED_TO(self, event):
		print "in moved from of file ",event.pathname
		fname=event.name.replace(' ','\ ')		
		notification_queue.append((fname, event.pathname, "MOVED TO"))

	def process_default(self, event):
		print "in default ",event.pathname





wm = WatchManager()			#somethng which creates a manager like thing to look wat all folders are to take care of
mask = pyinotify.ALL_EVENTS	#wat all events r to be notified
wm.add_watch('/home/madhu/trials/cutie-pie', mask, rec=True,auto_add=True)
notifier = Notifier(wm, MyProcessing())	# connecting d manager and methods to call
thread1=myThread(1,"cutie-pie-thread")
thread1.start()
notifier.loop()	# start
print "thread started"
