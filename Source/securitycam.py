#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 16:13:23 2020

@author: maxi
Warning: This code is really dirty,
I didnt have much time
"""

import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime
import traceback
import time
import os
import dbm
import pickle
import sys

db = dbm.open('config', 'r')
confs = pickle.loads(db['confs'])
config = {}
for conf in confs:
    if conf['type'] == 'str':
        config[conf['key']] = str(conf['value'])
    elif conf['type'] == 'float':
        config[conf['key']] = float(conf['value'])
    elif conf['type'] == 'list':
        config[conf['key']] = conf['value'].split(',')
    else:
        sys.exit('undefined type {}'.format(conf['type']))
# Set variables that will be neded
mailto = config['mailto']
date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# log = open('/home/pi/logs/log_{}'.format(date), 'w')
# sys.stdout = log
print('starting securitycam script')
path = '/home/pi/Pictures/Security_' + date + '/'
interval = config['interval']
area = config['minarea']
sleep = True
print('creating path')
if not os.path.exists(path):
    os.mkdir(path)
template = """\
<html>
    <body>
    <h1 style="color: red">Something Moved in your house!!!</h1>
    <p<Hello {name},<br>
    Today something moved in your house<br>
    the pictures are:<br></p>
    <img src="cid:1">
    <img src="cid:2">
    <p>{date}<br>
    Script made by Maxi Schmeling</p>
    </body>
</html>"""
# def funcs


def draw_around(img, contour):
    ret = img.copy()
    for cont in contour:
        if cv2.contourArea(cont) >= area:
            (x, y, w, h) = cv2.boundingRect(cont)
            cv2.rectangle(ret, (x, y), (x + w, y + h), (0, 0, 255), 2)
        else:
            pass
    return ret


def sendmail(img, diff, nowdate):
    impathaft = path + 'frame_before_{date}.jpg'.format(date=nowdate)
    impath = path + 'frame_diff_{date}.jpg'.format(date=nowdate)
    cv2.imwrite(impathaft, img)
    cv2.imwrite(impath, diff)
    msg = MIMEMultipart()
    msg['Subject'] = 'House Alert!!'
    msg['From'] = 'maxicarlos08@gmx.de'
    msg['To'] = ",".join(mailto)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(template.format(name='maxi', date=nowdate), 'html')
    msg.attach(msgText)

    # This example assumes the image is in the current directory
    af = open(impathaft, 'rb')
    msgaf = MIMEImage(af.read())
    bf = open(impath, 'rb')
    msgbf = MIMEImage(bf.read())
    af.close()
    bf.close()

    # Define the image ID
    msgaf.add_header('Content-ID', '<1>')
    msg.attach(msgaf)
    msgbf.add_header('Content-ID', '<2>')
    msg.attach(msgbf)
    s = smtplib.SMTP(host=config['mailserver'], port=config['port'])
    s.starttls()
    s.login(config['login'], config['passwd'])
    s.send_message(msg)
    s.quit()


def main(cam):
    new = cam.read()[1]
    gray = cv2.GaussianBlur(cv2.cvtColor(new, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    time.sleep(interval)
    print('start checking')
    while True:
        try:
            first = gray
            actualdate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            ret, new = cam.read()
            if ret is None:
                print('Noneimage found!!!')
                continue
            gray = cv2.GaussianBlur(cv2.cvtColor(new, cv2.COLOR_BGR2GRAY),
                                    (21, 21), 0)
            rawdif = cv2.absdiff(gray, first)
            diff = cv2.threshold(rawdif,
                                 100, 255,
                                 cv2.THRESH_BINARY)[1]
            diff = cv2.dilate(diff, None, iterations=2)
            # diff = cv2.absdiff(new, first)
            buh, contours, bla = cv2.findContours(diff, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            for cnt in contours:
                if cv2.contourArea(cnt) >= area:
                    print('contour found')
                    print(cv2.contourArea(cnt))
                    img = draw_around(new, contours)
                    senddif = draw_around(rawdif, contours)
                    sendmail(img, senddif, actualdate)
                    time.sleep(interval)
                    gray = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2GRAY)
                    sleep = False
                    break
                else:
                    pass
            if sleep: time.sleep(interval)
            else: sleep = True

        except:
            cam.release()
            traceback.print_exc()
            break


print('sleeping 30 secs')
time.sleep(30)
print('Strated')
if __name__ == '__main__':
    while True:
        try:
            cam = cv2.VideoCapture(0)
            main(cam)
        except:
            cam.release()
            time.sleep(10)
