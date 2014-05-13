# Echo client program
import socket

HOST =  ''   # The remote host
PORT = 12345# The same port as used by the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect((HOST, PORT))
fd = open('file1_copy.txt', 'wb')

while True:
	print 'waiting for a connection....'
	dat = sock.recv(1024)
	if dat:
		print 'started getting data....'
		while dat:
			fd.write(dat)
			dat=sock.recv(1024)
		fd.close()
		print 'finished getting the data.'	
		break		
sock.close()
print 'closed the socket'
