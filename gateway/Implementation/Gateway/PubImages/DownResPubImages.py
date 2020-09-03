#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import cv2
import time
import random
import subprocess
from datetime import datetime
import paho.mqtt.publish as publish

all_apps = ['yolo1', 'yolo2', 'yolo3', 'yolo4', 'yolo5', 'yolo6', 'yolo7', 'yolo8', 'yolo9', 'yolo10', 'yolo11', 'yolo12']
RTSPURL = os.environ['RTSPURL']
IMAGEHEAD = 'original_'
TIMEPERIOD = 2
RANDOMRANGE = 100000000
#POSTFIXRANGE = 1000
#MAXKNOB = 0.844
MAXKNOB = 1
#MINKNOB = 0.2
RATIO1 = 0.31
ZEROKNOB = 0.01

def readQosKnob():
    qos_knob_dict_list = []
    with open('../QoSknob.txt', 'r') as rf:
        for l in rf.readlines():
            # QoSknob.txt is empty
            if ', ' not in l:
                print('QoSknob.txt is empty')
                return {}
            # QoSknob.txt is not empty
            app, knob = l.strip().split(', ', 1)
            knob = round(float(knob), 3)
            if app[:4] == 'yolo': 
                if knob > 1: knob = 1
                # knob minimum is 0.2
                # Avoid knob become zero
                elif knob <= 0: knob = 0.01
                qos_knob_dict = {}
                qos_knob_dict[app] = knob
                qos_knob_dict_list.append(qos_knob_dict)
                #print('app', 'knob')
                #print(app, knob)
    return qos_knob_dict_list

def download(random_number):
    print(' Beginning downloading a image')
    image_name = IMAGEHEAD + random_number + '.jpg'
    #cmd = f'ffmpeg -i {RTSPURL} -f image2 -vf fps=1/{TIMEPERIOD} {image_name}'
    cmd = f'ffmpeg -i {RTSPURL} -f image2 -vframes 1 {image_name}'
    #print('CMD: ' + cmd)
    output = subprocess.run(cmd, shell=True)
    return image_name

def resize(imratio, img_name, saved_name):
    np_img_ori = cv2.imread(img_name)
    np_img_height, np_img_width, np_img_channels = np_img_ori.shape
    #print(np_img_height, np_img_width)
    imratio = imratio**(0.5)
    np_resize = cv2.resize(np_img_ori, (int(np_img_width*imratio), int(np_img_height*imratio)))
    cv2.imwrite(saved_name, np_resize)
    np_img_height, np_img_width, np_img_channels = np_resize.shape
    #print(np_img_height, np_img_width)

def PublishImages(image_name, image_number_str, app):
    f = open(image_name, 'rb')
    filecontent = f.read()
    byteArr = bytes(filecontent)
    publish.single("iot/iscc19/image/"+app+"/image_name", image_number_str, qos=1, hostname=os.environ['BROKER'])
    publish.single("iot/iscc19/image/"+app+"/image", byteArr, qos=1, hostname=os.environ['BROKER'])

def RandomNumber(random_range):
    random_number = random.randint(0, random_range-1)
    diff = len(str(random_range)) - 1 - len(str(random_number)) 
    add_0 = ''
    for i in range(diff):
        add_0 += '0'
    random_n_str = add_0 + str(random_number)
    return random_n_str

if __name__ == '__main__':
    if len(sys.argv) < 2: 
        date_time = datetime.now().strftime("%m%d_%H%M/")
        image_folder = 'original/' + date_time
    else:
        image_folder = sys.argv[1] if sys.argv[1][-1] == '/' else sys.argv[1]+'/'
    try: os.makedirs(image_folder)
    except: pass
    IMAGEHEAD = image_folder + IMAGEHEAD 
    #k = 0
    while True:
        tic = time.clock()
        #if k > 0: break
        # Read QoSknob.txt
        qos_knob_list = readQosKnob()
        
        # Download image from stream server
        # Produce a random number
        while True:
            random_n_str = RandomNumber(RANDOMRANGE)
            try: original_image = download(random_n_str)
            except: continue
            #else: break
            
            #print('original_image: ' + original_image)
        
            # Resize and Publish
            # Resize knob = 1
            image_1 = 'image_1.0' + '.jpg'
            # 600x800 (55KB) to 186x248 (24KB), use ratio 0.31
            try: resize(RATIO1, original_image, image_1)
            except: continue
            else: break
        ## Resize knob = 0.844
        #image_max = 'image_' + str(MAXKNOB) + '.jpg'
        #resize(MAXKNOB, image_1, image_max)
        # Resize knob = 0
        image_zero = 'image_' + str(ZEROKNOB) +'.jpg'
        resize(ZEROKNOB, image_1, image_zero)

        # Resize images according to QoSknob.txt
        resize_knobs = [ZEROKNOB, 1]
        resize_apps = []
        for app in qos_knob_list:
            app_name = list(app.keys())[0]
            knob = app[app_name]
            image_name = 'image_' + str(knob) + '.jpg'
            if knob not in resize_knobs:
                resize(knob, image_1, image_name)
                resize_knobs.append(knob)
            # Publish to the cloud server
            # Produce random number for postfix
            #postfix_n_str = RandomNumber(POSTFIXRANGE)
            print('image_name: ' + image_name)
            #print('image_number: ' + random_n_str+'_'+postfix_n_str)
            print('image_number: ' + random_n_str)
            print('app_name: ' + app_name)
            #PublishImages(image_name, random_n_str+'_'+postfix_n_str, app_name)
            PublishImages(image_name, random_n_str, app_name)
            #if app_name not in resize_apps: resize_apps.append(app_name) 
        #print('resize_apps', resize_apps)       
        
        '''
        # Resize images for apps not in QoSknob.txt
        for app in all_apps:
            if app not in resize_apps:
                # Publish to the cloud server
                # Produce random number for postfix
                postfix_n_str = RandomNumber(POSTFIXRANGE)
                print('image_name: ' + image_zero)
                print('image_number: ' + random_n_str+'_'+postfix_n_str)
                print('app_name: ' + app)
                PublishImages(image_zero, random_n_str+'_'+postfix_n_str, app)
        '''
        
        toc = time.clock()
        print('Used time:', toc-tic)
        time.sleep(TIMEPERIOD)
        #k += 1
        #if k == 20: break
