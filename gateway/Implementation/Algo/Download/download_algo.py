#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
python download_algo.py {registry_size} {bandwidth} {analytics} {IDA_method}
{registry_size}: 6 (default 6G)
{bandwidth}: 176000 (default 176Mbps)
{analytics}: 'analytics.input' (default)
'analytics.input': 
audio1-18                                                                                            
audio4-1
audio4-13
...
{method}: DP (Dynamic Programing), Lagrange (Lagrangian)

images_dict structure
{
  "ImageName":
  {
      "LayerID": is_exist (int type)
      "LayerID": is_exist (int type)
          ...
  }
  "ImageName": 
  ...
}
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import time
import math
import json
# list.copy only support since python 3.3 so use this instead
import copy
import docker
import commands
import subprocess
# To get the same items in a list
import collections
# write log
from datetime import datetime
from itertools import takewhile
import paho.mqtt.publish as publish


Duration = 5 # minutes

overall_images = {
    'yolo1':{}, 'yolo2':{}, 'yolo3':{}, 'yolo4':{}, 'yolo5':{}, 'yolo6':{},
    'yolo7':{}, 'yolo8':{}, 'yolo9':{}, 'yolo10':{}, 'yolo11':{}, 'yolo12':{},               
    'audio1':{}, 'audio2':{}, 'audio3':{}, 'audio4':{}, 'audio5':{}, 'audio6':{},
    'audio7':{}, 'audio8':{}, 'audio9':{}, 'audio10':{}, 'audio11':{}, 'audio12':{}
}

