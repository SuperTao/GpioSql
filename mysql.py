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

    def __init__(self):
        self.connect = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='aplex')
#        self.connection = pymysql.connect(**config)
        try:
            ''' connect database, create if not exists  '''
            with self.connect.cursor() as self.cursor:
                self.cursor.execute('create database if not exists gpio')
                self.cursor.execute('use gpio')
                self.cursor.execute('''create table if not exists real_date_log
                                (real_date_log_id int NOT NULL AUTO_INCREMENT,
                                PRIMARY KEY (real_date_log_id), 
                                device_id int, 
                                real_id varchar(50), 
                                name varchar(50), 
                                val varchar(50),
                                update_time datetime, 
                                flag int)''')
#                self.cursor.commit()
                self.connect.close()
#                cursor.close()
        except:
            print ('connect error')

    def __del__(self):
        pass
    
    def connectDatabase(self):
        self.connect = pymysql.connect(**config)
        self.cursor = self.connect.cursor()
        return True

    def insertInto(self, device_id, real_id, name, val, flag):
#conn = pymysql.connect(**config)
        try:
# with conn.cursor() as cursor:
            sql =   ('''   
                    INSERT INTO real_date_log  
                    (device_id ,real_id, name, val, update_time, flag) 
                    VALUES  
                    (%d, '%s', '%s', '%s', now(), %d) 
                    ''' % 
                    (device_id, real_id, name, val, flag))
            self.cursor.execute(sql)
            self.connect.commit()
#            self.cursor.close()
#self.cursor.execute(sql)
#            self.connection.commit()
#cursor.close()
        except:
            print ('error: execute sql')
#            connection.rollback()
        finally:
            pass
#            connection.close()

    def selectByDeviceId(self, device_id):
        try:
            sql = "SELECT  * from real_date_log where device_id=%d" % (device_id)
            self.cursor.execute(sql)
            results = self.cursor.fetchone()
            print (results)
            self.connect.commit()
            return results
        except:
            self.connect.rollback()

    def selectByRealDateLogId(self, real_date_log_id):
        try:
            sql = "SELECT  * from real_date_log where real_date_log_id=%d" % (real_date_log_id)
            print (sql)
            self.cursor.execute(sql)
            results = self.cursor.fetchone()
            print (results)
            self.connect.commit()
            return results
        except:
            self.connect.rollback()
#        finally:
#            self.cursor.close()
#            return results

    def close():
        self.cursor.close()
        self.connect.close()
