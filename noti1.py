import os
import threading
import pyinotify
import socket
import ast
from collections import deque
import time
from pyinotify import WatchManager, Notifier, ThreadedNotifier, EventsCodes, ProcessEvent
import shutil

moved_from_flag	=	0
moved_from_name =	''
moved_from_loc	=	''
notification_queue = deque()
send_queue={}
serverhost=''
serverport=0
myhost=''
myport=0
send_flag=1
flag=1
path=''


def check_moved_from():
	global moved_from_flag
	global moved_from_name
	global moved_from_loc
	if(moved_from_flag==1):
		notification_queue.append((moved_from_name, moved_from_loc,'',"RMDIR"))
	moved_from_flag	=	0
	moved_from_name =	''
	moved_from_loc	=	''


class myThread (threading.Thread):
    def __init__(self, threadID,name, folder_name, root_path,my_host, my_port, server_host, server_port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.folder_name=folder_name
        self.root_path=root_path
        self.myhost=my_host
        self.myport=my_port
        self.server_port=server_port
        self.server_host=server_host
        global myhost
        global myport
	global path
	global serverhost
	global serverport
        myhost=self.myhost
        myport=self.myport			#my_host and my_port are local
	serverport=self.server_port
	serverhost=self.server_host
	path=root_path+folder_name+'/'
    def run(self):
	global flag
	global send_flag
	global notification_queue
	global send_queue
	global path
    	if self.name[0:3]=="snd":
#	    	print "in sender thread"
		while  1:
			if notification_queue:
				p=notification_queue.popleft()
				if p[3]=="STOP":
					send_flag=0
				elif p[3]=="START":
					send_flag=1
				if send_flag==1 and p[3]!="START" and p[3]!="STOP" and p[0] and p[0][0]!='.' and p[0][-1]!='~':
					fname=p[1].replace(path,'')
					prevfname=p[2].replace(path,'')
					code=p[3]
					index=fname+'_'+prevfname+'_'+code
					print "to be sent---->"+index
					try:
						if send_queue[index]:
							send_queue[index]=send_queue[index]-1
						else:
							sock_send(p[0],p[1],p[2],p[3])
					except:
						sock_send(p[0],p[1],p[2],p[3])
					time.sleep(.005)
	elif self.name[0:3]=="rcv":
#	    	print "in receiver thread"
		HOST=self.myhost
		PORT=self.myport
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((HOST, PORT))
		sock.listen(80)
		folder=self.root_path+self.folder_name+"/"
		while True:
			conn, addr = sock.accept()
			literal=str(conn.recv(1024))
#			print literal

			conn.close()
			tup=ast.literal_eval(literal)
			code=tup[0]
			fname=tup[1]
			prevfname=tup[2]
			myhost=tup[3]
			myport=int(tup[4])
			notification_queue.append(("STOP", "STOP", '', "STOP"))
			flag=0
			index=fname+'_'+prevfname+'_'+code
			print "recieved---->"+index
			if self.myport!=myport or self.myhost!=myhost:
				if (code == "CREATE" or code=="MOVED_TO"):
					floc=folder+fname
					fd = open(floc, 'wb')
					conn, addr = sock.accept()
					if conn:
						dat = conn.recv(1024)
						if dat:
							while dat:
								fd.write(dat)
								dat=conn.recv(1024)
							fd.close()		
					try:
						send_queue[index]=send_queue[index]+1
					except:
						send_queue[index]=1
				elif (code == "DELETE" or code=="MOVED_FROM"):
#					print fname
					floc=folder+fname
					try:
						os.remove(floc)
						try:
							send_queue[index]=send_queue[index]+1
						except:
							send_queue[index]=1
					except:
						pass
				elif (code=="MKDIR"):
#					print fname
					try:
						os.mkdir(os.path.join(folder,fname))
						try:
							send_queue[index]=send_queue[index]+1
						except:
							send_queue[index]=1
					except:
						pass
				elif (code=="RMDIR"):
#					print "rmdir ----"+os.path.join(folder,fname)
					try:
						shutil.rmtree(os.path.join(folder,fname))
						try:
							send_queue[index]=send_queue[index]+1
						except:
							send_queue[index]=1
					except:
#						print "in exception"
						pass
				elif (code=="RENAMEDIR"):
#					print "fname  : "+fname			
#					print "prevfname  : "+prevfname
#					print "---"+ os.path.join(folder, prevfname)+"---"+os.path.join(folder, fname)
					try:
						os.rename(os.path.join(folder, prevfname), os.path.join(folder, fname))
						try:
							send_queue[index]=send_queue[index]+1
						except:
							send_queue[index]=1
					except:
						pass
#				print "closed the connection"
			notification_queue.append(("START", "START", '', "START"))
			flag=1
		sock.close()
#		print "closed the socket"


def sock_send(fname, floc, floc1, code):
	global myhost
	global myport
	global serverhost
	global serverport
	if ((fname)):
		global moved_from_flag
		global moved_from_name
		global moved_from_loc
		HOST =  serverhost	# The remote host
		PORT =  serverport		# The same port as used by the server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			sock.connect((HOST, PORT))
			fname=floc.replace(path, '')
			prevfname=''
			if(code=="RENAMEDIR"):
				prevfname=floc1.replace(path, '')
				literal= '[' +'"'+code+'"'+ ','  +'"'+fname+'"'+ ',' +'"'+prevfname+'"'+ ',' + '"' + myhost + '"' +','+ '"'+str(myport)+'"' +']'
				sock.send(literal)
				sock.close()
				moved_from_flag=0
				moved_from_loc=''
				moved_from_name=''
			elif (code=="CREATE" or code=="MOVED_TO"):			
				literal= '[' +'"'+code+'"'+ ','  +'"'+fname+'"'+ ',' +'"'+prevfname+'"'+ ',' + '"' + myhost + '"' +','+ '"'+str(myport)+'"' +']'
				sock.send(literal)
				sock.close()
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				sock.connect((HOST, PORT))
				try:
					fd = open(floc,'rb')
					dat = fd.read(1024)
					while dat:
		#				print "sending data"
						sock.send(dat)
						dat=fd.read(1024)
					fd.close()
				except:
					pass
				sock.close()
			elif code=="DELETE" or code=="MOVED_FROM" or code=="MKDIR" or code=="RMDIR":
				literal= '[' +'"'+code+'"'+ ','  +'"'+fname+'"'+ ',' +'"'+prevfname+'"'+ ',' + '"' + myhost + '"' +','+ '"'+str(myport)+'"' +']'
				sock.send(literal)
				sock.close()
		except:
			pass
class MyProcessing(ProcessEvent):
	def __init__(self):
		pass
	def process_IN_CLOSE_WRITE(self, event):
#		print "in close write ",event.pathname
		global flag
		if flag:
			check_moved_from()
			notification_queue.append((event.name, event.pathname, '',"CREATE"))
	def process_IN_DELETE(self, event):
#		print "in delete ",event.pathname
		global flag
		if flag:
			check_moved_from()
			if(event.dir):
				notification_queue.append((event.name, event.pathname, '',"RMDIR"))
			else:
				notification_queue.append((event.name, event.pathname,'', "DELETE"))
	def process_IN_CREATE(self, event):
#		print "in create ",event.pathname
		global flag
		if flag:
			check_moved_from()
			if(event.dir):
				notification_queue.append((event.name, event.pathname, '',"MKDIR"))
			else:
				notification_queue.append((event.name, event.pathname,'', "CREATE"))
	def process_IN_MOVED_FROM(self, event):
		global flag
		if flag:
			global moved_from_flag
			global moved_from_name
			global moved_from_loc
	#		print "in moved from of file ",event.pathname
			if (event.dir):
				if moved_from_flag==1:
					notification_queue((moved_from_name, moved_from_loc, '' , "RMDIR"))
				moved_from_flag	=	1
				moved_from_name =	event.name
				moved_from_loc	=	event.pathname
			else:
				notification_queue.append((event.name, event.pathname,'', "MOVED_FROM"))
	def process_IN_MOVED_TO(self, event):
#		print "in moved  to file ",event.pathname
		global flag
		if flag:
			global moved_from_flag
			global moved_from_name
			global moved_from_loc
			if(event.dir):
				if moved_from_flag==1:
					notification_queue.append((event.name,  event.pathname,moved_from_loc, "RENAMEDIR"))
					moved_from_flag	=	0
					moved_from_name =	''
					moved_from_loc	=	''

			else:
				notification_queue.append((event.name, event.pathname,'', "MOVED_TO"))
	def process_default(self, event):
		check_moved_from()
#		print "in default ",event.pathname




rootpath='/home/madhu/'
folder='ishani'
myp=12350
myhs=''
serp=12345
serhs=''

wm = WatchManager()			#somethng which creates a manager like thing to look wat all folders are to take care of
mask = pyinotify.ALL_EVENTS	#wat all events r to be notified
wm.add_watch(rootpath+folder, mask, rec=True,auto_add=True)
notifier = Notifier(wm, MyProcessing())	# connecting d manager and methods to call
thread1=myThread(1,'snd-'+folder+'-thread', folder, rootpath, myhs, myp, serhs, serp)
thread2=myThread(2,'rcv-'+folder+'-thread', folder, rootpath, myhs, myp, serhs, serp)
thread1.start()
thread2.start()
notifier.loop()	# start
print "thread started"

'''
create folder /home/madhu/trials/ishani  ----> let it be folder1
create folder /home/madhu/trials/ishani-ser----> let it be server
create folder /home/madhu/ishani----> let it be folder2
changes made in folder 1 will be tracked into server, which forwards the change requests to folder2..
hence changes made in folder 1 will be reflected in folder2, via server
folder1--->noti.py
folder2-->noti1.py
server-->ser.py
noti.py doesnt listen
noti1.py listens at port 12350, localhost
server listens at 12345, localhost

'''

