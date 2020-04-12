import socket
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
control=False
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

SPEED_LIMIT=35
SPEED_TRESHOLD=10
TURN_LIMIT=100
TURN_TRESHOLD=10
FLOAT_LIMIT=60
FLOAT_TRESHOLD=10

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

def videoProcessing():
    time.sleep(5)
    cap = cv2.VideoCapture('udp://@' + DRONE_IP + ':' + str(VIDEO_PORT))

    width=960/2 #(resized)
    height=720/2#(resized)
    goodDistance=200
    cWidth=int(width/2)
    cHeight=int((height-50)/2)
    lastvDistance=[0,0,0]
    dropTime = time.time()
    while True:
        ret, img = cap.read()
        small_frame = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small_frame,cv2.COLOR_BGR2GRAY)
        faces=face_cascade.detectMultiScale(gray,1.3,5)

        vDistance=[0,0,0]

        boxCenterX=0
        boxCenterY=0
       

        for(x, y, w, h) in faces:
    
            end_cord_x = x + w
            end_cord_y = y + h
            targ_cord_x = int((end_cord_x + x)/2)
            targ_cord_y = int((end_cord_y + y)/2)
            cv2.rectangle(small_frame, (x, y), (end_cord_x, end_cord_y), (255,0,0), 2)
            cv2.circle(small_frame, (targ_cord_x, targ_cord_y), 10, (0,255,0), 2)
            end_size = w*2
            vTrue = np.array((cWidth,cHeight,goodDistance))
            vTarget = np.array((targ_cord_x,targ_cord_y,end_size))
            vDistance = vTrue-vTarget

        text="[" +str(boxCenterX)+", "+str(boxCenterY)+"]"

        if(isArrayFullOfZero(vDistance) and (time.time()<dropTime)):
            vDistance = lastvDistance
        else:
            lastvDistance=vDistance
            dropTime=time.time()+1

        if(control):
            controller(vDistance)

        cv2.circle(small_frame,(cWidth,cHeight),10,(0,255,0),2)
        cv2.putText(small_frame,str(vDistance),(0,64),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
        cv2.imshow('img',small_frame)
        if cv2.waitKey (1)&0xFF == ord ('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def isArrayFullOfZero(array):
    for a in array:
        if(a!=0):
            return False;
    return True

def limiter(vaule, limit,treshold):
    if((vaule<treshold) and (vaule>-treshold)):
        return 0

    if(vaule>limit):
        return limit
    if(vaule<-limit):
        return -limit
    return vaule

def controller(vektor):
    
    send("rc 0 "+str(limiter(vektor[2]/2,SPEED_LIMIT,SPEED_TRESHOLD))+' '+str(limiter(vektor[1]/2,FLOAT_LIMIT,FLOAT_TRESHOLD))+' '+str(limiter(-vektor[0]/2,TURN_LIMIT,TURN_TRESHOLD)))

send("command")
send("streamon")
send("battery?")


videoThread = threading.Thread(target=videoProcessing)
videoThread.start()
os.system("start droneInfo.py "+str(INFO_PORT))
while True:
    be=input().lower()
    if (be=="kill"):
        control=False;
        send("emergency")
    elif (be=="stop"):
        control=False
        send("land")
    elif(be=="start"):
        send("takeoff")
        time.sleep(6)
        send("up 60")
        control=True
    elif(be=="on"):
        control=True
    elif(be=="off"):
        control=False;
    else:
        send(be)
