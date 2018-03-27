#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import cv2

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import datetime
import string
import random
import shutil
from time import gmtime, strftime, sleep
import sqlite3


# import imageUpload.py for uploading captured images to cloudinary
import imageUpload as imup

# import MSFaceAPI.py for msface api calls
import MSFaceAPI as msface


large_text_size = 22
medium_text_size = 14
small_text_size = 10


base_path = os.path.dirname(os.path.realpath(__file__))
dataset_path = os.path.join(base_path,'dataset')
unknown_user_path=os.path.join(base_path,'unknowns')
tmp_path = os.path.join(base_path,'tmp')
placeholder_image = os.path.join(base_path,'placeholder_600x400.svg')
db_path = os.path.join(base_path,'users.db')

cloudinary_dataset = 'http://res.cloudinary.com/aish/image/upload/v1488457817/RTFRSS/dataset'
cloudinary_tmp = 'http://res.cloudinary.com/aish/image/upload/v1488457817/RTFRSS/tmp'

current_userid = 0
current_userfname = ''
detection_interval=10000
capture_interval=30
camera_port = 0

font1 = QFont('Helvetica', small_text_size)
font2 = QFont('Helvetica', medium_text_size)
font3 = QFont('Helvetica', large_text_size) 

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
TABLE_NAME="users"

cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascPath)

# function to generate a random id for image file name
def id_generator(size=20, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))



