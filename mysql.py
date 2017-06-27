#!/usr/bin/env python

from datetime import date, datetime, timedelta
import pymysql

config = {
    'host':     '127.0.0.1',
    'port':     3306,
    'user':     'root',
    'password': 'aplex',
    'db':       'gpio',      
    'charset':  'utf8'
}

class Mysql:
    connect = None 
    cursor = None

#    def __init__(self):
    def __init__(self, Ip, Port, User, Passwd, Database, Table):
        self.ip = Ip
        self.port = Port
        self.user = User
        self.password = Passwd
        self.database = Database
        self.table = Table
        # 连接sqlserver服务器, 尝试连接并初始化数据库和数据表
        self.connect = pymysql.connect(host=self.ip, port=self.port, user=self.user, password=self.password)
#self.connect = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='aplex')
        try:
            ''' connect database, create if not exists  '''
            with self.connect.cursor() as self.cursor:
                # 查看数据库是否存在，没有就创建数据库
                self.cursor.execute('create database if not exists %s' % (self.database))
                self.cursor.execute('use %s' % (self.database))
                # 查看数据表是否存在，没有就创建
                self.cursor.execute('''create table if not exists %s 
                                (real_date_log_id int NOT NULL AUTO_INCREMENT,
                                PRIMARY KEY (real_date_log_id), 
                                device_id int, 
                                real_id varchar(50), 
                                name varchar(50), 
                                val varchar(50),
                                update_time datetime, 
                                flag int)''' % (self.table))
#flag int)'''))
                self.cursor.commit()
                self.connect.close()
        except:
            print ('connect error')

    def __del__(self):
        pass

    # 连接数据库和其中的数据表 
    def connectDatabase(self):
        self.connect = pymysql.connect(host=self.ip, port=self.port, user=self.user, password=self.password, db=self.database)
        self.cursor = self.connect.cursor()
        return True

    def insertInto(self, device_id, real_id, name, val, flag):
        try:
            sql =   ('''   
                    INSERT INTO real_date_log
                    (device_id ,real_id, name, val, update_time, flag) 
                    VALUES  
                    (%d, '%s', '%s', '%s', now(), %d) 
                    ''' % 
                    (device_id, real_id, name, val, flag))
            self.cursor.execute(sql)
            self.connect.commit()
        except:
            print ('error: execute sql')
        finally:
            pass

    def selectByDeviceId(self, device_id):
        try:
            sql = "SELECT  * from %s where device_id=%d" % (self.table, device_id)
            self.cursor.execute(sql)
            results = self.cursor.fetchone()
#            print (results)
            self.connect.commit()
            return results
        except:
            self.connect.rollback()

    def selectByRealDateLogId(self, real_date_log_id):
        try:
            sql = "SELECT  * from %s where real_date_log_id=%d" % (self.table, real_date_log_id)
            self.cursor.execute(sql)
            results = self.cursor.fetchone()
#            print (results)
            self.connect.commit()
            return results
        except:
            self.connect.rollback()

    def selectByUpdateTime(self, currentTime):
        try:
            sql = "SELECT  * from %s where update_time<'%s'" % (self.table, currentTime)
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.connect.commit()
            return results
        except:
            self.connect.rollback()

    def deleteByUpdateTime(self, currentTime):
        try:
            sql = "DELETE from %s where update_time<'%s'" % (self, currentTime)
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.connect.commit()
            return results
        except:
            self.connect.rollback()

    def deleteByRealDateLogId(self, real_date_log_id):
        try:
            sql = "DELETE from %s where real_date_log_id=%d" % (self.table, real_date_log_id)
            self.cursor.execute(sql)
            results = self.cursor.fetchone()
#            print (results)
            self.connect.commit()
            return results
        except:
            self.connect.rollback()

    def close():
        self.cursor.close()
        self.connect.close()

