# Echo server program
import socket
import os

ishani='/home/madhu/ishani/'
ishani_ser='/home/madhu/ishani-ser/'
ishani_trash='/home/madhu/ishani-trash/'
	

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 12345              # Arbitrary non-privileged port
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
	if code == "CREATE":
		fname=str(conn.recv(1024))
		floc=ishani_ser+fname
		fd = open(floc, 'wb')
		if conn:
			dat = conn.recv(1024)
			if dat:
				while dat:
					fd.write(dat)
				dat=conn.recv(1024)
				fd.close()
		
	elif code == "DELETE":
		fname=str(conn.recv(1024))
		print fname
		floc=ishani_ser+fname
		os.system("rm "+floc+ " ;")
	elif code == "CUT":
		fname=str(conn.recv(1024))		
		fromq.append(fname);
		floc1=ishani_ser+fname
		floc2=ishani_trash+fname
		os.system("mv "+floc1+ "  "+floc2+" ;")
	elif code == "PASTE":
		fname1 = fromq.pop()	
		fname2=str(conn.recv(1024))		
		floc1=ishani_trash+fname1
		floc2=ishani_ser+fname2
		os.system("mv "+floc1+ "  "+floc2+" ;")
	conn.close()

					
sock.close()
print 'closed socket'



