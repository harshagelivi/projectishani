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

send_flag=1
flag=1
confirm_flag=1

def check_moved_from1():
	global moved_from_flag
	global moved_from_name
	global moved_from_loc
	moved_from_flag	=	0
	moved_from_name =	''
	moved_from_loc	=	''


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
    def __init__(self, threadID,name, foldername, rootpath,myhs, myp, myftp, serhs, serp):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.folder_name=foldername
        self.root_path=rootpath
        self.myhost=myhs
        self.myport=myp
        self.myftport=myftp
        self.server_port=serp
        self.server_host=serhs
	self.path=self.root_path+self.folder_name+'/'
    def run(self):
	global flag
	global send_flag
	global confirm_flag
	global notification_queue
	global send_queue
	global path
    	if self.name[0:3]=="snd":
		while  1:
			if notification_queue:
				p=notification_queue.popleft()
				if p[3]=="STOP":
					send_flag=0
				elif p[3]=="START":
					send_flag=1
				if send_flag==1 and p[3]!="START" and p[3]!="STOP" and p[0] and p[0][0]!='.' and p[0][-1]!='~':
					fname=p[1].replace(self.path,'')
					prevfname=p[2].replace(self.path,'')
					code=p[3]
					index=fname+'_'+prevfname+'_'+code
					try:
						if send_queue[index]:
							confirm_flag=0
							send_queue[index]=send_queue[index]-1
						else:
							confirm_flag=1
					except:
							confirm_flag=1
					if confirm_flag:
						if ((fname)):
							HOST =  self.server_host	# The remote host
							PORT =  self.server_port		# The same port as used by the server
							sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
							try:
								sock.connect((HOST, PORT))
								if (code=="RENAMEDIR" or code=="CREATE" or code=="MOVED_TO" or code=="DELETE" or 															code=="MOVED_FROM" or code=="MKDIR" or code=="RMDIR"):
									literal= '[' +'"'+code+'"'+ ','  +'"'+fname+'"'+ ',' +'"'+prevfname+'"'+ ',' + '"' + self.myhost + '"' +','+ '"'+str(self.myport)+'"'+',' +'"'+str(self.myftport)+'"' +']'
									sock.send(literal)
									sock.close()
									if code=="RENAMEDIR":		
										check_moved_from1()
							except:
								pass
						time.sleep(0.005)	

	elif self.name[0:3]=="rcv":
		HOST=self.myhost
		PORT=self.myport
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((HOST, PORT))
		sock.listen(800)
		folder=self.root_path+self.folder_name+"/"
		while True:
			conn, addr = sock.accept()
			literal=str(conn.recv(1024))
			conn.close()
			tup=ast.literal_eval(literal)
			code=tup[0]
			fname=tup[1]
			prevfname=tup[2]
			originhost=tup[3]
			originport=int(tup[4])
			notification_queue.append(("STOP", "STOP", '', "STOP"))
			flag=0
			index=fname+'_'+prevfname+'_'+code
			if self.myport!=originport or self.myhost!=originhost:
				try:
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
					elif (code == "DELETE" or code=="MOVED_FROM"):
						floc=folder+fname
						os.remove(floc)
					elif (code=="MKDIR"):
						os.mkdir(os.path.join(folder,fname))
					elif (code=="RMDIR"):
						shutil.rmtree(os.path.join(folder,fname))
					elif (code=="RENAMEDIR"):
							os.rename(os.path.join(folder, prevfname), os.path.join(folder, fname))
					try:
						send_queue[index]=send_queue[index]+1
					except:
						send_queue[index]=1
				except:
					pass
			notification_queue.append(("START", "START", '', "START"))
			flag=1
		sock.close()

	elif self.name[0:3]=="pro":
		rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rcv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		HOST=self.myhost
		PORT=self.myftport
		rcv_sock.bind((HOST, PORT))
		rcv_sock.listen(100)
		while True:
			try:
				conn, addr = rcv_sock.accept()
				request = str(conn.recv(1024))
				tup=ast.literal_eval(request)
				print tup[0]
				if tup[0]=="SEND_FILE":
					fname=tup[1]
					server_host=tup[2]
					server_ft_port=int(tup[3])
					print fname+server_host+str(server_ft_port)
					floc=self.root_path+self.folder_name+fname
					snd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					snd_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					snd_sock.connect((server_host, server_ft_port))
					floc=self.root_path+self.folder_name+'/'+fname
					try:
						fd = open(floc,'rb')
						dat = fd.read(1024)
						while dat:
							print "sending data"
							snd_sock.send(dat)
							dat=fd.read(1024)
						fd.close()
						print "data sent"	
					except:
						pass
					snd_sock.close()
				conn.close()
			except:
				pass




class MyProcessing(ProcessEvent):
	def __init__(self):
		pass
	def process_IN_CLOSE_WRITE(self, event):
		global flag
		if flag:
			check_moved_from()
			notification_queue.append((event.name, event.pathname, '',"CREATE"))
	def process_IN_DELETE(self, event):
		global flag
		if flag:
			check_moved_from()
			if(event.dir):
				notification_queue.append((event.name, event.pathname, '',"RMDIR"))
			else:
				notification_queue.append((event.name, event.pathname,'', "DELETE"))
	def process_IN_CREATE(self, event):
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
			if (event.dir):
				if moved_from_flag==1:
					notification_queue((moved_from_name, moved_from_loc, '' , "RMDIR"))
				moved_from_flag	=	1
				moved_from_name =	event.name
				moved_from_loc	=	event.pathname
			else:
				notification_queue.append((event.name, event.pathname,'', "MOVED_FROM"))
	def process_IN_MOVED_TO(self, event):
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

rootpath='/home/madhu/'
foldername='ishani'
myp=12350
myftp=12351
myhs=''
serp=12345
serhs=''

wm = WatchManager()			#somethng which creates a manager like thing to look wat all folders are to take care of
mask = pyinotify.ALL_EVENTS	#wat all events r to be notified
wm.add_watch(rootpath+foldername, mask, rec=True,auto_add=True)
notifier = Notifier(wm, MyProcessing())	# connecting d manager and methods to call
thread1=myThread(1,'snd-'+foldername+'-thread', foldername, rootpath, myhs, myp, myftp, serhs, serp)
thread2=myThread(2,'rcv-'+foldername+'-thread', foldername, rootpath, myhs, myp, myftp, serhs, serp)
thread3=myThread(3,'pro-'+foldername+'-thread', foldername, rootpath, myhs, myp, myftp, serhs, serp)
thread1.start()
thread2.start()
thread3.start()
notifier.loop()	# start
print "thread started"

