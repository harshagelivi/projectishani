import os
import pyinotify
import socket


from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
def sock_send(fname, floc, code):
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
		
		if code=="CREATE" :
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
		elif code=="DELETE" :
			sock.send(fname)
			sock.close()
		elif code=="CUT" :
			sock.send(fname)
			sock.close()
		elif code=="PASTE" :
			sock.send(fname)
			sock.close()
		
class MyProcessing(ProcessEvent):
	def __init__(self):
		pass

	def process_IN_CLOSE_WRITE(self, event):
		print "in close write ",event.pathname
		sock_send(event.name, event.pathname, "CREATE")
		
	def process_IN_DELETE(self, event):
		print "in delete ",event.pathname
		sock_send(event.name, event.pathname, "DELETE")

	def process_IN_MOVED_FROM(self, event):
		print "in moved from of file ",event.pathname
		sock_send(event.name, event.pathname, "CUT")

	def process_IN_MOVED_TO(self, event):
		print "in moved from of file ",event.pathname
		sock_send(event.name, event.pathname, "PASTE")

	def process_default(self, event):
		print "in default ",event.pathname





wm = WatchManager()			#somethng which creates a manager like thing to look wat all folders are to take care of
mask = pyinotify.ALL_EVENTS	#wat all events r to be notified
wm.add_watch('/home/madhu/ishani', mask, rec=True)

notifier = Notifier(wm, MyProcessing())	# connecting d manager and methods to call
notifier.loop()	# start