def make_dir(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise



class DynamicFrame(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(DynamicFrame, self).__init__()
        self.initUI()
        self.counter=0
        self.capture_cnt=0
        self.capture = cv2.VideoCapture(camera_port)

    def initUI(self):
        self.video_stream = QLabel()
        self.video_stream.setScaledContents(True)
        self.video_stream.setAlignment(Qt.AlignLeft)
        self.video_stream.setFixedSize(600,450)
        self.video_stream_label=QLabel('Live Video Stream')
        self.video_stream_label.setAlignment(Qt.AlignCenter)
        self.video_stream_label.setFont(font2)

        self.face_image = QLabel()
        self.face_image.setScaledContents(True)
        self.face_image.setFixedSize(600,450)
        self.face_image.setAlignment(Qt.AlignRight)
        self.face_image.setPixmap(QPixmap(placeholder_image))
        self.face_image_label=QLabel('Last Capture Results')
        self.face_image_label.setAlignment(Qt.AlignCenter)
        self.face_image_label.setFont(font2)

        self.vbox1=QVBoxLayout()
        self.vbox1.addWidget(self.video_stream)
        self.vbox1.addWidget(self.video_stream_label)        
        
        self.vbox2=QVBoxLayout()
        self.vbox2.addWidget(self.face_image)
        self.vbox2.addWidget(self.face_image_label)

        self.hbox=QHBoxLayout()
        self.hbox.addLayout(self.vbox1)
        self.hbox.addLayout(self.vbox2)
        self.hbox.setAlignment(Qt.AlignCenter)
        self.hbox.setSpacing(20)

        self.hbox2=QHBoxLayout()
        self.hbox2.setAlignment(Qt.AlignCenter)
        self.message_label=QLabel('message')
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setFont(font2)
        self.hbox2.addWidget(self.message_label)
        self.hbox2.setContentsMargins(20, 20, 20, 20)
        self.hbox2.setSpacing(10)

        self.label1 = QLabel('Real-Time Face Recognition based Surveillance')
        self.label2 = QLabel('')
        self.label1.setAlignment(Qt.AlignCenter)
        self.label2.setAlignment(Qt.AlignCenter)
        self.label1.setFont(font3)
        self.label2.setFont(font3)
        self.fbox = QFormLayout()
        self.fbox.setAlignment(Qt.AlignCenter)
        self.fbox.setContentsMargins(20, 20, 20, 20)
        self.fbox.addRow(self.label1)
        self.fbox.addRow(self.label2)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.fbox)
        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.hbox2)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.setLayout(self.vbox)

        self.update_check()

    def stop_capture(self):
        if self.capturing:
            self.capturing = False
            self.capture.release()
            self.timer.stop()
            cv2.destroyAllWindows()

    
    def update_check(self):
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.display_video_stream)
        self.video_timer.start(capture_interval)

    def display_video_stream(self):
        ret,frame = self.capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )


        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        image = QImage(frame, frame.shape[1], frame.shape[0],
                       frame.strides[0], QImage.Format_RGB888)

        self.video_stream.setPixmap(QPixmap.fromImage(image))
        self.message_label.setText('Next image capture in %d seconds' % int((detection_interval-self.counter*capture_interval)/1000))
        
        if self.counter==int(detection_interval/capture_interval):
            self.message_label.setText('Face identification started ...')
            self.update_dynamic_frame()
            self.counter=0
        else:
            self.counter=self.counter+1


    def update_dynamic_frame(self):
        global current_userid
        global current_userfname

        detected_personid =     ''
        welcome_names=''
        ramp_frames = 10
        
        print "Face identification started .........."
        cv2.destroyAllWindows()
        try:
            for i in xrange(ramp_frames):
                s, im = self.capture.read()   

            ret,frame = self.capture.read()
            #self.message_label.setText('Image Captured')
            self.capture_cnt+=1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

            
            print "Total Faces in Image = %d " % len(faces) 
            
            #self.message_label.setText("Total Faces in Image = %d " % len(faces))
            
            if len(faces) > 0:
                detected_persons = []
                persons = []
                persons_cnt=0
                detected_persons_cnt=0
                
                for (x, y, w, h) in faces:
                    if w*h>500:
                        persons_cnt+=1
                        image_crop = frame[y:y+h,x:x+w]
                        #self.message_label.setText("Processing.. %d " % persons_cnt)            
                        file_name = id_generator()+'.jpg'
                        file = os.path.join(tmp_path,file_name)
                        cloudinary_url=cloudinary_tmp + '/' + file_name        
                        cv2.imwrite(file, image_crop)
                        imup.upload_image(file,file_name)
                        faceid=msface.face_detect(cloudinary_url)
                        print "Result for person %d " % persons_cnt
                        print "Image File = " + str(file)
                        print "faceId = " + str(faceid)
                        detected_personid = msface.face_identify(faceid)
                        

                        if detected_personid:
                            print "detected_personid = " + str(detected_personid)
                            comm = "SELECT * FROM %s WHERE personid = '%s'" % (TABLE_NAME,detected_personid)
                            res = cursor.execute(comm)
                            res = cursor.fetchone()
                            if res:
                                userid = res[0]
                                uname = res[1]
                                fname = res[2]
                                lname = res[3]
                                print "Welcome %s !" % (fname+' '+lname)
                                detected_persons_cnt+=1
                                detected_persons.append(fname)
                                persons.append(fname)
                                now = datetime.datetime.now()
                                comm = "SELECT * FROM users_present WHERE userid = %d and date = '%s' " % (int(userid), now.strftime("%Y-%m-%d"))
                                #print comm
                                res2=cursor.execute(comm)
                                res2=cursor.fetchone()
                                if res2==None:
                                    format_str = "INSERT INTO users_present (id, userid) VALUES (NULL,%d)" %(int(userid)) 
                                    #print format_str
                                    conn.execute(format_str)
                                    conn.commit()
                                    print "Attendance marked for user %s " % uname
                                else
                                    print "Attendance already marked for user %s " % uname



                        
                        else:
                            time_str=strftime("%Y-%m-%d_%H:%M:%S", gmtime())
                            print "Unknown person found"
                            cv2.imwrite(os.path.join(unknown_user_path,'cam1_'+time_str+'.jpg'),image_crop)
                            persons.append('Unknown')
   
                if detected_persons_cnt > 1:        
                    for i in range(detected_persons_cnt-1):
                            welcome_names = welcome_names + detected_persons[i] + ', '
                    welcome_names=welcome_names[:-2]
                    welcome_names=welcome_names + ' & ' + detected_persons[detected_persons_cnt-1]
                elif detected_persons_cnt>0:
                    welcome_names = detected_persons[0]

                self.label2.setText('Hello '+ welcome_names)


            else:
                self.label2.setText('') 
                print "No person in image"               
            
            k=0
            
            for (x, y, w, h) in faces:
                if persons[k]!='Unknown':
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, persons[k],(x, y-10), cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(0,255,0),1)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, persons[k],(x, y-10), cv2.FONT_HERSHEY_COMPLEX_SMALL , 1,(0,0,255),1)

                k=k+1
            #image=cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_image = QImage(image, image.shape[1], image.shape[0],
                           image.strides[0], QImage.Format_RGB888)

            self.face_image.setPixmap(QPixmap.fromImage(face_image))
                                       
        except Exception as e:
            print "Errors occured !"
            print e
        

class FullscreenWindow:
    def __init__(self, parent, *args, **kwargs):
        self.qt = QWidget()
        self.qt.showFullScreen()
        self.qt.pal=QPalette()
        self.qt.pal.setColor(QPalette.Background,QColor(0,0,0))
        self.qt.pal.setColor(QPalette.Foreground,QColor(255,255,255))
        self.qt.setPalette(self.qt.pal)
        self.bg_color=0
        self.qt.hbox4 = QHBoxLayout()
        self.qt.Dynamicframe = DynamicFrame(self.qt)
        self.qt.hbox4.addWidget(self.qt.Dynamicframe)
        self.qt.vbox = QVBoxLayout()
        self.qt.vbox.addLayout(self.qt.hbox4)
        self.qt.setLayout(self.qt.vbox)



if __name__ == '__main__':
    make_dir(tmp_path)
    make_dir(unknown_user_path)
    for root, dirs, files in os.walk(tmp_path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    
    a = QApplication(sys.argv)
    w = FullscreenWindow(a)
    sys.exit(a.exec_())


# command to terminate the running program
# killall -9 python