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


overall_images = {'yolo1':{}, 'yolo2':{}, 'yolo3':{}, 'yolo4':{},'yolo5':{}, 
          'audio1':{}, 'audio2':{}, 'audio3':{}, 'audio4':{}, 'audio5':{}}

const_overall_containers = { 
    "yolo1":{"CPU":55.6,"RAM":13.08,"SIZE":1.81,"BW":150, "COMLAYER":0, "LAYER":0},
    "yolo2":{"CPU":55.6,"RAM":13.08,"SIZE":2.25,"BW":150, "COMLAYER":0, "LAYER":0},
    "yolo3":{"CPU":55.6,"RAM":13.08,"SIZE":2.61,"BW":150, "COMLAYER":0, "LAYER":0},
    "yolo4":{"CPU":55.6,"RAM":13.08,"SIZE":2.96,"BW":150, "COMLAYER":0, "LAYER":0},
    "yolo5":{"CPU":55.6,"RAM":13.08,"SIZE":3.6,"BW":150, "COMLAYER":0, "LAYER":0},
    "audio1":{"CPU":51.3,"RAM":7.84,"SIZE":2.03,"BW":3260, "COMLAYER":0, "LAYER":0},
    "audio2":{"CPU":51.3,"RAM":7.84,"SIZE":2.49,"BW":3260, "COMLAYER":0, "LAYER":0},
    "audio3":{"CPU":51.3,"RAM":7.84,"SIZE":2.85,"BW":3260, "COMLAYER":0, "LAYER":0},
    "audio4":{"CPU":51.3,"RAM":7.84,"SIZE":3.13,"BW":3260, "COMLAYER":0, "LAYER":0},
    "audio5":{"CPU":51.3,"RAM":7.84,"SIZE":3.48,"BW":3260, "COMLAYER":0, "LAYER":0}
}

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
        img_name = 's2-' + img[:-1] + '-' + img[-1]
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
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'r') as reader:
        for line in reader.readlines():
            # If no replace images, then break
            if line.strip() == '': break
            rep_img, num_layers = line.rstrip().split(',')
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


def dynamic_program(input_analytics, n, total_size, bandwidth, CPU):
    size = overall_containers[input_analytics[n]]['LAYER']
    bw = overall_containers[input_analytics[n]]['COMLAYER']
    cpu = overall_containers[input_analytics[n]]['CPU']
    value = overall_containers[input_analytics[n]]['BW']

    #print 'n: ', n    
    #print 'total_size: ', total_size
    #print 'size: ', size

    if total_size <= 0 or bandwidth <= 0 or CPU <= 0 or n < 0:
        #print('constraintes 0 or n < 0')
        #print([])
        return 0, []
    
    #print 'n-1: ', n-1
    if (size > total_size) or (bw > bandwidth) or (cpu > CPU):
        #print 'constraint not enough'
        total_value, analytics = dynamic_program(input_analytics, n-1, total_size, bandwidth, CPU)
        #print 'total_value', total_value
        #print 'analytics: ', analytics
        return total_value, analytics
    else:
        #print 'constraint bigger enough'
        not_includ_value, not_includ_analyts = dynamic_program(input_analytics, n-1, total_size, bandwidth, CPU)
        includ_value, includ_analyts = dynamic_program(input_analytics, n-1, total_size-size, bandwidth-bw, CPU-cpu)
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

 
def subproblem(container, lambda_s, lambda_b, lambda_c):
    object_function = container['BW']*1000
    sum_constraints = container['LAYER'] + container['COMLAYER'] + container['CPU']
    relaxed_constraints = lambda_s*container['LAYER'] + lambda_b*container['COMLAYER'] + lambda_c*container['CPU']
    
    if object_function - relaxed_constraints > 0:
        return 1, relaxed_constraints, object_function-relaxed_constraints
    else: return 0, 0, 0
 

