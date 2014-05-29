# Echo server program
import socket
import os

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
	print code
	conn.close()
	conn, addr = sock.accept()
	fname=str(conn.recv(1024))
	print code,"  ",fname
	if (code == "CREATE" or code=="MOVED_TO"):
		floc=ishani_ser+fname
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
		floc=ishani_ser+fname
		os.remove(floc)
	conn.close()	
sock.close()
print 'closed socket'



