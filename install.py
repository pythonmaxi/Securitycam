#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:09:23 2020

@author: maxi
"""


import os
import sys
import dbm
import pickle
import getpass

os.chdir('/'.join(__file__.split('/')[0:-1]))

if os.getuid() != 0:
    raise PermissionError('Script must be run as root')
print("""\
Welcome to the securitycam installer script,
you will be asked do answear some questions
about the installation now,
we will need to install some dependencies now""")

packages = 'python3-dev python3-opencv samba samba-common-bin'

if input('do you want to install them? [y, n]') == 'y':
    os.system('apt install ' + packages)

else:
    sys.exit('Cant use this without packages')

print('setup the configuration')
db = dbm.open('config', 'c')
confs = [{'key': 'mailserver',
          'value': input('url of mailserver: '),
          'type': 'str'},
         {'key': 'port',
          'value': input('mailserver port'),
          'type': 'str'},
         {'key': 'login',
          'value': input('your login mail'),
          'type': 'str'},
         {'key': 'passwd',
          'value': input('your mail password'),
          'type': 'str'},
         {'key': 'interval',
          'value': input('interval of check, should be less than 2'),
          'type': 'float'},
         {'key': 'mailto',
          'value': input('your mailing list'),
          'type': 'list'},
         {'key': 'minarea',
          'value': input('minimal area of detection'),
          'type': 'int'}]

raw_conf = pickle.dumps(confs)
db['confs'] = raw_conf
db.close()

print('''\
Do you want to intall samba (Share saved photos on local network)
Warning: Your current configuration file wil be moved to /etc/samba/smb.conf.bak''', end='')
if input('[y,n]') == 'y':
    os.system('mv /etc/samba/smb.conf /etc/samba/smb.conf.bak')
    os.system('mv smb.conf /etc/samba/smb.conf')
    print('''\
Done moving files
restarting samba''')
    os.system('systemctl restart smbd')
    accept = input('Do you want to replace rc.local file?\nthis will backup your previos rc.local file [y,n]')
    if accept == 'y':
        os.system()