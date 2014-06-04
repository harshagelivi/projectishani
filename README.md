ishani
======

A Simple Folder synchronisation application

Developed in python and bash

One-way sync of shared folders

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


