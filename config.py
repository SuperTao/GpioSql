#!/usr/bin/env python

import os

import ConfigParser

if os.path.isfile(os.getcwd() + '/sql.conf') == False:
    cfg = ConfigParser.ConfigParser()
    cfg.add_section('remote')
    cfg.set('remote', 'ip' ,'115.29.245.156')
    cfg.set('remote', 'port' ,'40949')
    cfg.set('remote', 'user' ,'wangzg')
    cfg.set('remote', 'password' ,'wangzg123456')
    cfg.set('remote', 'table' ,'real_date_log')

    cfg.add_section('localhost')
    cfg.set('localhost', 'ip' ,'127.0.0.1')
    cfg.set('localhost', 'port' ,'3306')
    cfg.set('localhost', 'user' ,'root')
    cfg.set('localhost', 'password' ,'aplex')

    cfg.add_section('interval')
    cfg.set('interval', 'heartbeat', '1')
    cfg.set('interval', 'upload_data', '5')

    cfg.write(open('./sql.conf', 'w+'))

else:
    cfg = ConfigParser.ConfigParser()
    cfg.read('./sql.conf')
    print cfg.items('remote')
    print cfg.get('remote', 'ip')
    print cfg.getint('remote', 'port')
    print cfg.get('remote', 'user')
    print cfg.get('remote', 'password')
    print cfg.get('remote', 'table')

    print cfg.items('localhost')
    print cfg.get('remote', 'ip')
    print cfg.getint('remote', 'port')
    print cfg.get('remote', 'user')
    print cfg.get('remote', 'password')

    print cfg.items('interval')
    print cfg.get('interval', 'heartbeat')
    print cfg.get('interval', 'upload_data')