def lagrange(input_analytics, input_images_dict, total_size, bandwidth, CPU):
    # Initialize parameters
    t = 0
    lambda_s = 0.1
    lambda_b = 0.1
    lambda_c = 0.1
    # time_step 
    #alpha = 0.0000000000001
    alpha = 0.0000000000001
    # relaxed constraints
    sum_relaxtion = 0
    # stop criteria
    stop_range = 100000
    # total value
    total_value = stop_range + 1
    min_value = 0
    min_local_e_a = []
    min_t = 0

    ## ----- Compute Dual Decomposition ----- ##
    old_lambda_s = 0
    old_lambda_b = 0
    old_lambda_c = 0
    old_value = total_value
    first_t = True 
    while (old_value - total_value) >= 0 and (lambda_s > 0 or lambda_b > 0 or lambda_c > 0):
        # relaxed constraints
        sum_constraints = 0
        sum_value = 0
        # object variables
        local_e_a = []
        # Compute decomposed subproblems
        for analytic in input_analytics:
            e_a, sum_const, value = subproblem(overall_containers[analytic], lambda_s, lambda_b, lambda_c)
            local_e_a.append(e_a)
            sum_constraints += sum_const
            sum_value += value 
            #print('sum_const', sum_const) 
        # Update lambdas
        old_lambda_s = lambda_s
        old_lambda_b = lambda_b
        old_lambda_c = lambda_c
        lambda_s = lambda_s - alpha * (total_size-sum_constraints)
        if lambda_s < 0: lambda_s = 0
        lambda_b = lambda_b - alpha * (bandwidth-sum_constraints)
        if lambda_b < 0: lambda_b = 0
        lambda_c = lambda_c - alpha * (CPU-sum_constraints)
        if lambda_c < 0: lambda_c = 0
        #print('sum_constraints', sum_constraints)
        #print(old_lambda_s)
        #print(old_lambda_b)
        #print(old_lambda_c)
        # compute total value
        old_value = total_value
        total_value = sum_value + old_lambda_s*total_size + old_lambda_b*bandwidth + old_lambda_c*CPU
        if first_t:
            old_value = total_value
            first_t = False 
        #print('iteration: ', t)
        #print('sum_value: ', sum_value)
        #print ('total_value: ', total_value)
        if t == 0:
            min_value = total_value
            min_local_e_a = local_e_a
            min_t = t
        elif total_value < min_value: 
            min_value = total_value
            min_local_e_a = local_e_a
            min_t = t
        t += 1

    # Debug Message
    #print ('min_t: ' + str(min_t))
    #print ('min_value: ' + str(min_value))
    
    return min_local_e_a


