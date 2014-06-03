# Echo client program
import socket
import os
import shutil

my_home='/home/harsha/user2/'

HOST =  ''   # The remote host
PORT = 4567# The same port as used by the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(10)

while True:
	conn, addr = sock.accept()
	code=str(conn.recv(1024))
	conn.close()
	conn, addr = sock.accept()
	relative_name=str(conn.recv(1024))
	conn.close()	
	user_path=my_home+relative_name
	print code,"  ",relative_name
	if code=="MKDIR":
		os.mkdir(user_path)
	if code == "RMDIR":
		shutil.rmtree(user_path)	
	if (code=="MVDIR" or code=="MOVE"):
		conn, addr = sock.accept()
		src_name=str(conn.recv(1024))
		src_path=my_home+src_name
		shutil.move(src_path, user_path)
	if (code == "CREATE" or code=="MOVED_TO"):
		fd = open(user_path, 'wb')
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
		if(os.path.exists(user_path)):
			os.remove(user_path)
sock.close()
print 'closed socket'



