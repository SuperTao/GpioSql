#!/usr/bin/env python

import time
import select
import threading
import os

from ctypes import *

from datetime import datetime

import gpio
import mysql

gpioTuple = (15, 14, 13, 12, 36, 37, 38, 39)

class HeartbeatThread(threading.Thread):
    first_connect = True
    def __init__(self): 
        threading.Thread.__init__(self)

    def run(self):
        sqlserver = cdll.LoadLibrary(os.getcwd() + '/libsqlserver.so')
#        sqlserver.openSqlserver()

        while True:
            if self.first_connect:
                if sqlserver.openSqlserver() == 0:
                    time.sleep(1)
                    continue
                self.first_connect = False
            mutexLock.acquire()
            print ('heartbeat......')
            if sqlserver.heartbeat(1, '0'.encode(), 'heartbeat'.encode(), '1'.encode(), 0) == 0:
                mutexLock.release()
                if sqlserver.openSqlserver() == 0:
                    continue
                continue
#return 0

            mutexLock.release()
            time.sleep(1)

class UpdateMysqlThread(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self)

    def run(self):
        gpioFd = []
        gpioDB = mysql.Mysql()
        gpioDB.connectDatabase()
        epoll = select.epoll()
        # 初始化，更新一次本地所有的gpio的状态
        for gpioIndex in range(8):
            # 更新gpio口状态
            gpio.gpioExport(gpioTuple[gpioIndex])
            gpio.setInput(gpioTuple[gpioIndex])
            gpio.setEdge(gpioTuple[gpioIndex], 'both')
            gpioDB.insertInto(gpioIndex, '%d' % (gpioIndex + 1) , 'gpio%d' % (gpioIndex+1), gpio.getInputValue(gpioTuple[gpioIndex]), gpioIndex)
            # 获取value的文件,后面的操作，文件都是一直打开的，避免重复打开关闭文件带来的时间上的浪费
            f = gpio.gpioInputFile(gpioTuple[gpioIndex])
            gpioFd.append(f)
            print ('fileno: %d' % f.fileno())
            # 注册到epoll中
            epoll.register(f, select.EPOLLERR | select.EPOLLPRI)
        while True:
            events = epoll.poll()
            for fileno, event in events:
                # 有数据要读取
                if event & select.EPOLLPRI:
                    # 循环检测哪个gpio的数据变化了，要读取
                    for i in range(8):
                        if fileno == gpioFd[i].fileno():
                            value = gpioFd[i].read().strip('\n')
                            print ('f: %s' % value)
                            # 文件指针移动到文件开头
                            gpioFd[i].seek(0, 0)
                            # 保存到mysql中
                            gpioDB.insertInto(1, '%d' % (gpioIndex + 1) , 'gpio%d' % (i+1), value, gpioIndex)
                            break

            if event & select.EPOLLERR:
                pass

class UploadSqlserverThread(threading.Thread):
    first_connect = True
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        gpioDB = mysql.Mysql()
        gpioDB.connectDatabase()
        sqlserver = cdll.LoadLibrary(os.getcwd() + '/libsqlserver.so')
#if (sqlserver.openSqlserver() == 0):
#            return 0
#        sqlserver.openSqlserver()
        print ('open sqlserver success')
        while True:
            if self.first_connect:
                if sqlserver.openSqlserver() == 0:
                    time.sleep(1)
                    continue
                self.first_connect = False
            # 获取目前的时间
            timeLocal = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # 获取本地数据库中，更新时间小于当前时间的数据
            results = gpioDB.selectByUpdateTime(timeLocal)
            # 得到的tuple顺序是反的，所以运行调整顺序
            for res in results[::-1]:
                print (res)
                print (res[0])
                # 转换成时间戳
                t = res[5].timestamp()
                # 更新
                mutexLock.acquire()
                if sqlserver.insertInto(res[1], res[2].encode(), res[3].encode(), res[4].encode(), int(t), res[6]) == 0:
                    print ('insert error----------------')
                    mutexLock.release()
                    if sqlserver.openSqlserver() == 0:
                        continue
                    continue
                # 更新完成的数据在本地删除
                mutexLock.release()
                gpioDB.deleteByRealDateLogId(res[0])
#gpioDB.deleteByUpdateTime(timeLocal)
            time.sleep(5)

if __name__ == '__main__':

    gpio.unexportAllGPIO(gpioTuple)

    mutexLock = threading.Lock()

    mysqlThread = UpdateMysqlThread()
    heartbeatThread = HeartbeatThread()
    sqlserverThread = UploadSqlserverThread()

    mysqlThread.daemon = True
    heartbeatThread.daemon = True
    sqlserverThread.daemon = True

    mysqlThread.start()
    heartbeatThread.start()
    sqlserverThread.start()

    mysqlThread.join()
    heartbeatThread.join()
    sqlserverThread.join()
