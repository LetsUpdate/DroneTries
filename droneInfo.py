import sys
import os
import msvcrt as m
import socket


def exit(message):
    print(message)
    print("press a button to continoue.......")
    m.getch()
    sys.exit()

if(len(sys.argv)<=1):
    exit("no arguments")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = int(sys.argv[1])
sock.bind(('',port))


while True:
    try:
        data,server=sock.recvfrom(1518)
        infoString =data.decode(encoding="utf-8")
        infoString=infoString[:-1]
        splittedInfo= infoString.split(";")
        os.system('cls')
        for x in splittedInfo:
            print(x);

    except:
        exit("reciver exception")
