#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/02'

import os
import sys
import time
import math
import json
import random
import docker
import warnings
import commands
import paho.mqtt.publish as publish
# list.copy only support since python 3.3 so use this instead
import copy

## parameter
#registry_size = 16 # 16G
#network_bandwidth = 176000 # 176Mbps

overall_com_layers = {}
overall_layers = {}
overall_repo = 'yujungwang/iscc19'


def read_image_json(imgs_list, is_exist):
    images_dict = {}
    for img in imgs_list:
        images_dict[img] = {}

    com_layers = {}
    layers = {}
    for img in images_dict:
        img_name = 's2-' + img[:-1] + '-' + img[-1]
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


def get_exist_images():
    client = docker.from_env()
    exist_images = client.images.list()
    images_list = []
    for image in exist_images:
        repo = str(image).split(':')[1].split(':')[0].replace("'","").replace(" ","")
        tag = str(image).split(':')[2].replace("'","").replace(" ","").replace(">","")
        if overall_repo == repo:
            name = tag[3:-2] + tag[-1]
            images_list.append(name)

    return images_list


def get_unreplace_layers(exist_images_list):
    unreplaced_images = []
    replaced_layer_nums = []
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'r') as reader:
        for line in reader.readlines():
            try: 
                rep_img, num_layers = line.rstrip().split(',')
            except:
                warnings.warn('images_replace.log:\n' + reader.read() +'\nNo images in images_replace.log')
                break
            rep_img = rep_img.split(':')[1]
            unreplaced_images.append(rep_img[3:-2]+rep_img[-1])
            replaced_layer_nums.append(int(num_layers))
    # Remove existed layers
    for img in unreplaced_images:
        if img in exist_images_list:
            del replaced_layer_nums[unreplaced_images.index(img)]
            unreplaced_images.remove(img)
    # Read the image information json file to get layers' information
    images_dict = {}
    for img in unreplaced_images:
        images_dict[img] = {}
    com_layers = {}
    layers = {}
    for img in images_dict:
        img_name = 's2-' + img[:-1] + '-' + img[-1]
        parts = []
        with open('/home/minion/YC/iscc19/Implementation/Algo/Download/image_'+img_name+'.json', 'r') as reader:
            reads = reader.read().replace('\n', '').replace(' ', '').split('[{', 1)[1]
            #print('reads: ' + reads)
            parts = reads.split('},{')
            #parts = reader.read().replace('\n', '').replace(' ', '').split('[{', 1)[1].split('},{')
        # max number of existed layers
        max_l_num = len(parts)-replaced_layer_nums[unreplaced_images.index(img)]-1
        for i in range(0, len(parts)):
            #values = parts[i].split('":"')
            #com_size_str = values[1].split('"', 1)[0]
            #size = values[2].split('"', 1)[0]
            #l_id = values[3].split('"', 1)[0]
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
            # Bytes
            layers[l_id] = float(size)
    # Write back replacement information
    # The new information is different from only if the unreplaced images are existed now
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'w') as writer:
        for image in unreplaced_images:
            writer.write(overall_repo+':s2-'+image[:-1]+'-'+image[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')

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
        if not layers[l]:
            layer_size += overall_layers[l]
            com_layer_size += overall_com_layers[l]
    container['LAYER'] = layer_size
    container['COMLAYER'] = com_layer_size


def get_available_size(total_size):
    #print('Before total size: ' + str(total_size))
    # storage GB -> B
    total_size *= 1000*1000*1000
    # Get Existed Images
    exist_images_list = get_exist_images()
    #print (exist_images_list)
    exist_images_dict, exist_com_layers_dict, exist_layers_dict = read_image_json(exist_images_list, 1)
    # Get Unreplaced layers
    unreplace_images_dict, unreplace_com_layers_dict, unreplace_layers_dict = get_unreplace_layers(exist_images_list)      
    # Calculate the avallable storage size
    # Firstly, find all existed layers from existed images and unreplace layers
    overall_using_layers = copy.deepcopy(exist_layers_dict)
    for img in unreplace_images_dict:
        #print('unreplace image:', img)
        for lay in unreplace_images_dict[img]:
            #print('unreplace layer:', lay)
            #print('overall_using_layers:', overall_using_layers)
            #print('unreplace_images_dict[img][lay]:', unreplace_images_dict[img][lay])
            if lay not in overall_using_layers.keys() and unreplace_images_dict[img][lay]:
                #print('unsing unreplace layer:', lay)
                overall_using_layers[lay] = unreplace_layers_dict[lay]
    # Sum the size of all the existed layers
    sum_existed_layers_size = 0
    for lay in overall_using_layers:
        sum_existed_layers_size += overall_using_layers[lay]
    #print('sum_existed_layers_size: ' +str(sum_existed_layers_size))
    # Total available size = total size - size of existed layers
    total_size -= sum_existed_layers_size
    total_size /= 1000*1000*1000
    #print ('After total_size: ' + str(total_size))
    
    return total_size
    
def get_containers_info():
    analytics = []
    k8s_containers = []
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        newstr = str(container).replace("<", "").replace(">","")
        analytics.append(newstr.split(':')[1].replace(" ",""))

    err, k8s_containers_info = commands.getstatusoutput('docker ps | grep k8s')
    infos = ' '.join(k8s_containers_info.split()).split(' ')
    for i in range(len(infos)):
        if i % 10 == 0:
           k8s_containers.append(infos[i])
           try:
               analytics.remove(infos[i][:-2])
           except:
              # print "cannot remove "+infos[i]
              pass
    return analytics

def get_analytics(containers):
    analytics = []
    client = docker.from_env()
    for container in containers:
        a = client.containers.get(container)
        image = str(a.image).split(':')[1].replace("'","").replace(" ","")
        tag = str(a.image).split(':')[2].replace("'","").replace(">","")

        analytics.append(image+":"+tag)
    return analytics

def get_cost(analytics):
    costs = {}
    yolo = {"yolo1":{"CPU":105.2,"RAM":13.08,"SIZE":2.15,"BW":150},
    "yolo2":{"CPU":105.2,"RAM":13.08,"SIZE":2.83,"BW":150},
    "yolo3":{"CPU":105.2,"RAM":13.08,"SIZE":3.28,"BW":150},
    "yolo4":{"CPU":105.2,"RAM":13.08,"SIZE":3.58,"BW":150},
    "yolo5":{"CPU":105.2,"RAM":13.08,"SIZE":3.93,"BW":150}
}
    audio = {"audio1":{"CPU":99.51,"RAM":7.84,"SIZE":1.94,"BW":3260},
    "audio2":{"CPU":99.51,"RAM":7.84,"SIZE":2.36,"BW":3260},
    "audio3":{"CPU":99.51,"RAM":7.84,"SIZE":3.02,"BW":3260},
    "audio4":{"CPU":99.51,"RAM":7.84,"SIZE":3.31,"BW":3260},
    "audio5":{"CPU":99.51,"RAM":7.84,"SIZE":3.67,"BW":3260},
}
    costs.update(yolo)
    costs.update(audio)

    return costs


def download_algo(total_size, bandwidth, analytics_cost, input_analytics):
    da = {}
    max_cpu = 400 # x
    max_ram = 100 # y
    #max_sz = total_size 
    max_sz = get_available_size(total_size)

    analytics = []


    if input_analytics == []:

       return []

    #return input_analytics[0]
    audio_analytics = [a.split('-')[0] for a in input_analytics if 'audio' in a]  
    yolo_analytics = [a.split('-')[0] for a in input_analytics if 'yolo' in a]
    
    while True:
          num = len(audio_analytics)
          if num > 0:
             i = random.randint(0,num-1)
             if max_sz - analytics_cost[audio_analytics[i]]['SIZE'] >= 0:
                analytics.append(audio_analytics[i])
                max_sz -= analytics_cost[audio_analytics[i]]['SIZE']
                del audio_analytics[i]
             else:
                del audio_analytics[i]
          else:
             break

    while True:
          num = len(yolo_analytics)
          if num > 0:
             i = random.randint(0,num-1)
             if max_sz - analytics_cost[yolo_analytics[i]]['SIZE'] >= 0:
                analytics.append(yolo_analytics[i])
                max_sz -= analytics_cost[yolo_analytics[i]]['SIZE']
                del yolo_analytics[i]
             else:
                del yolo_analytics[i]
          else:
             break
    return analytics

def is_exist(image):
    client = docker.from_env()
    images = client.images.list()
    if image in images:
       return True
    return False

def write_log(edge_analytics):
    name = []
    download_time = []
    access_num = []
    not_exist_num = 0
    f = open("YC/iscc19/Implementation/Algo/Replacement/images_download.log","r")
    for line in f:
        name.append(line.split(",")[0])
        download_time.append(line.split(",")[1])
        access_num.append(int(line.split(",")[2]))
    f.close()

    for analytic in edge_analytics:
        app = analytic[:-1]
        version = analytic[-1]
        analytic_name = "yujungwang/iscc19:s2-"+app+"-"+version
        index = name.index(analytic_name)
        if is_exist(analytic):
           access_num[index] += 1
        else:
           not_exist_num += 1
           access_num[index] += 1
           download_time[index] = time.time()
        content = name[index]+','+str(download_time[index])+','+str(access_num[index])
        os.popen('sed -i "'+str(index+1)+'c '+content+'" YC/iscc19/Implementation/Algo/Replacement/images_download.log')

    return not_exist_num

def read(filename):
    num = 0
    with open(filename) as f:
         analytics = f.readlines()
    analytics = [item.rstrip().split("-")[0] for item in analytics]
    num = len(analytics)
    return num, analytics

if __name__ == '__main__':

    #epsilon = float(sys.argv[1])
    registry_size = float(sys.argv[1])
    network_bandwidth = int(sys.argv[2])
    analytics_file = sys.argv[3]

    start_time = time.time()

    num, master_analytics = read(analytics_file)
     
    #containers = get_containers_info()
    #print '== continers:  ==\n', containers
    #analytics = get_analytics(containers)
    #print '== analytics:  ==\n' , analytics+master_analytics
    analytics_cost = get_cost(master_analytics) 
    #print '== cost of each analytics: ==\n', analytics_cost

    decision = download_algo(registry_size, network_bandwidth, analytics_cost, master_analytics)
    #decision = download_algo(registry_size, network_bandwidth, analytics_cost, epsilon, master_analytics)
    #decision = download_algo(registry_size, network_bandwidth, analytics_cost, layers, epsilon)
    edge =  decision
    m_analytics = [a.split('-')[0]  for a in master_analytics]

    for a in edge:
        m_analytics.remove(a)

    cloud = m_analytics
    #cloud = map(lambda s:s.strip(), list(set(m_analytics) - set(edge)))
    #cloud ,edge= test_algo(master_analytics, registry_size, analytics_cost)
    
    print 'Deploy to cloud>',';'.join(cloud),',Deploy at edge>',';'.join(edge) 

    if len(edge) > 0:  
       delete_num = write_log([edge[0]])

    print('time: ' + str(time.time()-start_time))
