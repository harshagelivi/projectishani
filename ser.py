# Echo server program
import socket
import os
import shutil
import mysql.connector
from mysql.connector import errorcode
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('server_data.cfg')

#fill dese from config file
DB_NAME = config.get('database', 'name')
DB_USER = config.get('database', 'user')
DB_PASS = config.get('database', 'pass')
DB_HOST = config.get('database', 'host')


ishani='/home/harsha/ishani/'
ishani_ser='/home/harsha/ishani-ser/'
proj_home='/home/harsha/'

HOST = ''                 	# Symbolic name meaning all available interfaces
PORT = 12345              	# Arbitrary non-privileged port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((HOST, PORT))
sock.listen(10)

cnx = mysql.connector.connect(user=DB_USER, password=DB_PASS, host=DB_HOST)
cnx.database = DB_NAME    
cursor = cnx.cursor()
src_name=""
fromq=[]
def send_given_creds(ip, port, msg):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.connect((ip, port))
	sock.send(msg)
	sock.close()

def send_to_user(user_name, code, relative_name):
	user_ip=""
	if user_name=="user1":
		user_port=5678
	else:
		user_port=4567	
	send_given_creds(user_ip, user_port, code)
	send_given_creds(user_ip, user_port, relative_name)
	if (code=="MVDIR" or code=="MOVE"):
		global src_name
		user_ip=""
		if user_name=="user1":
			user_port=5678
		else:
			user_port=4567	
		send_given_creds(user_ip, user_port, src_name)
	if (code=="CREATE" or code=="MOVED_TO" ):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.connect((user_ip, user_port))
		fd = open(ishani_ser+relative_name,'rb')
		dat = fd.read(1024)
		while dat:
			sock.send(dat)
			dat=fd.read(1024)
		sock.close()
		fd.close()



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
		query = "select username from user_table where usergroup=0"
		cursor.execute(query)
		for name in cursor:
			user_name="{}".format(name[0])
			print "MKDIR ",user_name+relative_name
			#os.mkdir(user_path+relative_name)
			send_to_user(user_name, code, relative_name)
	if code == "RMDIR":
		shutil.rmtree(server_path)	
		query = "select username from user_table where usergroup=0"
		cursor.execute(query)
		for name in cursor:
			user_name="{}".format(name[0])
			print "RMDIR ",user_name+relative_name
			#shutil.rmtree(proj_home+user_path+relative_name)
			send_to_user(user_name, code, relative_name)			
	if (code=="MVDIR" or code=="MOVE"):
		conn, addr = sock.accept()
		src_name=str(conn.recv(1024))
		src_path=ishani_ser+src_name
		shutil.move(src_path, server_path)
		query = "select username from user_table where usergroup=0"
		cursor.execute(query)
		for name in cursor:
			user_name="{}".format(name[0])
			print "MOVING ",user_name+src_name,"  TO  ",user_name+relative_name
			#shutil.move(user_path+src_name, user_path+relative_name)
			send_to_user(user_name, code, relative_name)			
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
		query = "select username from user_table where usergroup=0"
		cursor.execute(query)
		for name in cursor:
			user_name="{}".format(name[0])
			print "CREATE ",user_name+relative_name
			#shutil.rmtree(proj_home+user_path+relative_name)
			send_to_user(user_name, code, relative_name)			
	if (code == "DELETE" or code=="MOVED_FROM"):
		if(os.path.exists(server_path)):
			os.remove(server_path)
		query = "select username from user_table where usergroup=0"
		cursor.execute(query)
		for name in cursor:
			user_name="{}".format(name[0])
			print "DELETE ",user_name+relative_name
			#shutil.move(user_path+src_name, user_path+relative_name)
			send_to_user(user_name, code, relative_name)			

sock.close()
print 'closed socket'



