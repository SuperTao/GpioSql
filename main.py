#!/usr/bin/env python

import time
import select
import threading
import os

from ctypes import *

from datetime import datetime

import gpio
import mysql
import config
import ConfigureInotify

# 内核中gpio的序号
gpioTuple = (15, 14, 13, 12, 36, 37, 38, 39)

class HeartbeatThread(threading.Thread):
    first_connect = True
    upload_result = True

    def __init__(self): 
        threading.Thread.__init__(self)

    def run(self):
        # 打开C语言的库，可以调用里面的函数
        sqlserver = cdll.LoadLibrary(os.getcwd() + '/libsqlserver.so')
        while True:
            # 判断是否是这个类第一次连接
            if self.first_connect or self.upload_result == False:
#                print ('%s:%s' % (cfg.getRemoteIp(), cfg.getRemotePort()))
                # 链接sqlserver
                if sqlserver.openSqlserver(cfg.getRemoteUser().encode(), cfg.getRemotePassword().encode(), cfg.getRemoteDatabase().encode(), ('%s:%s' % (cfg.getRemoteIp(), cfg.getRemotePort())).encode(), cfg.getRemoteTable().encode()) == 0:
                    # 失败的话，1秒后重新连接
                    time.sleep(1)
                    continue
                # 连接成功，标志清除
                self.first_connect = False
                self.upload_result = True 
            # 获取锁
            mutexLock.acquire()
            # 发送心跳数据
            if sqlserver.heartbeat(1, '0'.encode(), 'heartbeat'.encode(), '1'.encode(), 0) == 0:
                # 失败的话，释放锁
                print ('heart beat error--------')
                mutexLock.release()
                self.upload_result = False
                continue

            mutexLock.release()
            time.sleep(int(cfg.getHeartbeatInterval()))

class UpdateMysqlThread(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self)

    def run(self):
        gpioFd = []
        # 创建数据库对象
        gpioDB = mysql.Mysql(cfg.getLocalIp(), int(cfg.getLocalPort()), cfg.getLocalUser(), cfg.getLocalPassword(), cfg.getLocalDatabase(), cfg.getLocalTable())
        # 连接数据库
        gpioDB.connectDatabase()
        epoll = select.epoll()
        # 初始化，更新一次本地所有的gpio的状态
        for gpioIndex in range(8):
            # 更新gpio口状态
            # 申请gpio
            gpio.gpioExport(gpioTuple[gpioIndex])
            # 设置为输入
            gpio.setInput(gpioTuple[gpioIndex])
            # 设置gpio的中断触发方式为双边沿触发
            gpio.setEdge(gpioTuple[gpioIndex], 'both')
            # 插入gpio的状态到sqlserver
            gpioDB.insertInto(gpioIndex, '%d' % (gpioIndex + 1) , 'gpio%d' % (gpioIndex+1), gpio.getInputValue(gpioTuple[gpioIndex]), gpioIndex)
            # 获取value的文件,后面的操作，文件都是一直打开的，避免重复打开关闭文件带来的时间上的浪费
            f = gpio.gpioInputFile(gpioTuple[gpioIndex])
            gpioFd.append(f)
            #print ('fileno: %d' % f.fileno())
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
                            # print ('f: %s' % value)
                            # 文件指针移动到文件开头
                            gpioFd[i].seek(0, 0)
                            # 保存到mysql中
                            gpioDB.insertInto(1, '%d' % (gpioIndex + 1) , 'gpio%d' % (i+1), value, gpioIndex)
                            break

            if event & select.EPOLLERR:
                pass

class UploadSqlserverThread(threading.Thread):
    first_connect = True
    upload_result = True

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        gpioDB = mysql.Mysql(cfg.getLocalIp(), int(cfg.getLocalPort()), cfg.getLocalUser(), cfg.getLocalPassword(), cfg.getLocalDatabase(), cfg.getLocalTable())
        gpioDB.connectDatabase()
        sqlserver = cdll.LoadLibrary(os.getcwd() + '/libsqlserver.so')
        while True:
            if self.first_connect or self.upload_result == False:
                #print ('%s:%s' % (cfg.getRemoteIp(), cfg.getRemotePort()))
                if sqlserver.openSqlserver(cfg.getRemoteUser().encode(), cfg.getRemotePassword().encode(), cfg.getRemoteDatabase().encode(), ('%s:%s' % (cfg.getRemoteIp(), cfg.getRemotePort())).encode(), cfg.getRemoteTable().encode()) == 0:
                    time.sleep(1)
                    continue
                self.first_connect = False
                self.upload_result = True
            # 获取目前的时间
            timeLocal = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # 获取本地数据库中，更新时间小于当前时间的数据
            results = gpioDB.selectByUpdateTime(timeLocal)
            # 得到的tuple顺序是反的，所以运行调整顺序
#            print('upload time ' + configureInotify.get_section_value('remote', 'interval_uploadData'))
            for res in results[::-1]:
                print (res)
                print (res[0])
                # 转换成时间戳
                t = res[5].timestamp()
                # 更新
                mutexLock.acquire()
                if sqlserver.insertInto(res[1], res[2].encode(), res[3].encode(), res[4].encode(), int(t), res[6]) == 0:
                    mutexLock.release()
                    # 更新数据失败，从新链接sqlserver
                    self.upload_result = False
                    continue
                mutexLock.release()
                # 更新完成的数据在本地删除
                gpioDB.deleteByRealDateLogId(res[0])
            time.sleep(int(cfg.getUploadInterval()))

if __name__ == '__main__':
    # 先释放所有的gpio端口，防止被其他应用程序占用
    gpio.unexportAllGPIO(gpioTuple)

    cfg = config.ConfigFile()
    # 打印一下配置文件中的一些参数k
    print (cfg.getRemoteIp())
    print (cfg.getRemotePort())
    print (cfg.getRemoteUser())
    print (cfg.getRemotePassword())

    # 线程锁
    # 由于heartbeat和上传数据都需要操作sqlserver，而且在不同的线程，所以需要考虑到资源抢占的问题
    mutexLock = threading.Lock()
    
    # 本地mysql数据库更新线程
    mysqlThread = UpdateMysqlThread()
    # 心跳进程，发送数据到sqlserver
    heartbeatThread = HeartbeatThread()
    # 更新本地gpio状态到sqlserver
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
