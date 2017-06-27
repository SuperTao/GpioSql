#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zengjf <zengjf42@163.com>

import configparser
import threading
import os
import pyinotify
import time
from pyinotify import WatchManager, Notifier, ProcessEvent

class InotifyEventHandler(ProcessEvent):
    def process_IN_MODIFY(self, event):
        # reparse the configure file
        if event.name.find(os.path.basename(ConfigureInotify.get_config_file())) == 0:
            ConfigureInotify.parse_config()

# 初始化配置
class ConfigureInotify(threading.Thread):

    __mutex = threading.Lock()
    #__configure_file_path = os.getcwd() + '/sql.conf'
    __configure_file_path = '/etc/aplex/config.ini'
    config = configparser.ConfigParser()

    # 使用单例模式来生成统一的对象
    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, "_inst"):

            # 单例对象
            cls._inst = super(ConfigureInotify, cls).__new__(cls)
            cls.config.read(cls.__configure_file_path)

        return cls._inst

    @classmethod
    def parse_config(cls):

        cls.__mutex.acquire()
        # 配置并解析配置文件
        cls.config.read(cls.__configure_file_path)
        cls.__mutex.release()

        print("parse_config")

    @classmethod
    def set_config_file(cls, file_path):

        cls.__configure_file_path = file_path

    @classmethod
    def get_config_file(cls):

        return cls.__configure_file_path

    @classmethod
    def run(cls):
        wm = WatchManager()
        mask = pyinotify.IN_MODIFY
        notifier = Notifier(wm, InotifyEventHandler())
        wm.add_watch(os.path.dirname(cls.__configure_file_path), mask, auto_add= True, rec=True)

        # print("now starting monitor config directory." )

        while True:
            try:
                notifier.process_events()
                if notifier.check_events():
                    notifier.read_events()
            except KeyboardInterrupt:
                print("keyboard Interrupt.")
                notifier.stop()
                break

    @classmethod
    def get_sections(cls):
        if cls.config != None :
            try:
                cls.__mutex.acquire()
                ret = cls.config.sections()
            except:
                ret = None
            finally:
                cls.__mutex.release()
                return ret
        else :
            return None

    @classmethod
    def get_section_value(cls, section, key):

        if cls.config != None :
            try:
                cls.__mutex.acquire()
                ret = cls.config[section][key]
            except:
                ret = None
            finally:
                cls.__mutex.release()
                return ret
        else :
            return None

configureInotify = ConfigureInotify()

if __name__ == '__main__':

    # 输出信息：
    #     < __main__.Configures object at 0x000001F27F04DE48 >
    #     < __main__.Configures object at 0x000001F27F04DE48 >
    #     < __main__.Configures object at 0x000001F27F04DE48 >
    print(ConfigureInotify())
    print(ConfigureInotify())
    print(configureInotify)

    configureInotify.set_config_file("/etc/aplex/sql.conf")
    #configureInotify.set_config_file("sql.conf")
    configureInotify.start()

    while True:
        print(configureInotify.get_sections())
        print(configureInotify.get_section_value("remote", "IP"))
        # time.sleep(50 / 1000)
        time.sleep(1)

