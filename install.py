#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 10:09:23 2020

@author: maxi
"""


import os
import sys

if os.getuid() != 0:
    sys.exit('Script must bee done as root')
print("""\
      Welcome to the securitycam installer script,
      you will be asked do answear some questions
      about the installation now,
      we will need to install some dependencies now""")

packages = 'python3 python3-dev python3-opencv samba samba-common-bin'

if input('do you want to install them? [y, n]') == 'y':
    os.system('apt install ' + packages)

else:
    sys.exit('Cant use this without packages')