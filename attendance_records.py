#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division

import sys
import sys
import os

from PyQt4.QtCore import QSize, Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import datetime
import string
import shutil
from time import gmtime, strftime, sleep
import sqlite3



window_width = 700
window_height = 450
window_x = 400
window_y = 150
ip = '<IP>'
ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = "hh:mm:ss" # 12 or 24
date_format = "dd-MM-YYYY" # check python doc for strftime() for options
large_text_size = 14
medium_text_size = 12
small_text_size = 10

base_path = os.path.dirname(os.path.realpath(__file__))
dataset_path = os.path.join(base_path,'dataset')
tmp_path = os.path.join(base_path,'tmp')
db_path = os.path.join(base_path,'users.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()


def query(comm,params=None):
    conn.execute(comm,params)
    conn.commit()
    return cursor

def multiple_select_query(comm,params=()):
    cursor.execute(comm,params)
    res = cursor.fetchall()
    return res

def select_query(comm,params=()):
    cursor.execute(comm,params)
    res = cursor.fetchall()
    res =[x[0].encode('utf8') for x in res]
    return res

def int_select_query(comm,params=()):
    cursor.execute(comm,params)
    res = cursor.fetchall()
    res =[x[0] for x in res]
    return res

def id_generator(size=20, chars=string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


class RecordsTab(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super(RecordsTab, self).__init__()
        self.initUI()

    def initUI(self):

        font1 = QFont('Helvetica', small_text_size)
        font2 = QFont('Helvetica', medium_text_size)
        font3 = QFont('Helvetica', large_text_size)

        self.hbox=QHBoxLayout()
        self.vbox1= QVBoxLayout()
        
        self.left = QFrame()
        self.left.setFrameShape(QFrame.StyledPanel)
        self.left.setLayout(self.vbox1)

        
        self.recordsTable = QTableWidget()
        self.recordsTable.setRowCount(30)
        self.recordsTable.setContentsMargins(5,5,5,5)
        self.vbox1.addWidget(self.recordsTable)
        self.setLayout(self.vbox1)
        self.fetch_attendance_records()

        
        
        #self.vbox2.addStretch(2)

    def fetch_attendance_records(self):


        comm = "SELECT id, fname, lname FROM users ORDER BY id"
        res = multiple_select_query(comm)
        
        comm2 = "SELECT distinct date FROM users_present ORDER BY date"
        res2 = multiple_select_query(comm2)

        userids = []
        names = []
        dates = []
        


        self.recordsTable.setRowCount(len(res))
 
        
        for row in res:
            userids.append(row[0])
            names.append(row[1].encode('ascii','ignore')+' '+row[2].encode('ascii','ignore'))

        for row in res2:
            dates.append(row[0].encode('ascii','ignore'))

        headers = ['userid','name']

        for i in range(len(dates)):
            headers.append(dates[i])

        headers.append('total_presents')
        headers.append('attendance_percentage')

        self.recordsTable.setColumnCount(len(headers))
        self.recordsTable.setHorizontalHeaderLabels(headers)
        self.header = self.recordsTable.horizontalHeader()
        self.header.setResizeMode(QHeaderView.Stretch)
                
        for idx,userid in enumerate(userids):

            presents=[]
            present_cnt=0
            for j,date in enumerate(dates):

                comm = "SELECT COUNT(*) FROM users_present WHERE userid =? and date=?"
              
                res = int_select_query(comm,(userid,date))
                if res and res[0]!=0:
                    present_cnt=present_cnt+1
                    presents.append(1)
                else:
                    presents.append(0)
            
            row_content = [userid, names[idx]]
            
            for i in range(len(dates)):
                row_content.append(presents[i])

            row_content.append(present_cnt)
            row_content.append(round((present_cnt/len(dates)*100),2))

            for pos , item in enumerate(row_content):
                self.recordsTable.setItem(idx, pos , QTableWidgetItem(str(item)))
           
    
class MainWindow:
    def __init__(self): 
        self.qt = QTabWidget()
        geom = QDesktopWidget().availableGeometry()
        self.qt.setGeometry(geom)
        #self.qt.setGeometry(window_x, window_y, window_width, window_height)
        self.pal=QPalette()
        self.pal.setColor(QPalette.Background,Qt.white)
        self.pal.setColor(QPalette.Foreground,Qt.black)
        self.qt.setPalette(self.pal)
    
        self.tab = QWidget()
        self.RecordsTab=RecordsTab(self.tab)
        self.qt.addTab(self.RecordsTab,"Attendance Records")
        self.qt.setStyleSheet("""
        #box-border {
            border-style : solid;
            border-color : #BFC9CA;
            border-width : 2px;
            border-radius: 5px;

            
            }
        """)
        
        self.qt.setMouseTracking(True)
        #self.qt.showFullScreen()
        self.qt.show()
        
    def setMouseTracking(self, flag):
        def recursive_set(parent):
            for child in parent.findChildren(QtCore.QObject):
                try:
                    child.setMouseTracking(flag)
                except:
                    pass
                recursive_set(child)
        QtGui.QWidget.setMouseTracking(self, flag)
        recursive_set(self)

    def mouseMoveEvent(self, event):
        print 'mouseMoveEvent: x=%d, y=%d' % (event.x(), event.y())    


if __name__ == '__main__':
    a = QApplication(sys.argv)
    w = MainWindow()
   

    sys.exit(a.exec_())
