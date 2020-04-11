import socket
import keyboard
import threading
import os
import cv2
import numpy as np
import time

MESSAGE_PORT=8889
INFO_PORT=8890
VIDEO_PORT=11111
DRONE_IP="192.168.10.1"
PC_IP="192.168.10.2"
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

messageSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
messageSock.bind((PC_IP,MESSAGE_PORT))

def send(message):
    messageSock.sendto(message.encode(encoding="utf-8"),(DRONE_IP,MESSAGE_PORT))

def reciveMessages():
    print("starting reciver!")
    while True:
        try:
            data,server=messageSock.recvfrom(1518)
            print("[MESSAGE]: "+data.decode(encoding="utf-8"))
        except:
            print("reciver thread exception")
            
recvThread = threading.Thread(target=reciveMessages)
recvThread.start()

send("command")

send("streamon")
time.sleep(3)
cap = cv2.VideoCapture('udp://@' + DRONE_IP + ':' + str(VIDEO_PORT))

width=960/2 #(resized)
height=720/2#(resized)
goodDistance=304
cWidth=int(width/2)
cHeight=int(height/2)

while True:
    ret, img = cap.read()
    small_frame = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    gray = cv2.cvtColor(small_frame,cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(gray,1.3,5)
    cv2.circle(small_frame,(cWidth,cHeight),10,(0,255,0),2)

    boxCenterX=0
    boxCenterY=0
    vDistance=[0,0,0]

    for(x, y, w, h) in faces:

        end_cord_x = x + w
        end_cord_y = y + h
        targ_cord_x = int((end_cord_x + x)/2)
        targ_cord_y = int((end_cord_y + y)/2)
        cv2.rectangle(small_frame, (x, y), (end_cord_x, end_cord_y), (255,0,0), 2)
        cv2.circle(small_frame, (targ_cord_x, targ_cord_y), 10, (0,255,0), 2)
        end_size = w*2
        vTrue = np.array((cWidth,cHeight,304))
        vTarget = np.array((targ_cord_x,targ_cord_y,end_size))
        vDistance = vTrue-vTarget

    text="[" +str(boxCenterX)+", "+str(boxCenterY)+"]"
    cv2.putText(small_frame,str(vDistance),(0,64),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
    cv2.imshow('img',small_frame)
    if cv2.waitKey (1)&0xFF == ord ('q'):
        break
cap.release()
cv2.destroyAllWindows()
send("land")
time.sleep(3)
send("land")