def download_algo(total_size, bandwidth, CPU, original_analytics, method):
    ## ----- Initialization ----- ##
    # storage GB -> B
    #print ('Before total_size: ' + str(total_size))
    total_size *= 1000*1000*1000
    #print ('total_size: ' + str(total_size))
    # bandwidth (Kbps) -> bps, and meltiply time step 10 minutes
    #print ('bandwidth: ' + str(bandwidth))
    bandwidth *= 1000*10*60
    #print ('bandwidth: ' + str(bandwidth))
    # Calculate remaining CPU resource
    # Get running image
    running_images = get_running_images(get_containers())
    for img in running_images:
        CPU -= const_overall_containers[img]['CPU']
    
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
                overall_com_layers[lay] = exist_com_layers_dict[lay]
            except:
                input_images_dict[img][lay] = 0
                if img in unreplace_images_dict.keys():
                    input_images_dict[img][lay] = unreplace_images_dict[img][lay]    
    # Get the size of layers which need to be downloaded
    for analytic in original_analytics:
        get_layer_size(overall_containers[analytic], input_images_dict[analytic]) 
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
    #print ('After total_size: ' + str(total_size))

    
    ### ----- Lagrange Need ----- ###
    if method == 'Lagrange':
        # To let the magnitude of cpu is similar to the bandwidth and the size 
        for container in overall_containers:
            overall_containers[container]['CPU'] *= 1000*1000*10    
        #print ('CPU: ' + str(CPU))
        CPU *= 1000*1000*10
        #print ('CPU: ' + str(CPU))
 
    # Remove duplicate items and multiply bandwidth
    input_analytics = []
    duplic_analytics = []
    duplicate_num = []
    for analytic in original_analytics:
        ### ----- Lagrange Need ----- ###
        if method == 'Lagrange': 
            add_cpu = overall_containers[analytic]['CPU'] + const_overall_containers[analytic]['CPU']*1000*1000*10
        ### -----  DP Need ----- ###
        else:
            add_cpu = overall_containers[analytic]['CPU'] + const_overall_containers[analytic]['CPU']

        if analytic not in input_analytics:
            input_analytics.append(analytic)
        elif analytic not in duplic_analytics and add_cpu <= CPU:
            duplic_analytics.append(analytic)
            duplicate_num.append(2)
            overall_containers[analytic]['BW'] += const_overall_containers[analytic]['BW']
            overall_containers[analytic]['CPU'] = add_cpu
        elif add_cpu <= CPU:
            index = duplic_analytics.index(analytic)
            duplicate_num[index] += 1
            overall_containers[analytic]['BW'] += const_overall_containers[analytic]['BW']
            overall_containers[analytic]['CPU'] = add_cpu
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

    
    ### ----- Lagrangian Method ----- ### 
    if method == 'Lagrange':
        local_e_a = lagrange(input_analytics, input_images_dict, total_size, bandwidth, CPU)
        download_analytics = []
        for i in range(len(input_analytics)):
            if local_e_a[i] == 1:
                download_analytics.append(input_analytics[i])
    ### ----- Dynamic Programing Method ----- ###
    elif method == 'DP':
        total_value, download_analytics = dynamic_program(input_analytics, len(input_analytics)-1, total_size, bandwidth, CPU)
    elif method == 'Greedy':
        print('Greedy')
    else: 
        print('Algorithm: ' + method + ' is not the valid algorithm.')
        return []


    # Check the constraints/
    solution_analytics = []
    size_constraint = 0
    bw_constraint = 0
    cpu_constraint = 0
    for analytic in download_analytics:
        exceed = False
        multiply = overall_containers[analytic]['BW']/const_overall_containers[analytic]['BW']
        new_size = size_constraint + overall_containers[analytic]['LAYER']
        new_bw = bw_constraint + overall_containers[analytic]['COMLAYER']
        new_cpu = cpu_constraint + overall_containers[analytic]['CPU']
        if new_size > total_size: continue
        if new_bw > bandwidth: continue
        if new_cpu > CPU: exceed = True
        if not exceed: 
            solution_analytics.append(analytic)
            size_constraint = new_size
            bw_constraint = new_bw
            cpu_constraint = new_cpu
        elif multiply > 1:
            for i in range(multiply):
                ### ----- Lagrange Need ----- ###
                if method == 'Lagrange':
                    new_cpu = cpu_constraint + const_overall_containers[analytic]['CPU']*1000*1000*10
                ### ----- DP Need ----- ###
                else:
                    new_cpu = cpu_constraint + const_overall_containers[analytic]['CPU']

                if new_cpu > CPU: continue
                if analytic not in solution_analytics: 
                    solution_analytics.append(analytic)
                    duplicate_num[duplic_analytics.index(analytic)] = 1
                    cpu_constraint = new_cpu
                else:
                    duplicate_num[duplic_analytics.index(analytic)] += 1
                    cpu_constraint = new_cpu
            
                
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
    images = client.images.list()
    if image in images:
       return True
    return False

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
        app = analytic[:-1]
        version = analytic[-1]
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
 
    start_time = time.time()
    
    total_CPU = 400
    num, master_analytics = read(analytics_file)
    decision = download_algo(registry_size, network_bandwidth, total_CPU, master_analytics, method)

    edge =  decision
    m_analytics = [a.split('-')[0]  for a in master_analytics]

    for a in edge:
        m_analytics.remove(a)
    cloud = m_analytics
    
    print 'Deploy to cloud>',';'.join(cloud),',Deploy at edge>',';'.join(edge) 

    if len(edge) > 0:  
       delete_num = write_log([edge[0]])

    print('time: ' + str(time.time()-start_time))