const_overall_containers = { 
    "yolo1":{"CPU":55.6,"RAM":13.08,"SIZE":1.81,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo2":{"CPU":55.6,"RAM":13.08,"SIZE":2.25,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo3":{"CPU":55.6,"RAM":13.08,"SIZE":2.61,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo4":{"CPU":55.6,"RAM":13.08,"SIZE":2.96,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo5":{"CPU":55.6,"RAM":13.08,"SIZE":1.81,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo6":{"CPU":55.6,"RAM":13.08,"SIZE":2.25,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo7":{"CPU":55.6,"RAM":13.08,"SIZE":2.61,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo8":{"CPU":55.6,"RAM":13.08,"SIZE":2.96,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo9":{"CPU":55.6,"RAM":13.08,"SIZE":1.81,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo10":{"CPU":55.6,"RAM":13.08,"SIZE":2.25,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo11":{"CPU":55.6,"RAM":13.08,"SIZE":2.61,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "yolo12":{"CPU":55.6,"RAM":13.08,"SIZE":2.96,"BW":22.48, "COMLAYER":0, "LAYER":0},
    "audio1":{"CPU":51.3,"RAM":7.84,"SIZE":2.03,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio2":{"CPU":51.3,"RAM":7.84,"SIZE":2.49,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio3":{"CPU":51.3,"RAM":7.84,"SIZE":2.85,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio4":{"CPU":51.3,"RAM":7.84,"SIZE":3.13,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio5":{"CPU":51.3,"RAM":7.84,"SIZE":2.03,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio6":{"CPU":51.3,"RAM":7.84,"SIZE":2.49,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio7":{"CPU":51.3,"RAM":7.84,"SIZE":2.85,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio8":{"CPU":51.3,"RAM":7.84,"SIZE":3.13,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio9":{"CPU":51.3,"RAM":7.84,"SIZE":2.03,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio10":{"CPU":51.3,"RAM":7.84,"SIZE":2.49,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio11":{"CPU":51.3,"RAM":7.84,"SIZE":2.85,"BW":688.52, "COMLAYER":0, "LAYER":0},
    "audio12":{"CPU":51.3,"RAM":7.84,"SIZE":3.13,"BW":688.52, "COMLAYER":0, "LAYER":0},
}
"""
{
    "yolo5":{"CPU":55.6,"RAM":13.08,"SIZE":3.6,"BW":24.08, "COMLAYER":0, "LAYER":0},
    "audio5":{"CPU":51.3,"RAM":7.84,"SIZE":3.48,"BW":688.52, "COMLAYER":0, "LAYER":0}
}
"""

overall_containers = copy.deepcopy(const_overall_containers)
overall_com_layers = {}
overall_layers = {}
#overall_repo = 'yujungwang/iscc19'
overall_repo = os.environ['DOCKER_PROVIDER'] + '/' + os.environ['DOCKER_REPO']


def read_image_json(imgs_list, is_exist):
    images_dict = {}
    for img in imgs_list:
        images_dict[img] = {}

    com_layers = {}    
    layers = {}    
    for img in images_dict:
        if 'yolo' in img:
            img_name = 's2-yolo-' + img.split('yolo')[-1]
        elif 'audio' in img:
            img_name = 's2-audio-' + img.split('audio')[-1]
        #print('img_name: ' + img_name)
        with open('/home/minion/YC/iscc19/Implementation/Algo/Download/image_'+img_name+'.json', 'r') as reader:
            jf = json.loads(reader.read())
            #images_dict[img]['Layers'] = jf['Layers']
            for l in jf['Layers']:
                if l['LayerID'] not in com_layers:
                    # Convert unit to Byte
                    com_size, unit = l['CompressLayerSize'].split(' ', 1)
                    if unit == 'GB':
                        com_layers[l['LayerID']] = float(com_size)*1000*1000*1000
                    elif unit == 'MB':
                        com_layers[l['LayerID']] = float(com_size)*1000*1000
                    elif unit == 'KB':
                        com_layers[l['LayerID']] = float(com_size)*1000
                    else: # B
                        com_layers[l['LayerID']] = float(com_size)

                images_dict[img][l['LayerID']] = is_exist
                # Bytes
                layers[l['LayerID']] = float(l['LayerSize']) 
    return images_dict, com_layers, layers

"""
def get_exist_images():
    client = docker.from_env()
    exist_images = client.images.list(name=overall_repo) 
    images_list = []   
    for image in exist_images:
        repo = str(image).split(':')[1].split(':')[0].replace("'","").replace(" ","")
        tag = str(image).split(':')[2].replace("'","").replace(" ","").replace(">","")
        if overall_repo == repo:
            name = tag[3:-2] + tag[-1]
            images_list.append(name)
    return images_list
"""
def get_exist_images():
    exist_images = []
    client = docker.from_env()
    images = client.images.list(name=overall_repo)
    #print('exist images')
    for image in images:
        #print(image)
        newstr = str(image).replace("<", "").replace(">","").replace("'","")
        img = newstr.split(' ', 1)[1]
        #print(img)
        if ', ' in img: 
            tmp_imgs = img.split(', ')    
            for tmp_img in tmp_imgs:
                exist_images.append(tmp_img.split(':', -1)[-1].split('-')[1]+tmp_img.split(':', -1)[-1].split('-')[-1])
        else:
            exist_images.append(img.split(':', -1)[-1].split('-')[1]+img.split(':', -1)[-1].split('-')[-1])
        #print(img.split(':', -1)[-1].split('-')[1]+img.split(':', -1)[-1].split('-')[-1])
    return exist_images


def get_running_images(analytics):
    images = []
    client = docker.from_env()
    for container in analytics:
        a = client.containers.get(container)
        newstr = str(a.image).replace("<", "").replace(">","").replace("'","")
        #images.append(newstr.split(' ')[1])
        repo, app, vers = newstr.split(' ')[1].split('-', 2)
        images.append(app+vers)
    return images


def get_containers():
    analytics = []
    cmd = 'docker ps| grep k8s'
    k8s_containers_info = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    lines = k8s_containers_info.split('\n')
    for line in lines[:-1]:
        infos = line.split()
        if 'k8s_audio-recognition' in infos[-1] or 'k8s_object-detection' in infos[-1]:
            analytics.append(infos[0])
    return analytics


def get_unreplace_layers(exist_images_list):
    unreplaced_images = []
    replaced_layer_nums = []
    is_write = False
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'r') as reader:
        for line in reader.readlines():
            # If no replace images, then break
            if line.strip() == '': break
            rep_img, num_layers = line.rstrip().split(',')
            rep_img = rep_img.split(':')[-1]
            #unreplaced_images.append(rep_img[3:-2]+rep_img[-1])
            unreplaced_images.append(rep_img.split('-')[1]+rep_img.split('-')[-1])
            replaced_layer_nums.append(int(num_layers))
    # Remove existed layers
    for img in unreplaced_images:
        if img in exist_images_list:
            del replaced_layer_nums[unreplaced_images.index(img)]
            unreplaced_images.remove(img)
            is_write = True
    # Read the image information json file to get layers' information
    images_dict = {}
    for img in unreplaced_images:
        images_dict[img] = {}
    com_layers = {}
    layers = {}
    for img in images_dict:
        #print('img: ' + img)
        #img_name = 's2-' + img[:-1] + '-' + img[-1]
        if 'yolo' in img:
            img_name = 's2-yolo-' + img.split('yolo')[-1]
        elif 'audio' in img:
            img_name = 's2-audio-' + img.split('audio')[-1]
        if overall_repo in img:
            img_name = img.split(':')[-1]
        #print('overall_repo: ' + overall_repo)
        #print('img_name: ' + img_name)
        parts = []
        with open('/home/minion/YC/iscc19/Implementation/Algo/Download/image_'+img_name+'.json', 'r') as reader:
            reads = reader.read().replace('\n', '').replace(' ', '').split('[{', 1)[1]
            #print('reads: ' + reads)
            parts = reads.split('},{')
            #parts = reader.read().replace('\n', '').replace(' ', '').split('[{', 1)[1].split('},{')
        # max number of existed layers
        max_l_num = len(parts)-replaced_layer_nums[unreplaced_images.index(img)]-1
        #print('img: ' + img)
        #print('max_l_num: ' + str(max_l_num))
        for i in range(0, len(parts)):
            com_size_str = parts[i].split('"CompressLayerSize":"', 1)[1].split('"', 1)[0]
            size = parts[i].split('"LayerSize":"', 1)[1].split('"', 1)[0]
            l_id = parts[i].split('"LayerID":"', 1)[1].split('"')[0]
            if l_id not in com_layers:
                # Convert unit to Byte
                #com_size, unit = com_size_str.split(' ', 1)
                unit = com_size_str[-2:]
                com_size = com_size_str[:-2]
                if unit == 'GB':
                    com_layers[l_id] = float(com_size)*1000*1000*1000
                elif unit == 'MB':
                    com_layers[l_id] = float(com_size)*1000*1000
                elif unit == 'KB':
                    com_layers[l_id] = float(com_size)*1000
                else: # B
                    com_layers[l_id] = float(com_size_str[:-1])
            # layers before max_l_num are existed (1)
            images_dict[img][l_id] = 1 if i <= max_l_num else 0
            #print('l_id: ' + l_id)
            #print('i: ' + str(i))
            #print('images_dict[img][l_id]: ' + str(images_dict[img][l_id]))
            # Bytes
            layers[l_id] = float(size)
    # Write back replacement information 
    # The new information is different from only if the unreplaced images are existed now 
    if is_write:
        with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'w') as writer:
            for image in unreplaced_images:
                #writer.write(overall_repo+':s2-'+image[:-1]+'-'+image[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')
                if 'yolo' in image:
                    writer.write(overall_repo+':s2-yolo-'+image.split('yolo')[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')
                elif 'audio' in image:
                    writer.write(overall_repo+':s2-audio-'+image.split('audio')[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')

    # Debug Message
    #print('Get unreplaced layers information')
    #print('images_dict:', images_dict)
    #print('com_layers:', com_layers)
    #print('layers:', layers)
    #print('keys:', images_dict.keys())
    return images_dict, com_layers, layers 


def get_layer_size(container, layers):
    layer_size = 0
    com_layer_size = 0
    for l in layers:
        #print('l: ' + l)
        #print('layers[l]', layers[l])
        if not layers[l]:
            #print('not layers[l]')
            layer_size += overall_layers[l]
            com_layer_size += overall_com_layers[l]
    container['LAYER'] = layer_size
    container['COMLAYER'] = com_layer_size
    #print("container['COMLAYER']", container['COMLAYER'])


#def dynamic_program(input_analytics, n, total_size, bandwidth, CPU):
#def dynamic_program(input_analytics, n, D, CPU):
def dynamic_program(input_analytics, n, D):
    #size = overall_containers[input_analytics[n]]['LAYER']
    #bw = overall_containers[input_analytics[n]]['COMLAYER']
    size = overall_containers[input_analytics[n]]['COMLAYER']
    #cpu = overall_containers[input_analytics[n]]['CPU']
    value = overall_containers[input_analytics[n]]['BW']

    #print 'n: ', n    
    #print 'total_size: ', total_size
    #print 'size: ', size

    #if total_size <= 0 or bandwidth <= 0 or CPU <= 0 or n < 0:
    #if D <= 0 or CPU <= 0 or n < 0:
    if D <= 0 or n < 0:
        #print('constraintes 0 or n < 0')
        #print([])
        return 0, []
    
    #print 'n-1: ', n-1
    #if (size > total_size) or (bw > bandwidth) or (cpu > CPU):
    #if size > D or cpu > CPU:
    if size > D:
        #print 'constraint not enough'
        #total_value, analytics = dynamic_program(input_analytics, n-1, total_size, bandwidth, CPU)
        #total_value, analytics = dynamic_program(input_analytics, n-1, D, CPU)
        total_value, analytics = dynamic_program(input_analytics, n-1, D)
        #print 'total_value', total_value
        #print 'analytics: ', analytics
        return total_value, analytics
    else:
        #print 'constraint bigger enough'
        #not_includ_value, not_includ_analyts = dynamic_program(input_analytics, n-1, total_size, bandwidth, CPU)
        #not_includ_value, not_includ_analyts = dynamic_program(input_analytics, n-1, D, CPU)
        not_includ_value, not_includ_analyts = dynamic_program(input_analytics, n-1, D)
        #includ_value, includ_analyts = dynamic_program(input_analytics, n-1, total_size-size, bandwidth-bw, CPU-cpu)
        #includ_value, includ_analyts = dynamic_program(input_analytics, n-1, D-size, CPU-cpu)
        includ_value, includ_analyts = dynamic_program(input_analytics, n-1, D-size)
        #print 'not_includ_analyts: ', not_includ_analyts
        #print 'includ_analyts: ', includ_analyts
        
        if not_includ_value >= includ_value+value:
            #print('not_includ_value bigger')
            #print 'analytics: ', not_includ_analyts
            return not_includ_value, not_includ_analyts
        else:
            #print('includ_value bigger')
            includ_analyts.append(input_analytics[n]) 
            #print 'analytics: ', includ_analyts
            return includ_value + value, includ_analyts


#def greedy(input_analytics, total_size, bandwidth, CPU):
#def greedy(input_analytics, D, CPU):
def greedy(input_analytics, D):
    # CP ratio
    ds = []
    for analytic in input_analytics:
        #size = overall_containers[analytic]['LAYER']
        #bw = overall_containers[analytic]['COMLAYER']
        size = overall_containers[analytic]['COMLAYER']
        #cpu = overall_containers[analytic]['CPU']
        value = overall_containers[analytic]['BW']
        #normal = max([size/D, cpu/CPU])
        normal = size/D
        if normal == 0:
            ds.append([analytic, value*D])
        else:
            ds.append([analytic, value/normal])
    # Sort analytics in descending order
    ds = sorted(ds, key=lambda a: a[1], reverse=True)
    analytics = [item[0] for item in ds]
    # Check resources constraints
    download_analytics = []
    for analytic in analytics:
        #print('D: ' + str(D)) 
        #size = overall_containers[analytic]['LAYER']
        #bw = overall_containers[analytic]['COMLAYER']
        size = overall_containers[analytic]['COMLAYER']
        #cpu = overall_containers[analytic]['CPU']
        #if size <= total_size and bw <= bandwidth and cpu <= CPU:
        #if size <= D and cpu <= CPU:
        if size <= D:
            download_analytics.append(analytic)
            #total_size -= size
            #bandwidth -= bw
            D -= size
            #CPU -= cpu
        #elif total_size <= 0 and bandwidth <= 0 and CPU <= 0:
        #elif D <= 0 and CPU <= 0:
        elif D <= 0:
            break
    return download_analytics


def roundoff(input_analytics, alpha):
    global overall_containers
    max_analytic = max(input_analytics, key = lambda a:overall_containers[a]['BW'])
    max_value = overall_containers[max_analytic]['BW']
    k  = (max_value * alpha) / len(input_analytics)
    for analytic in input_analytics:
        value = overall_containers[analytic]['BW']
        overall_containers[analytic]['BW'] = math.floor(value/k)
    

#def download_algo(total_size, bandwidth, CPU, original_analytics, method):
def download_algo(total_size, bandwidth, original_analytics, method, alpha):
    ## ----- Initialization ----- ##
    # storage GB -> B
    #print ('Before total_size: ' + str(total_size))
    total_size *= 1000*1000*1000
    #print ('total_size: ' + str(total_size))
    # bandwidth (Kbps) -> bps, and meltiply time step 10 minutes
    #print ('bandwidth: ' + str(bandwidth))
    bandwidth *= 1000*Duration*60
    #print ('bandwidth: ' + str(bandwidth))
    # Calculate remaining CPU resource
    # Get running image
    #running_images = get_running_images(get_containers())
    #for img in running_images:
    #    CPU -= const_overall_containers[img]['CPU']
    
    global overall_containers
    #overall_containers = copy.deepcopy(const_overall_containers)
    # Get Existed Images
    exist_images_list = get_exist_images()
    #print (exist_images_list)
    exist_images_dict, exist_com_layers_dict, exist_layers_dict = read_image_json(exist_images_list, 1)
    # input images, layers default assume exist
    input_images_dict, input_com_layers_dict, input_layers_dict = read_image_json(original_analytics, 1)
    global overall_layers
    overall_layers = input_layers_dict
    global overall_com_layers
    overall_com_layers = input_com_layers_dict
    # Get Unreplaced layers
    unreplace_images_dict, unreplace_com_layers_dict, unreplace_layers_dict = get_unreplace_layers(exist_images_list)        
    # Check the layers of input images exist or not
    for img in input_images_dict:
        for lay in input_images_dict[img]:
            try:
                #print('img: ' + img)
                #print('lay: ' + lay)
                #print('overall_com_layers[lay]', overall_com_layers[lay])
                #print('exist_com_layers_dict[lay]', exist_com_layers_dict[lay])
                overall_com_layers[lay] = exist_com_layers_dict[lay]
                #print('input_images_dict[img][lay]', input_images_dict[img][lay])
            except:
                input_images_dict[img][lay] = 0
                #print('img: ' + img)
                #print('lay: ' + lay)
                #print('unreplace_images_dict.keys()', unreplace_images_dict.keys())
                if img in unreplace_images_dict.keys():
                    #print('unreplace_images_dict[img][lay]' + str(unreplace_images_dict[img][lay]))
                    #print('input_images_dict[img][lay]' + str(input_images_dict[img][lay]))
                    input_images_dict[img][lay] = unreplace_images_dict[img][lay]    
                    #print('After input_images_dict[img][lay]' + str(input_images_dict[img][lay]))
                else:
                    for image in unreplace_images_dict.keys():
                        if lay in unreplace_images_dict[image].keys():
                            input_images_dict[img][lay] = unreplace_images_dict[image][lay]
    # Get the size of layers which need to be downloaded
    for analytic in original_analytics:
        #print('analytic: ' + analytic)
        #print('overall_containers[analytic]', overall_containers[analytic])
        #print('input_images_dict[analytic]', input_images_dict[analytic])
        get_layer_size(overall_containers[analytic], input_images_dict[analytic]) 
    # Calculate the avallable storage size
    # Firstly, find all existed layers from existed images and unreplace layers
    #overall_using_layers = copy.deepcopy(exist_layers_dict)
    # Here use compressed size to replace size
    overall_using_layers = copy.deepcopy(exist_com_layers_dict)
    #print('overall_using_layers', overall_using_layers)
    for img in unreplace_images_dict:
        #print('unreplace image:', img)
        for lay in unreplace_images_dict[img]:
            #print('unreplace layer:', lay)
            #print('overall_using_layers:', overall_using_layers)
            #print('unreplace_images_dict[img][lay]:', unreplace_images_dict[img][lay])
            if lay not in overall_using_layers.keys() and unreplace_images_dict[img][lay]:
                #print('using unreplace layer:', lay)
                # Here we use compressed size to replace size
                overall_using_layers[lay] = unreplace_com_layers_dict[lay]
    # Sum the size of all the existed layers
    sum_existed_layers_size = 0
    #print('sum overall_using_layers')
    for lay in overall_using_layers:
        #print('lay: ' + lay)
        #print('overall_using_layers[lay]: ' + str(overall_using_layers[lay]))
        sum_existed_layers_size += overall_using_layers[lay]
    #print('sum_existed_layers_size: ' +str(sum_existed_layers_size))
    # Total available size = total size - size of existed layers
    total_size -= sum_existed_layers_size
    #print ('After total_size: ' + str(total_size))
    D = min(total_size, bandwidth)
    #print('D: ' + str(D))

    """ 
    ### ----- Lagrange Need ----- ###
    if method == 'Lagrange':
        # To let the magnitude of cpu is similar to the bandwidth and the size 
        for container in overall_containers:
            overall_containers[container]['CPU'] *= 1000*1000*10    
        #print ('CPU: ' + str(CPU))
        CPU *= 1000*1000*10
        #print ('CPU: ' + str(CPU))
    """    

    # Remove duplicate items and multiply bandwidth
    input_analytics = []
    duplic_analytics = []
    duplicate_num = []
    for analytic in original_analytics:
        """
        ### ----- Lagrange Need ----- ###
        if method == 'Lagrange': 
            add_cpu = overall_containers[analytic]['CPU'] + const_overall_containers[analytic]['CPU']*1000*1000*10
        ### -----  DP Need ----- ###
        else:
            add_cpu = overall_containers[analytic]['CPU'] + const_overall_containers[analytic]['CPU']
        """
        #add_cpu = overall_containers[analytic]['CPU'] + const_overall_containers[analytic]['CPU']

        if analytic not in input_analytics:
            input_analytics.append(analytic)
        #elif analytic not in duplic_analytics and add_cpu <= CPU:
        elif analytic not in duplic_analytics:
            duplic_analytics.append(analytic)
            duplicate_num.append(2)
            overall_containers[analytic]['BW'] += const_overall_containers[analytic]['BW']
            #overall_containers[analytic]['CPU'] = add_cpu
        #elif add_cpu <= CPU:
        #    index = duplic_analytics.index(analytic)
        #    duplicate_num[index] += 1
        #    overall_containers[analytic]['BW'] += const_overall_containers[analytic]['BW']
        #    overall_containers[analytic]['CPU'] = add_cpu
        #else: print('duplicate and over CPU')

    # Reorder items by their ['BW']
    #print('input_analytics')
    #for analytic in input_analytics:
    #    print(analytic)
    # Reorder list
    input_analytics.sort(key=lambda a: overall_containers[a]['BW'], reverse=True)
    #print('reorder_analytics')
    #for analytic in input_analytics:
    #    print(analytic)
            

    # Debug Message
    #print('original_analytics')
    #for analytic in original_analytics:
    #    print(analytic)
            
    #print('input_analytics')
    #for analytic in input_analytics:
    #    print(analytic)
            
    #print('duplic_analytics')
    #for analytic in duplic_analytics:
    #    print(analytic)
            
    #print('duplicate_num')
    #for num in duplicate_num:
    #    print(num)
            
    #print('input_analytics')
    #for analytic in input_analytics:
    #    print(analytic)
            
    #print('overall_containers LAYER')
    #for container in overall_containers:
    #    print(container, overall_containers[container]['LAYER'])
            
    #print('overall_containers COMLAYER')
    #for container in overall_containers:
    #    print(container, overall_containers[container]['COMLAYER'])
            
    #print('overall_containers CPU')
    #for container in overall_containers:
    #    print(container, overall_containers[container]['CPU'])
            
    #print('overall_containers BW')
    #for container in overall_containers:
    #    print(container, overall_containers[container]['BW'])

    """ 
    ### ----- Lagrangian Method ----- ### 
    if method == 'Lagrange':
        local_e_a = lagrange(input_analytics, input_images_dict, total_size, bandwidth, CPU)
        download_analytics = []
        for i in range(len(input_analytics)):
            if local_e_a[i] == 1:
                download_analytics.append(input_analytics[i])
    """
    ### ----- Dynamic Programing Method ----- ###
    if method == 'DP':
        #total_value, download_analytics = dynamic_program(input_analytics, len(input_analytics)-1, total_size, bandwidth, CPU)
        #total_value, download_analytics = dynamic_program(input_analytics, len(input_analytics)-1, D, CPU)
        total_value, download_analytics = dynamic_program(input_analytics, len(input_analytics)-1, D)
    elif method == 'FPTAS':
        roundoff(input_analytics, alpha)
        total_value, download_analytics = dynamic_program(input_analytics, len(input_analytics)-1, D)
    elif method == 'Greedy':
        #download_analytics = greedy(input_analytics, total_size, bandwidth, CPU)
        #download_analytics = greedy(input_analytics, D, CPU)
        download_analytics = greedy(input_analytics, D)
    else: 
        print('Algorithm: ' + method + ' is not a valid algorithm.')
        return []


    # Check the constraints/
    solution_analytics = []
    size_constraint = 0
    #bw_constraint = 0
    #cpu_constraint = 0
    for analytic in download_analytics:
        exceed = False
        multiply = overall_containers[analytic]['BW']/const_overall_containers[analytic]['BW']
        #new_size = size_constraint + overall_containers[analytic]['LAYER']
        #new_bw = bw_constraint + overall_containers[analytic]['COMLAYER']
        new_size = size_constraint + overall_containers[analytic]['COMLAYER']
        #new_cpu = cpu_constraint + overall_containers[analytic]['CPU']
        #if new_size > total_size: continue
        #if new_bw > bandwidth: continue
        if new_size > D: continue
        #if new_cpu > CPU: exceed = True
        if not exceed: 
            solution_analytics.append(analytic)
            size_constraint = new_size
            #bw_constraint = new_bw
            #cpu_constraint = new_cpu
        elif multiply > 1:
            for i in range(multiply):
                """
                ### ----- Lagrange Need ----- ###
                if method == 'Lagrange':
                    new_cpu = cpu_constraint + const_overall_containers[analytic]['CPU']*1000*1000*10
                ### ----- DP Need ----- ###
                else:
                    new_cpu = cpu_constraint + const_overall_containers[analytic]['CPU']
                """
                #new_cpu = cpu_constraint + const_overall_containers[analytic]['CPU']

                #if new_cpu > CPU: continue
                if analytic not in solution_analytics: 
                    solution_analytics.append(analytic)
                    duplicate_num[duplic_analytics.index(analytic)] = 1
                    #cpu_constraint = new_cpu
                else:
                    duplicate_num[duplic_analytics.index(analytic)] += 1
                    #cpu_constraint = new_cpu
            
                
        #print('size_constraint: ' + str(size_constraint))
        #print('bw_constraint: ' + str(bw_constraint))
        #print('cpu_constraint: ' + str(cpu_constraint))
    

    # Insert the original duplicate items
    answer_analytics = []
    for analytic in solution_analytics:
        answer_analytics.append(analytic)
        if analytic in duplic_analytics:
            number = duplicate_num[duplic_analytics.index(analytic)]
            for a in range(number-1):
                answer_analytics.append(analytic)
    
    saved_bandwidth = 0
    for analytic in answer_analytics:
        saved_bandwidth += overall_containers[analytic]['BW'] 
    print "saved bandwidth:",saved_bandwidth
 
    # Debug message
    #print('Download analytics')
    #for analytic in download_analytics:
    #    print(analytic)
    #print('Solution analytics')
    #for analytic in solution_analytics:
    #    print(analytic)
    #print('Answer analytics')
    #for analytic in answer_analytics:
    #    print(analytic)

    return answer_analytics


def is_exist(image):
    client = docker.from_env()
    images = client.images.list(name=overall_repo)
    if image in images:
       return True
    return False

"""
def write_log(edge_analytics):
    name = []
    download_time = []
    access_num = []
    not_exist_num = 0
    f = open("/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_download.log","r")
    for line in f:
        name.append(line.split(",")[0])
        download_time.append(line.split(",")[1])
        access_num.append(int(line.split(",")[2]))
    f.close()

    for analytic in edge_analytics:
        if 'yolo' in analytic: 
            app = 'yolo'
            version = analytic.split('yolo')[-1]
        elif 'audio' in analytic: 
            app='audio'
            version = analytic.split('audio')[-1]
        #app = analytic[:-1]
        #version = analytic[-1]
        analytic_name = overall_repo+":s2-"+app+"-"+version
        index = name.index(analytic_name)
        if is_exist(analytic):
           access_num[index] += 1
        else:
           not_exist_num += 1
           access_num[index] += 1
           download_time[index] = time.time()
        content = name[index]+','+str(download_time[index])+','+str(access_num[index])
        os.popen('sed -i "'+str(index+1)+'c '+content+'" /home/minion/YC/iscc19/Implementation/Algo/Replacement/images_download.log')

    return not_exist_num
"""

def read(filename):
    num = 0
    with open(filename) as f:
         analytics = f.readlines()
    analytics = [item.rstrip().split("-")[0] for item in analytics]
    num = len(analytics)
    return num, analytics

if __name__ == '__main__':

    registry_size = float(sys.argv[1])
    network_bandwidth = int(sys.argv[2])
    analytics_file = sys.argv[3]
    method = sys.argv[4]
    if len(sys.argv) < 6:
        alpha = 0.1
    else:
        alpha = float(sys.argv[5])
 
    start_time = time.time()
    
    #total_CPU = 400
    num, master_analytics = read(analytics_file)
    #decision = download_algo(registry_size, network_bandwidth, total_CPU, master_analytics, method)
    decision = download_algo(registry_size, network_bandwidth, master_analytics, method, alpha)

    edge =  decision
    m_analytics = [a.split('-')[0]  for a in master_analytics]

    for a in edge:
        m_analytics.remove(a)
    cloud = m_analytics
    
    print 'Deploy to cloud>',';'.join(cloud),',Deploy at edge>',';'.join(edge) 

    #if len(edge) > 0:  
    #   delete_num = write_log([edge[0]])

    print('time: ' + str(time.time()-start_time))
