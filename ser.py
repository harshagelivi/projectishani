import threading
import socket
import time
import os
import shutil
import ast
from collections import deque

users={}
users[12348]=''
users[12350]=''

smfr = threading.Semaphore()

available_port=12344
root_path='/home/madhu/trials/'
notification_q={}
received_q=deque()

def get_a_port():
	global available_port
	available_port=available_port+1
	return available_port

class myThread (threading.Thread):
    def __init__(self, threadID, name, port_num, port_num_ft, hostname,folder_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
	self.host_name=hostname
	self.port_num=port_num
	self.port_num_ft=port_num_ft
	self.folder_name=folder_name
	self.host_name=hostname
	global notification_q
	notification_q[self.folder_name]=deque()
    def run(self):
	global notification_q
	global received_q
	global root_path
	if self.name[0:3]=="rcv":
		global root_path
		HOST = self.host_name                 	# Symbolic name meaning all available interfaces
		PORT = self.port_num	  	# Arbitrary non-privileged port
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((HOST, PORT))
		sock.listen(80)
		while True:
			try:
				conn, addr = sock.accept()
				literal=str(conn.recv(1024))
	#			print "RCVD:---->",literal
				received_q.append(literal)
				conn.close()
			except:
				pass
		sock.close()
	elif self.name[0:3]=="snd":
		global users
		while True:
			try:
				if notification_q[self.folder_name]:
					n=notification_q[self.folder_name].popleft()
					tup=ast.literal_eval(n)
					for i in users:
						HOST=users[i]
						PORT=i
						sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
						sock.connect((HOST, PORT))
						sock.send(n)
						sock.close()
						if (tup[0]=="CREATE" or tup[0]=="MOVED_TO") and (int(tup[4]) != PORT or tup[3]!=HOST):
							sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
							sock.connect((HOST, PORT))
							try:
								fd = open(root_path+self.folder_name+'-ser/'+tup[1],'rb')
								dat = fd.read(1024)
								while dat:
									sock.send(dat)
									dat=fd.read(1024)
								fd.close()
								print "File sent"
							except:
								pass
							sock.close()
			except:
				pass
	elif self.name[0:3]=="pro":
		HOST = self.host_name                 	# Symbolic name meaning all available interfaces
		PORT = self.port_num_ft	  	# Arbitrary non-privileged port
		print "processor started!!"+HOST+str(PORT)
		rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		rcv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		rcv_sock.bind((HOST, PORT))
		rcv_sock.listen(100)
		folder=root_path+self.folder_name+'/'
		folder_ser=root_path+self.folder_name+'-ser/'
		while True:
			try:
				if received_q:
					literal = received_q.popleft()
					tup=ast.literal_eval(literal)
					code=tup[0]
					fname=tup[1]
					prevfname=tup[2]
					from_host=tup[3]
					from_port=int(tup[4])
					from_ft_port=int(tup[5])
					print literal
					if (code == "CREATE" or code=="MOVED_TO"):
						snd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						snd_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
						snd_sock.connect((from_host,from_ft_port))
						n= '[' +'"SEND_FILE"'+ ','  +'"'+fname+'"'+ ',' +'"' + HOST + '"' +','+ '"'+str(PORT)+'"' +']'
						snd_sock.send(n)
						snd_sock.close()
						conn, addr = rcv_sock.accept()
						floc=folder_ser+fname
						fd = open(floc, 'wb')
						if conn:
							dat = conn.recv(1024)
							if dat:
								while dat:
									fd.write(dat)
									dat=conn.recv(1024)
								fd.close()	
#							print "file recieved--->"+floc
						conn.close()
					elif (code == "DELETE" or code=="MOVED_FROM"):
						floc=folder_ser+fname
						try:
							os.remove(floc)
						except:
							pass
					elif (code=="MKDIR"):
						try:
							os.mkdir(os.path.join(folder_ser,fname))
						except:
							pass
					elif (code=="RMDIR"):
						try:
							shutil.rmtree(os.path.join(folder_ser,fname))
						except:
							pass
					elif (code=="RENAMEDIR"):
						try:
							os.rename(os.path.join(folder_ser, prevfname), os.path.join(folder_ser, fname))
						except:
							pass
					notification_q[self.folder_name].append(literal)
			except:
				pass
threads = []
hostname=''
mainport=12345
file_transfer_port=12346
# Create new threads
thread1 = myThread(1, "rcv-ishani-1",mainport,  file_transfer_port, hostname,"ishani");
thread2 = myThread(2, "snd-ishani-1",mainport,  file_transfer_port, hostname,"ishani");
thread3 = myThread(3, "pro-ishani-1",mainport,  file_transfer_port, hostname,"ishani");

# Start new Threads
thread1.start()
thread2.start()
thread3.start()

# Add threads to thread list
threads.append(thread1)
threads.append(thread2)
threads.append(thread3)

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"

