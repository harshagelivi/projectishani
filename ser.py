#!/usr/bin/python

import threading
import socket
import time
import os
import shutil

available_port=12344
root_path='/home/madhu/trials/'
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

    def run(self):
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
	folder_trash=root_path+self.folder_name+'-trash/'
	while True:
		conn, addr = sock.accept()
		code=str(conn.recv(1024))
		print code
		conn.close()
		conn, addr = sock.accept()
		if (code == "CREATE" or code=="MOVED_TO"):
			fname=str(conn.recv(1024))
			floc=folder_ser+fname
			fd = open(floc, 'wb')
			conn.close()
			conn, addr = sock.accept()
			if conn:
				dat = conn.recv(1024)
				if dat:
					while dat:
						fd.write(dat)
						dat=conn.recv(1024)
					fd.close()		
		elif (code == "DELETE" or code=="MOVED_FROM"):
			fname=str(conn.recv(1024))
			print fname
			floc=folder_ser+fname
			try:
				'''os.remove(os.path.join(folder_ser,fname))'''
				os.remove(floc)
			except:
				pass
		elif (code=="MKDIR"):
			fname=str(conn.recv(1024))
			print fname
			try:
				os.mkdir(os.path.join(folder_ser,fname))
			except:
				pass
		elif (code=="RMDIR"):
			fname=str(conn.recv(1024))
			print "rmdir ----"+os.path.join(folder_ser,fname)
			try:
				shutil.rmtree(os.path.join(folder_ser,fname))
			except:
				pass
		elif (code=="RENAMEDIR"):
			fname=str(conn.recv(1024))
			print "fname  : "+fname			
			conn.close()
			conn, addr = sock.accept()			
			prevfname=str(conn.recv(1024))
			print "prevfname  : "+prevfname
			print "---"+ os.path.join(folder_ser, prevfname)+"---"+os.path.join(folder_ser, fname)
			try:
				os.rename(os.path.join(folder_ser, prevfname), os.path.join(folder_ser, fname))
			except:
				pass
		conn.close()
		print "closed the connection"
        sock.close()
        print "closed the socket"

threads = []

# Create new threads
thread1 = myThread(1, "Thread-1", get_a_port(), "ishani");
thread2 = myThread(2, "Thread-2", get_a_port(), "kiwi");
thread3 = myThread(3, "Thread-3", get_a_port(), "mango");

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
