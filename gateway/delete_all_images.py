#!/usr/bin/env python3

__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import time
import subprocess
from datetime import datetime

#provider = 'yujungwang/'
provider = os.environ['DOCKER_PROVIDER'] + '/'
#provider = '192.168.1.100:5000/'
#repo = 'iscc19'
repo = os.environ['DOCKER_REPO']
password = os.environ['PASSWORD']

pull_audio_cmds = [
    'docker pull '+provider+repo+':s2-audio-1', 'docker pull '+provider+repo+':s2-audio-2', 
    'docker pull '+provider+repo+':s2-audio-3', 'docker pull '+provider+repo+':s2-audio-4',
    'docker pull '+provider+repo+':s2-audio-5', 'docker pull '+provider+repo+':s2-audio-6', 
    'docker pull '+provider+repo+':s2-audio-7', 'docker pull '+provider+repo+':s2-audio-8',
    'docker pull '+provider+repo+':s2-audio-9', 'docker pull '+provider+repo+':s2-audio-10', 
    'docker pull '+provider+repo+':s2-audio-11', 'docker pull '+provider+repo+':s2-audio-12'
]

pull_yolo_cmds = [
    'docker pull '+provider+repo+':s2-yolo-1', 'docker pull '+provider+repo+':s2-yolo-2', 
    'docker pull '+provider+repo+':s2-yolo-3', 'docker pull '+provider+repo+':s2-yolo-4',
    'docker pull '+provider+repo+':s2-yolo-5', 'docker pull '+provider+repo+':s2-yolo-6', 
    'docker pull '+provider+repo+':s2-yolo-7', 'docker pull '+provider+repo+':s2-yolo-8',
    'docker pull '+provider+repo+':s2-yolo-9', 'docker pull '+provider+repo+':s2-yolo-10', 
    'docker pull '+provider+repo+':s2-yolo-11', 'docker pull '+provider+repo+':s2-yolo-12'
]

delete_audio_cmds = [
    'docker rmi '+provider+repo+':s2-audio-1', 'docker rmi '+provider+repo+':s2-audio-2', 
    'docker rmi '+provider+repo+':s2-audio-3', 'docker rmi '+provider+repo+':s2-audio-4',
    'docker rmi '+provider+repo+':s2-audio-5', 'docker rmi '+provider+repo+':s2-audio-6', 
    'docker rmi '+provider+repo+':s2-audio-7', 'docker rmi '+provider+repo+':s2-audio-8',
    'docker rmi '+provider+repo+':s2-audio-9', 'docker rmi '+provider+repo+':s2-audio-10', 
    'docker rmi '+provider+repo+':s2-audio-11', 'docker rmi '+provider+repo+':s2-audio-12'
]

delete_yolo_cmds = [
    'docker rmi '+provider+repo+':s2-yolo-1', 'docker rmi '+provider+repo+':s2-yolo-2', 
    'docker rmi '+provider+repo+':s2-yolo-3', 'docker rmi '+provider+repo+':s2-yolo-4',
    'docker rmi '+provider+repo+':s2-yolo-5', 'docker rmi '+provider+repo+':s2-yolo-6', 
    'docker rmi '+provider+repo+':s2-yolo-7', 'docker rmi '+provider+repo+':s2-yolo-8',
    'docker rmi '+provider+repo+':s2-yolo-9', 'docker rmi '+provider+repo+':s2-yolo-10', 
    'docker rmi '+provider+repo+':s2-yolo-11', 'docker rmi '+provider+repo+':s2-yolo-12'
]

# Clean all the replacement record
cmd = f'rm /home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log'
subprocess.run(cmd, shell=True)
cmd = f'echo "" > /home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log'
subprocess.run(cmd, shell=True)
print('delete images_replce.log finish') 

# Clean all the allocation record
cmd = f'rm /home/minion/YC/iscc19/Implementation/Gateway/QoSknob.txt'
subprocess.run(cmd, shell=True)
cmd = f'echo "" > /home/minion/YC/iscc19/Implementation/Gateway/QoSknob.txt'
subprocess.run(cmd, shell=True)
#print('Clean all the allocation record')

# Make sure delete the whole image 
cmd = f'sed -i "1c 40" /home/minion/YC/YC-docker-engine/delete_layer_num'
subprocess.run(cmd, shell=True)

# Start to screenshot and publish images
# Stop and kill previous screenshot 
cmd = f'screen -S PubImage -X quit'
subprocess.run(cmd, shell=True)
print('Stop and Kill previous screenshot')
time.sleep(5)
"""
# Stop and kill previous recording
cmd = f'screen -S PubAudio -X quit'
subprocess.run(cmd, shell=True)
print('Stop and Kill previous recording')
time.sleep(5)
"""
# Algorithm
if sys.argv[1] == 'end' or sys.argv[1] == 'END':
    sys.exit("It's END")
#print(f'Algorithm: {sys.argv[1]}')
cmd = f'rm /home/minion/YC/iscc19/Algorithm.txt'
subprocess.run(cmd, shell=True)
cmd = f'echo {sys.argv[1]} > /home/minion/YC/iscc19/Algorithm.txt'
subprocess.run(cmd, shell=True)
# Start PubImage screen and PubImage
cmd = f'screen -S PubImage -d -m bash /home/minion/YC/iscc19/PubImage.sh'
subprocess.run(cmd, shell=True)
print('Restart PubImage')
time.sleep(20)

"""
# Start to record and publish audios
## Stop and kill previous recording
#cmd = f'screen -S PubAudio -X quit'
#subprocess.run(cmd, shell=True)
#print('Stop and Kill previous recording')
#time.sleep(5)
# Start to record and publish audios
cmd = f'screen -S PubAudio -d -m bash YC/iscc19/PubAudio.sh'
subprocess.run(cmd, shell=True)
print('Restart PubAudio')
time.sleep(20)
"""

# Restart docker engine
# Stop docker engine
cmd = f'screen -S docker_screen -X stuff ^C'
subprocess.run(cmd, shell=True)
print('Stop docker engine')
time.sleep(15)
cmd = f'screen -S docker_screen -X stuff "exit\r"'
subprocess.run(cmd, shell=True)
print('Kill docker screen')
time.sleep(3)
# Start docker screen and docker engine
cmd = f'screen -S docker_screen -d -m bash /home/minion/YC/iscc19/delete_all_images.sh'
output = subprocess.run(cmd, shell=True)
print('Restart docker engine')
time.sleep(30)
cmd = f'docker ps -a | grep Exit | cut -d " " -f 1 | xargs  docker rm'
output = subprocess.run(cmd, shell=True)
print('Remove docker existed containers')
time.sleep(1)

pull_process = []
for cmd in pull_audio_cmds:
    p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    pull_process.append(p)
    (stdoutput,erroutput) = p.communicate() 
    if erroutput is not None:
        print(erroutput)
    
for process in pull_process:
    p.wait()
print('Pull audio over')

del pull_process
pull_process = []
for cmd in pull_yolo_cmds:
    p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
    pull_process.append(p)
    (stdoutput,erroutput) = p.communicate() 
    if erroutput is not None:
        print(erroutput)
    
for process in pull_process:
    p.wait()
print('Pull yolo over')

for cmd in delete_audio_cmds:
    p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
print('Delete audio over')

for cmd in delete_yolo_cmds:
    p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
print('Delete audio over')
