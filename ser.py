# Echo server program
import socket
import os
import shutil

ishani='/home/harsha/ishani/'
ishani_ser='/home/harsha/ishani-ser/'
ishani_trash='/home/harsha/ishani-trash/'
	

HOST = ''                 	# Symbolic name meaning all available interfaces
PORT = 12345              	# Arbitrary non-privileged port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(10)

fromq=[]

while True:
	conn, addr = sock.accept()
	code=str(conn.recv(1024))
	conn.close()
	conn, addr = sock.accept()
	relative_name=str(conn.recv(1024))
	conn.close()	
	server_path=ishani_ser+relative_name
	print code,"  ",relative_name
	if code=="MKDIR":
		os.mkdir(server_path)
	if code == "RMDIR":
		shutil.rmtree(server_path)	
	if (code=="MVDIR" or code=="MOVE"):
		conn, addr = sock.accept()
		src_name=str(conn.recv(1024))
		src_path=ishani_ser+src_name
		shutil.move(src_path, server_path)
	if (code == "CREATE" or code=="MOVED_TO"):
		fd = open(server_path, 'wb')
		conn, addr = sock.accept()
		if conn:
			dat = conn.recv(1024)
			if dat:
				while dat:
					fd.write(dat)
					dat=conn.recv(1024)
				fd.close()
				conn.close()
		
	if (code == "DELETE" or code=="MOVED_FROM"):
		os.remove(server_path)
sock.close()
print 'closed socket'



