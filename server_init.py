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

TABLES = {}
TABLES['user_table'] = (
    "CREATE TABLE `user_table` ("
    "  `username` varchar(20) NOT NULL ,"
    "  `password` varchar(20) NOT NULL,"
    "  `usergroup` int(11) NOT NULL,"
    "  PRIMARY KEY (`username`)"
    ") ")

TABLES['active_table'] = (
    "CREATE TABLE `active_table` ("
    "  `username` varchar(20) NOT NULL ,"
    "  `ip` varchar(16) NOT NULL,"
    "  `port` int(11) NOT NULL,"
    "  CONSTRAINT `user_exists` FOREIGN KEY (`username`) "
    "     REFERENCES `user_table` (`username`) ON DELETE CASCADE, "
    "  PRIMARY KEY (`username`)"
    ") ")
cnx = mysql.connector.connect(user=DB_USER, password=DB_PASS, host=DB_HOST)
cursor = cnx.cursor()
def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME    
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)
for name, ddl in TABLES.iteritems():
    try:
        print("Creating table {}: ".format(name)),
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
i=0
while i<4:
	act_users=config.items('users')
	add_user = ("INSERT INTO user_table (username, password, usergroup) VALUES "+act_users[i][1])
	cursor.execute(add_user)
	i=i+1
cnx.commit()	
cursor.close()
cnx.close()
