#!/usr/bin/env python

import time
import threading
import os
from ctypes import *

from datetime import datetime

import gpio
import mysql

real_date_log_id = 1

gpioTuple = (15, 14, 13, 12, 36, 37, 38, 39)

class HeartbeatThread(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self)

    def run(self):
        gpioDB = mysql.Mysql()
        gpioDB.connectDatabase()
        while True:
            gpioDB.insertInto(0, '0', 'heartbeat', '1', 0)
            time.sleep(1)

class UpdateMysqlThread(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self)

    def run(self):
        gpioDB = mysql.Mysql()
        gpioDB.connectDatabase()
        while True:
            for gpioIndex in range(8):
                gpioDB.insertInto(gpioIndex, '%d' % (gpioIndex + 1) , 'gpio%d' % (gpioIndex+1), gpio.getGpioValue(gpioTuple[gpioIndex]), gpioIndex)
            time.sleep(1)

class UploadSqlserverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        gpioDB = mysql.Mysql()
        gpioDB.connectDatabase()
        sqlserver = cdll.LoadLibrary(os.getcwd() + '/libsqlserver.so')
        if (sqlserver.openSqlserver() == 0):
            return 0
        print ('open sqlserver success')
        global real_date_log_id
        while True:
            for i in range(9):
                res = gpioDB.selectByRealDateLogId(real_date_log_id)
                print ("id: %d" % real_date_log_id)
                print (res)
                real_date_log_id += 1
#res = gpioDB.selectByDeviceId(1)
#print (res)
                t = res[5].timestamp()
                sqlserver.insertInto(res[1], res[2].encode(), res[3].encode(), res[4].encode(), int(t), res[6])
            time.sleep(1)

if __name__ == '__main__':
    real_date_log_id = 1
    mysqlThread = UpdateMysqlThread()
    heartbeatThread = HeartbeatThread()
    sqlserverThread = UploadSqlserverThread()

    mysqlThread.daemon = True
    heartbeatThread.daemon = True
    sqlserverThread.daemon = True

#    mysqlThread.start()
#    heartbeatThread.start()
    sqlserverThread.start()

#    mysqlThread.join()
#    heartbeatThread.join()
    sqlserverThread.join()
