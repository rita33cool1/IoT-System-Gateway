#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import time
import librosa
import threading
import subprocess
import paho.mqtt.publish as publish

all_apps = ['audio1', 'audio2', 'audio3', 'audio4', 'audio5','audio6', 'audio7', 'audio8', 'audio9', 'audio10','audio11', 'audio12']

def readQosKnob():
    qos_knob_dict = {}
    with open('../QoSknob.txt', 'r') as rf:
        for l in rf.readlines():
            # QoSknob.txt is empty
            if ', ' not in l:
                print('QoSknob.txt is empty')
                time.sleep(10)
                return {}
            # QoSknob.txt is not empty
            app, knob = l.strip().split(', ', 1)
            knob = round(float(knob), 3) 
            if knob >= 1: knob = '1'
            #elif app[:5] == 'audio' and knob < 0.4 and knob >= 0: knob = '0.001'
            elif app[:5] == 'audio' and knob < 0.4: knob = '0.001'
            else: knob = str(knob)
            #if knob == 0: knob = '0.001'
            if app[:5] == 'audio':
                #qos_knob_dict[app[:6]] = knob
                qos_knob_dict[app] = knob
                print('app', 'knob')
                print(app, knob)
    return qos_knob_dict

def download_audio(number, ratio):
    try: 
        os.remove('audio_'+str(ratio)+'.wav')
    except: pass
    print(' Beginning downloading an audio')
    url = os.environ['STREAMURL'] + 'audio' + str(number) + '.wav'
    print('Audio url:', url)
    # Difault sampling rate: 22050
    cmd = 'ffmpeg -t 4 -i ' + url + ' -ar ' + str(int(float(ratio)*22050)) + ' audio_' + str(ratio) + '.wav'
    #cmd = 'ffmpeg -t 4 -i ' + url + ' -ar ' + str(int(float(ratio)*44100)) + ' audio_' + ratio + '.wav'
    print('cmd:', cmd)
    subprocess.run(cmd, shell=True)
    
'''
def resample(ratio, audio_name, saved_name):
    # Downsample, original default 22050
    y, sr = librosa.load(audio_name, sr=None) 
    print('Original sampling rate:', sr)
    print('Original audio time series:', y.shape)
    re_sr = int(ratio*sr)
    #y_ds = librosa.resample(y, sr, sr*ratio)
    librosa.output.write_wav(saved_name, y, re_sr)
    y_tmp, sr_tmp = librosa.load(saved_name, sr=None) 
    print('After downsampling, sampling rate:', sr_tmp)
    print('After downsampling, audio time series:', y_tmp.shape)
'''


if __name__ == '__main__':
    a = 0
    qos_knob_dict = {}
    while True:
        #tic = time.clock()
        # Read QoSknob.txt
        old_qos_knob_dict = qos_knob_dict
        qos_knob_dict = readQosKnob()
        
        a = (a%10) + 1
        # Avoid inaccurate audios: engine, jackhammer and children playing
        if a == 5 or a==7 or a == 9:
            a += 1
        
        # Download audio from stream server with knob x default sampling rate
        audio_knobs = []
        knob = '0'
        threads = []
        for app in qos_knob_dict:
            # Sampling rate is according to QoSknob.txt
            knob = qos_knob_dict[app]
            #if knob != 1 and knob != 0:
            if knob != '0':
                if knob not in audio_knobs:
                    while True:
                        try:
                            audio_knobs.append(knob)
                            down_knob_thread = threading.Thread(target=download_audio(a, knob))
                            down_knob_thread.start()
                            threads.append(down_knob_thread)
                        except:
                            time.sleep(10) 
                            continue
                        else: break

        # Wait until all threads are done
        for thread in threads:
            thread.join()
        
        # Publish
        knob = '0'
        for app in qos_knob_dict:
            knob = qos_knob_dict[app]
            if knob != '0':
                try: f = open('audio_'+knob+'.wav', 'rb')
                except: continue
                filecontent = f.read()
                publish.single("iot/iscc19/audio/"+app+"/audio_name", str(a), qos=1, hostname=os.environ['BROKER'])
                publish.single("iot/iscc19/audio/"+app+"/audio", filecontent, qos=1, hostname=os.environ['BROKER'])
        #toc = time.clock()
        #print('Used time:', toc-tic)
        #time.sleep(0.5)
        #if a == 1: break
