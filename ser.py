#!/usr/bin/python

import threading
import socket
import time
import os
import shutil
import ast
from collections import deque

available_port=12344
root_path='/home/madhu/trials/'
notification_q={}

def get_a_port():
	global available_port
	available_port=available_port+1
	return available_port

class myThread (threading.Thread):
    def __init__(self, threadID, name, port_num, folder_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
	self.port_num=port_num
	self.folder_name=folder_name
	global notification_q
	notification_q[self.folder_name]=deque()
    def run(self):
	global notification_q
	if self.name[0:3]=="rcv":
		global root_path
		HOST = ''                 	# Symbolic name meaning all available interfaces
		PORT = self.port_num	  	# Arbitrary non-privileged port
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((HOST, PORT))
		sock.listen(80)
		from_stack=[]
		folder=root_path+self.folder_name+'/'
		folder_ser=root_path+self.folder_name+'-ser/'
		while True:
			conn, addr = sock.accept()
			literal=str(conn.recv(1024))
			print literal
			conn.close()
			tup=ast.literal_eval(literal)
			code=tup[0]
			fname=tup[1]
			prevfname=tup[2]
			if (code == "CREATE" or code=="MOVED_TO"):
				floc=folder_ser+fname
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
				print fname
				floc=folder_ser+fname
				try:
					'''os.remove(os.path.join(folder_ser,fname))'''
					os.remove(floc)
				except:
					pass
			elif (code=="MKDIR"):
				print fname
				try:
					os.mkdir(os.path.join(folder_ser,fname))
				except:
					pass
			elif (code=="RMDIR"):
				print "rmdir ----"+os.path.join(folder_ser,fname)
				try:
					shutil.rmtree(os.path.join(folder_ser,fname))
				except:
					pass
			elif (code=="RENAMEDIR"):
				print "fname  : "+fname			
				print "prevfname  : "+prevfname
				print "---"+ os.path.join(folder_ser, prevfname)+"---"+os.path.join(folder_ser, fname)
				try:
					os.rename(os.path.join(folder_ser, prevfname), os.path.join(folder_ser, fname))
				except:
					pass
		
			print "closed the connection"
			notification_q[self.folder_name].append(literal)
		sock.close()
		print "closed the socket"
	elif self.name[0:3]=="snd":
		HOST=''
		PORT=12350
		while True:
			if notification_q[self.folder_name]:
				n=notification_q[self.folder_name].popleft()
				tup=ast.literal_eval(n)
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				sock.connect((HOST, PORT))
				sock.send(n)
				sock.close()
				if tup[0]=="CREATE" or tup[0]=="MOVED_TO":
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					sock.connect((HOST, PORT))
					print root_path+tup[1] + "---------> to be rewrited"
					fd = open(root_path+self.folder_name+'/'+tup[1],'rb')
					dat = fd.read(1024)
					while dat:
						print "sending data"
						sock.send(dat)
						dat=fd.read(1024)
					fd.close()
					sock.close()
		
threads = []

# Create new threads
thread1 = myThread(1, "rcv-ishani-1", get_a_port(), "ishani");
thread2 = myThread(2, "snd-ishani-1", 0, "ishani");

# Start new Threads
thread1.start()
thread2.start()

# Add threads to thread list
threads.append(thread1)
threads.append(thread2)

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"

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

