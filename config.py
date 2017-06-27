#!/usr/bin/env python

import os

import configparser
import ConfigureInotify

class ConfigFile(object):
    def __init__(self):
        # 查看当前目录是否存在sql.conf文件
        #if os.path.isfile(os.getcwd() + '/sql.conf') == False:
        if os.path.isfile('/etc/aplex/config.ini') == False:
            # 如果不存在文件，就创建配置文件，并添加默认值
            cfg = configparser.ConfigParser()
            cfg.add_section('remote')
            cfg.set('remote', 'ip' ,'115.29.245.156')
            cfg.set('remote', 'port' ,'40949')
            cfg.set('remote', 'user' ,'wangzg')
            cfg.set('remote', 'password' ,'Wangzg123456')
            cfg.set('remote', 'database' ,'wangzg')
            cfg.set('remote', 'table' ,'real_date_log')
        
            cfg.add_section('localhost')
            cfg.set('localhost', 'ip' ,'127.0.0.1')
            cfg.set('localhost', 'port' ,'3306')
            cfg.set('localhost', 'user' ,'root')
            cfg.set('localhost', 'password' ,'aplex')
            cfg.set('localhost', 'database' ,'gpio')
            cfg.set('localhost', 'table' ,'real_date_log')
        
            cfg.add_section('interval')
            cfg.set('interval', 'heartbeat', '1')
            cfg.set('interval', 'upload_data', '5')
        
            #cfg.write(open(os.getcwd() + '/sql.conf', 'w+'))
            cfg.write(open('/etc/aplex/config.ini', 'w+'))

        # 新建一个监听文件变化的类
        self.cfgIno = ConfigureInotify.ConfigureInotify()
        # 设置要监听文件
        #self.cfgIno.set_config_file("sql.conf")
        self.cfgIno.set_config_file("/etc/aplex/config.ini")
        # 开始监听
        self.cfgIno.start()
    
    def getRemoteIp(self):
        return self.cfgIno.get_section_value('remote', 'ip')

    def getRemotePort(self):
        return self.cfgIno.get_section_value('remote', 'port')

    def getRemoteUser(self):
        return self.cfgIno.get_section_value('remote', 'user')

    def getRemotePassword(self):
        return self.cfgIno.get_section_value('remote', 'password')
        
    def getRemoteDatabase(self):
        return self.cfgIno.get_section_value('remote', 'database')

    def getRemoteTable(self):
        return self.cfgIno.get_section_value('remote', 'table')

    def getLocalIp(self):
        return self.cfgIno.get_section_value('loaclhost', 'ip')

    def getLocalPort(self):
        return self.cfgIno.get_section_value('localhost', 'port')

    def getLocalUser(self):
        return self.cfgIno.get_section_value('localhost', 'user')

    def getLocalPassword(self):
        return self.cfgIno.get_section_value('localhost', 'password')

    def getLocalDatabase(self):
        return self.cfgIno.get_section_value('localhost', 'database')

    def getLocalTable(self):
        return self.cfgIno.get_section_value('localhost', 'table')
       
    def getHeartbeatInterval(self):
        return self.cfgIno.get_section_value('interval', 'heartbeat')

    def getUploadInterval(self):
        return self.cfgIno.get_section_value('interval', 'upload_data')
        
