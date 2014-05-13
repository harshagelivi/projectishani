# Echo server program
import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 12345              # Arbitrary non-privileged port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(3)
while True:
	conn, addr = sock.accept()
	if conn:
		print 'got a conection from '+str(addr)
		fd = open('file1.txt','rb')
		dat = fd.read(1024)
		print 'opened and sending the file....'
		while dat:
			conn.send(dat)
			dat=fd.read(1024)
		conn.close()
		fd.close()
		print 'closed the connection and file.'
		print 'successfully sent the file.'
sock.close()
print 'closed socket'
