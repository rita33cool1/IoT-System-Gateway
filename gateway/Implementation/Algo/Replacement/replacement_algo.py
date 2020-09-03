#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/04'

import os
import sys
import json
import copy
import time
import docker
import random
import subprocess

#overall_repo = 'yujungwang/iscc19'
overall_repo = os.environ['DOCKER_PROVIDER'] + '/' + os.environ['DOCKER_REPO']

im1 = overall_repo + ":s2-audio-1"
im2 = overall_repo + ":s2-audio-2"
im3 = overall_repo + ":s2-audio-3"
im4 = overall_repo + ":s2-audio-4"
im5 = overall_repo + ":s2-audio-5"
im6 = overall_repo + ":s2-audio-6"
im7 = overall_repo + ":s2-audio-7"
im8 = overall_repo + ":s2-audio-8"
im9 = overall_repo + ":s2-audio-9"
im10 = overall_repo + ":s2-audio-10"
im11 = overall_repo + ":s2-audio-11"
im12 = overall_repo + ":s2-audio-12"
im13 = overall_repo + ":s2-yolo-1"
im14 = overall_repo + ":s2-yolo-2"
im15 = overall_repo + ":s2-yolo-3"
im16 = overall_repo + ":s2-yolo-4"
im17 = overall_repo + ":s2-yolo-5"
im18 = overall_repo + ":s2-yolo-6"
im19 = overall_repo + ":s2-yolo-7"
im20 = overall_repo + ":s2-yolo-8"
im21 = overall_repo + ":s2-yolo-9"
im22 = overall_repo + ":s2-yolo-10"
im23 = overall_repo + ":s2-yolo-11"
im24 = overall_repo + ":s2-yolo-12"
#im5 = overall_repo + ":s2-audio-5"
#im10 = overall_repo + ":s2-yolo-5"

# Audio: 1-5, Yolo: 6-10
#"im5": {'max':24}
#"im10": {'max':22}
layers = {
    "im1": {'max':21}, "im2": {'max':22}, "im3": {'max':23}, "im4": {'max':24},
    "im5": {'max':19}, "im6": {'max':20}, "im7": {'max':19}, "im8": {'max':20},
    "im9": {'max':19}, "im10": {'max':20}, "im11": {'max':19}, "im12": {'max':20},        
    "im13": {'max':19}, "im14": {'max':21}, "im15": {'max':21}, "im16": {'max':22}, 
    "im17": {'max':16}, "im18": {'max':16}, "im19": {'max':16}, "im20": {'max':16},
    "im21": {'max':16}, "im22": {'max':16}, "im23": {'max':16}, "im24": {'max':16}
}
"""
layers = {}
# Audio
l= {"im1": {'max':21, '1':6079, '2':59604121, '3':192622442, '4':192622442, '5':224526626, '6':224927808, '7':231758631, '8':233209203, '9':492710201, '10':493187754, '11':1223903049, '12':1235941075, '13':1246100175, '14':1253593582, '15':1259647974, '16':1303490375, '17':1320370062, '18':1643412709, '19':1766682440, '20':1808151687, '21':1937224007}}
layers.update(l)
l= {"im2": {'max':22, '1':6079, '2':58025147, '3':412963334, '4':545981655, '5':545981655, '6':551323134, '7':551724316, '8':558555139, '9':560005711, '10':823141536, '11':823610078, '12':1555692026, '13':1648989999, '14':1659149099, '15':1665212599, '16':1665212631, '17':1725163120, '18':1742042807, '19':2065085454, '20':2188355185, '21':2229824432, '22':2358896752}}
layers.update(l)
l= {"im3": {'max':23, '1':6080, '2':57119574, '3':880842540, '4':1013860861, '5':1013860861, '6':1020390492, '7':1020791949, '8':1027622772, '9':1029073344, '10':1292288532, '11':1292802374, '12':2017062763, '13':2091782818, '14':2108180085, '15':2115672200, '16':2121726804, '17':2169555153, '18':2186414163, '19':2748602029, '20':2890384908, '21':2898197294, '22':2921428855, '23':3022023085}}
layers.update(l)
l= {"im4": {'max':24, '1':6080, '2':57366901, '3':333501848, '4':1157224814, '5':1290243135, '6':1290243135, '7':1296772900, '8':1297174357, '9':1304005180, '10':1305455752, '11':1567270389, '12':1567732207, '13':2297254122, '14':2371974335, '15':2388371602, '16':2394435314, '17':2394435346, '18':2459772971, '19':2476631981, '20':3038819847, '21':3180602726, '22':3188415112, '23':3211646673, '24':3312240903}}
layers.update(l)
l= {"im5": {'max':24, '1':6080, '2':58030930, '3':881753896, '4':1514770345, '5':1647788666, '6':1647788666, '7':1654318431, '8':1654719888, '9':1661550711, '10':1663001283, '11':1926137117, '12':1926605660, '13':2658203695, '14':2733415275, '15':2749812542, '16':2755876254, '17':2755876286, '18':2819763470, '19':2836622480, '20':3398810346, '21':3540593225, '22':3548405611, '23':3571637172, '24':3672231402}}
layers.update(l)
# Yolo
l= {"im6": {'max':19, '1':4891, '2':710107, '3':368124564, '4':368124564, '5':604566207, '6':604566207, '7':706363170, '8':706840723, '9':1437556031, '10':1449594052, '11':1459753152, '12':1467246559, '13':1473300951, '14':1517143352, '15':1534023039, '16':1857065686, '17':1980335417, '18':2021804664, '19':2150876984}}
layers.update(l)
l= {"im7": {'max':21, '1':4915, '2':690954, '3':355629141, '4':723043598, '5':723043598, '6':983980779, '7':983980779, '8':1085771903, '9':1086233735, '10':1805565746, '11':1880288088, '12':1896685355, '13':1902749067, '14':1902749099, '15':1973156886, '16':1990140806, '17':2552328672, '18':2694111551, '19':2701923937, '20':2725155498, '21':2825749728}}
layers.update(l)
l= {"im8": {'max':21, '1':4915, '2':710152, '3':824433118, '4':1191847575, '5':1191847575, '6':1452792883, '7':1452792883, '8':1554589846, '9':1555067398, '10':2285792390, '11':2347755814, '12':2364153081, '13':2371645196, '14':2377699800, '15':2425528149, '16':2442387159, '17':3004575025, '18':3146357904, '19':3154170290, '20':3177401851, '21':3277996081}}
layers.update(l)
l= {"im9": {'max':22, '1':4915, '2':696700, '3':276831647, '4':1100554613, '5':1467969070, '6':1467969070, '7':1728904113, '8':1728904113, '9':1830694730, '10':1831156548, '11':2560678459, '12':2635398667, '13':2651795934, '14':2657859646, '15':2657859678, '16':2723197303, '17':2740056313, '18':3302244179, '19':3444027058, '20':3451839444, '21':3475071005, '22':3575665235}}
layers.update(l)
l= {"im10": {'max':22, '1':4915, '2':697186, '3':633713635, '4':1457436601, '5':1824851058, '6':1824851058, '7':2085786103, '8':2085786103, '9':2187576746, '10':2188045290, '11':2919643324, '12':2994854899, '13':3011252166, '14':3017315878, '15':3017315910, '16':3081203094, '17':3098062104, '18':3660249970, '19':3802032849, '20':3809845235, '21':3833076796, '22':3933671026}}
layers.update(l)
"""

#overall_com_layers = {}
#overall_layers = {}


def read_image_json(imgs_list, is_exist):
    # Read the image information json file to get layers' information
    images_dict = {}
    for img in imgs_list:
        #images_dict[overall_repo+':s2-'+img[:-1]+'-'+img[-1]] = {}
        if 'yolo' in img:
            images_dict[overall_repo+':s2-yolo-'+img.split('yolo')[-1]] = {}
        elif 'audio' in img:
            images_dict[overall_repo+':s2-audio-'+img.split('audio')[-1]] = {}
    com_layers = {}
    layers = {}
    images_layers_list = []
    images_list = []
    for img in images_dict:
        layers_list = []
        #print('img:', img)
        img_name = img.split(':', -1)[-1]
        #print('img_name:', img_name)
        parts = []
        with open('/home/minion/YC/iscc19/Implementation/Algo/Download/image_'+img_name+'.json', 'r') as reader:
            parts = reader.read().replace('\n', '').replace(' ', '').split('[{', 1)[1].split('},{')
        for i in range(0, len(parts)):
            com_size_str = parts[i].split('"CompressLayerSize":"', 1)[1].split('"', 1)[0]
            size = parts[i].split('"LayerSize":"', 1)[1].split('"', 1)[0]
            l_id = parts[i].split('"LayerID":"', 1)[1].split('"')[0]
            layers_list.append(l_id)
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
            images_dict[img][l_id] = is_exist
            # Bytes
            layers[l_id] = float(size)
        #images_list.append(overall_repo+':s2-'+img[:-1]+'-'+img[-1])
        images_list.append(img)
        layers_list.reverse()
        #print('layers_list:', layers_list)
        images_layers_list.append(layers_list)

    return images_dict, com_layers, layers, images_list, images_layers_list


def get_allimages_abbr():
    abbrs = []
    all_images = get_allimages()
    for image in all_images:
        abbrs.append(image.split(':', -1)[-1].split('-')[1]+image.split(':', -1)[-1].split('-')[-1])
    return abbrs


def get_unreplace_layers(exist_images_list):
    unreplaced_images = []
    replaced_layer_nums = []
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
    # Read the image information json file to get layers' information
    images_dict = {}
    for img in unreplaced_images:
        images_dict[img] = {}
    com_layers = {}
    layers = {}
    images_layers_list = []
    images_list = []
    for img in images_dict:
        layers_list = []
        #img_name = 's2-' + img[:-1] + '-' + img[-1]
        if 'yolo' in img:
            img_name = 's2-yolo-' + img.split('yolo')[-1]
        elif 'audio' in img:
            img_name = 's2-audio-' + img.split('audio')[-1]
        parts = []
        with open('/home/minion/YC/iscc19/Implementation/Algo/Download/image_'+img_name+'.json', 'r') as reader:
            parts = reader.read().replace('\n', '').replace(' ', '').split('[{', 1)[1].split('},{')
        # max number of existed layers
        max_l_num = len(parts)-replaced_layer_nums[unreplaced_images.index(img)]-1
        for i in range(0, len(parts)):
            com_size_str = parts[i].split('"CompressLayerSize":"', 1)[1].split('"', 1)[0]
            size = parts[i].split('"LayerSize":"', 1)[1].split('"', 1)[0]
            l_id = parts[i].split('"LayerID":"', 1)[1].split('"')[0]
            layers_list.append(l_id)
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
        if 'yolo' in img:
            images_list.append(overall_repo+':s2-yolo-'+img.split('yolo')[-1])
        elif 'audio' in img:
            images_list.append(overall_repo+':s2-audio-'+img.split('audio')[-1])
        layers_list.reverse()
        #print('layers_list:', layers_list)
        images_layers_list.append(layers_list)
    # Write back replacement information
    # The new information is different from only if the unreplaced images are existed now
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'w') as writer:
        for image in unreplaced_images:
            #writer.write(overall_repo+':s2-'+image[:-1]+'-'+image[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')
            if 'yolo' in image:
                writer.write(overall_repo+':s2-yolo-'+image.split('yolo')[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')
            elif 'audio' in image:
                writer.write(overall_repo+':s2-audio-'+image.split('audio')[-1]+','+str(replaced_layer_nums[unreplaced_images.index(image)])+'\n')

    return images_dict, com_layers, layers, images_list, images_layers_list


def get_available_size(total_size):
    #print('Before total size: ' + str(total_size))
    ## storage GB -> B# Here using compressed layer size to replace layer size
    #total_size *= 1000*1000*1000
    # Get Existed Images
    exist_images_list = get_allimages_abbr()
    #print (exist_images_list)
    exist_images_dict, exist_com_layers_dict, exist_layers_dict, exist_images_list, exist_layers_list = read_image_json(exist_images_list, 1)
    # Get Unreplaced layers
    unreplace_images_dict, unreplace_com_layers_dict, unreplace_layers_dict, unreplace_images_list, unreplace_layers_list = get_unreplace_layers(exist_images_list)
    # Calculate the avaliable storage size
    # Firstly, find all existed layers from existed images and unreplace layers
    #overall_using_layers = copy.deepcopy(exist_layers_dict)
    # Here using compressed layer size to replace layer size 
    overall_using_layers = copy.deepcopy(exist_com_layers_dict)
    for img in unreplace_images_dict:
        #print('unreplace image:', img)
        for lay in unreplace_images_dict[img]:
            #print('unreplace layer:', lay)
            #print('overall_using_layers:', overall_using_layers)
            #print('unreplace_images_dict[img][lay]:', unreplace_images_dict[img][lay])
            if lay not in overall_using_layers.keys() and unreplace_images_dict[img][lay]:
                #print('unsing unreplace layer:', lay)
                # Here using compressed layer size to replace layer size
                #overall_using_layers[lay] = unreplace_layers_dict[lay]
                overall_using_layers[lay] = unreplace_com_layers_dict[lay]
    # Sum the size of all the existed layers
    sum_existed_layers_size = 0
    for lay in overall_using_layers:
        sum_existed_layers_size += overall_using_layers[lay]
    print('Storage usage: ' +str(sum_existed_layers_size))
    # Total available size = total size - size of existed layers
    total_size -= sum_existed_layers_size
    #total_size /= 1000*1000*1000
    #print ('After total_size: ' + str(total_size))
    '''
    long_exist_images_list = []
    for image in exist_images_list:
        long_image = image
        if 'yolo' in image:
            long_image = overall_repo+':'+'s2-yolo-'+image.split('yolo')[-1]
        elif 'audio' in image:
            long_image = overall_repo+':'+'s2-audio-'+image.split('audio')[-1]
        long_exist_images_list.append(long_image)
    '''
    #return total_size, exist_images_dict, exist_layers_dict, exist_images_list, exist_layers_list, unreplace_images_dict, unreplace_layers_dict, unreplace_images_list, unreplace_layers_list
    # Here using compressed layer size to replace layer size
    return total_size, exist_images_dict, exist_com_layers_dict, exist_images_list, exist_layers_list, unreplace_images_dict, unreplace_com_layers_dict, unreplace_images_list, unreplace_layers_list


def imID(images_name):
    if images_name == im1:
       return "im1"
    elif images_name == im2:
       return "im2"
    elif images_name == im3:
       return "im3"
    elif images_name == im3:
       return "im3"
    elif images_name == im4:
       return "im4"
    elif images_name == im5:
       return "im5"
    elif images_name == im6:
       return "im6"
    elif images_name == im7:
       return "im7"
    elif images_name == im8:
       return "im8"
    elif images_name == im9:
       return "im9"
    elif images_name == im10:
       return "im10"
    elif images_name == im11:
       return "im11"
    elif images_name == im12:
       return "im12"
    elif images_name == im13:
       return "im13"
    elif images_name == im14:
       return "im14"
    elif images_name == im15:
       return "im15"
    elif images_name == im16:
       return "im16"
    elif images_name == im17:
       return "im17"
    elif images_name == im18:
       return "im18"
    elif images_name == im19:
       return "im19"
    elif images_name == im20:
       return "im20"
    elif images_name == im21:
       return "im21"
    elif images_name == im22:
       return "im22"
    elif images_name == im23:
       return "im23"
    elif images_name == im24:
       return "im24"

def get_layers(images):
    layers = []
    client = docker.from_env()
    for image in images:
        a = client.images.get(image) 
        image_info = a.attrs
        if 'RootFS' in image_info:
            layer_info = image_info['RootFS']
            if 'Layers' in layer_info:
                layer = layer_info['Layers']
        for tmp in layer:
            if tmp not in layers:
               layers.append(tmp)

    return layers

def get_images(analytics):
    #print('get_images')
    images = []
    client = docker.from_env()
    for container in analytics:
        a = client.containers.get(container)
        #print(str(a.image))
        #newstr = str(a.image).replace("<", "").replace(">","").replace("'","")
        #images.append(newstr.split(' ')[1])
        #print(a.image)
        newstr = str(a.image).replace("<", "").replace(">","").replace("'","")
        img = newstr.split(' ', 1)[1]
        #print(img)
        if ', ' in img: 
            tmp_imgs = img.split(', ')        
            for tmp_img in tmp_imgs:
                if tmp_img not in images: 
                    images.append(tmp_img)
        elif img not in images:
            images.append(img)
    return images

def get_analytics():
    analytics = []
    cmd = 'docker ps| grep k8s'
    k8s_containers_info = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    lines = k8s_containers_info.split('\n')
    for line in lines[:-1]:
        infos = line.split()
        if 'k8s_audio-recognition' in infos[-1] or 'k8s_object-detection' in infos[-1]:
            analytics.append(infos[0])
    return analytics

def get_allimages():
    exist_images = []
    client = docker.from_env()
    images = client.images.list(name=overall_repo)
    for image in images:
        #print(image)
        newstr = str(image).replace("<", "").replace(">","").replace("'","")
        #exist_images.append(newstr.split(' ')[1])
        img = newstr.split(' ', 1)[1]
        if ', ' in img: 
            tmp_imgs = img.split(', ')        
            for tmp_img in tmp_imgs:
                if tmp_img not in exist_images:
                    exist_images.append(tmp_img)
        elif img not in exist_images:
            exist_images.append(img)
    return exist_images

def read_log(log_file, candidate_layers):

    layers = []
    download_times = []
    num_access = []

    with open(log_file) as f:
        lines = f.readlines()
        print('line in images_download.log:')
        for line in lines:
            layer_id = line.split(',')[0]
            if layer_id in candidate_layers:
                layers.append(layer_id)
                print(line)
                download_times.append(float(line.split(',')[1]))
                num_access.append(int(line.split(',')[2]))

    return layers, num_access, download_times

"""
def get_exist_images():
    client = docker.from_env()
    exist_images = client.images.list(name=overall_repo)
    images_list = []
    for image in exist_images:
        repo = str(image).split(':')[1].split(':')[0].replace("'","").replace(" ","")
        tag = str(image).split(':')[2].replace("'","").replace(" ","").replace(">","")
        if overall_repo == repo:
            #name = tag[3:-2] + tag[-1]
            images_list.append(overall_repo+':'+tag)
    return images_list
"""

def get_number_times_layers(exist_images_dict, unreplace_images_dict):
    num_using_layers = {}
    for img in exist_images_dict:
        for lay in exist_images_dict[img]:
            if lay not in num_using_layers.keys():
                num_using_layers[lay] = 1
            else:
                num_using_layers[lay] += 1
    for img in unreplace_images_dict:
        for lay in unreplace_images_dict[img]:
            if lay not in num_using_layers.keys() and unreplace_images_dict[img][lay]:
                num_using_layers[lay] = 1
            elif lay in num_using_layers.keys():
                num_using_layers[lay] += unreplace_images_dict[img][lay]
    
    return num_using_layers


def replacement_algo(total_size, high_level, low_level, image_layers, policy):
    # storage GB -> B
    total_size *= 1000*1000*1000
    high_level_sz = high_level*total_size
    replacement_sz = (1-low_level)*total_size
    # Flags to indicate the image is replaced image or not
    is_replaces = []
    # Survey the replaced images
    replaced_images = []
    replaced_layer_nums = []
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'r') as reader:
        for line in reader.readlines():
            # No replace images
            if line.strip() == '': break
            rep_img, num_layers = line.rstrip().split(',')
            replaced_images.append(rep_img)
            replaced_layer_nums.append(int(num_layers))
    # Get the existed images now
    exist_images = get_allimages()
    print('Before replaced_images:', replaced_images)
    print('Before replaced_layer_nums:', replaced_layer_nums)
    # If the image is exited now, remove the replacemant information
    for image in replaced_images:
        if image in exist_images:
            del replaced_layer_nums[replaced_images.index(image)]    
            replaced_images.remove(image)
    print('exist_images:', exist_images)
    print('After replaced_images:', replaced_images)
    print('After replaced_layer_nums:', replaced_layer_nums)
    # Get the total size and existed images, unreplaced images
    print('Before replacement_sz: ' + str(replacement_sz))
    #available_size, exist_images_dict, exist_layers_dict, exist_images_list, exist_layers_list, unreplace_images_dict, unreplace_layers_dict, unreplace_images_list, unreplace_layers_list = get_available_size(total_size)
    # Here using compressed layer size to replace layer size
    available_size, exist_images_dict, exist_com_layers_dict, exist_images_list, exist_layers_list, unreplace_images_dict, unreplace_com_layers_dict, unreplace_images_list, unreplace_layers_list = get_available_size(total_size)
    print('Available size: ' + str(available_size))
    replacement_sz = replacement_sz - available_size
    print('After replacement_sz: ' + str(replacement_sz))

    # Check wheather occupation rate is higher than high water mark or not
    # If occupation rate is lower than high water mark, do nothing
    print('total_size: ' + str(total_size))
    print('high_level_sz: ' + str(high_level_sz))
    if total_size-available_size < high_level_sz:
        return [], [], []

    # Get running image
    running_images = get_images(get_analytics())

    # Get the times of each layer is used
    num_times_layers = get_number_times_layers(exist_images_dict, unreplace_images_dict)

    replacement_layers = []
    replacement_images = []
    layers_num = len(image_layers)
    tmp_sz = 0

    if replacement_sz > 0:
        # Existed images include invisible replaced images
        print('Before image_layers:', image_layers)
        image_layers = image_layers + replaced_images
        print('image_layers + replaced_images:', image_layers)
        # Exclude running images
        image_layers = [l for l in image_layers if not l in running_images]
        print('running_images:', running_images)
        print('image_layers exclude running_images:', image_layers)
        # Get image using information
        images, num_access_time, download_time = read_log("/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_download.log", image_layers)
        print('get images from download log:', images) 
        print('get num_access_time from download log:', num_access_time) 
        print('get download_time from download log:', download_time) 
        while tmp_sz < int(replacement_sz) and len(images) > 0:
            print('images:', images)
            print('num_access_time:', num_access_time)
            print('download_time: ', download_time)
            print('policy: ' + policy)
            # FIFO doesn't work
            if policy == 'FIFO':
                index = download_time.index(min(download_time))
            elif policy == 'LRU':
                index = download_time.index(min(download_time))
            elif policy == 'MRU':
                index = download_time.index(max(download_time))
            elif policy == 'LFU':
                index = num_access_time.index(min(num_access_time))
            elif policy == 'MFU':
                index = num_access_time.index(max(num_access_time))
            print('index: ' + str(index))
            replacement_images.append(images[index])
            app_name = imID(images[index])
            layer_num = layers[app_name]['max']
            print(images[index])
            # Check the image is replaced images or not
            print('unreplace_images_list:', unreplace_images_list)
            print('replaced_images:', replaced_images)
            if images[index] in replaced_images:
                is_replace = True
                print('image in replaced_images')
                start_num = replaced_layer_nums[replaced_images.index(images[index])]
                unreplace_image_index = unreplace_images_list.index(images[index])
                print('unreplace_layers_list:', unreplace_layers_list)
                end_num = len(unreplace_layers_list[unreplace_image_index])
                for i in range(start_num, end_num):
                    replace_layer = unreplace_layers_list[unreplace_image_index][i]
                    #print('replace_layer:', replace_layer)
                    #print('Before num_times_layers:', num_times_layers[replace_layer])
                    num_times_layers[replace_layer] -= 1
                    #print('After num_times_layers:', num_times_layers[replace_layer])
                    # Only when no images using this layer, the layer could be exactly deleted
                    if num_times_layers[replace_layer] == 0: 
                        #replacement_sz -= unreplace_layers_dict[replace_layer]
                        #print('Subtract unreplace layer size:', unreplace_layers_dict[replace_layer])
                        # Here using compressed layer size to replace layer size
                        replacement_sz -= unreplace_com_layers_dict[replace_layer]
                        print('Subtract unreplace compressed layer size:', unreplace_com_layers_dict[replace_layer])
                    if replacement_sz <= 0: 
                        replacement_layers.append(str(i+1)) 
                        is_replaces.append(True)
                        break
                    # Last layer
                    elif i == end_num - 1:
                        replacement_layers.append(str(i+1)) 
                        is_replaces.append(True)
            else:
                progressive_size = 0
                #print('exist_images_list', exist_images_list)
                exist_image_index = exist_images_list.index(images[index])
                layer_num = len(exist_layers_list[exist_image_index])
                for i in range(layer_num):
                    exist_layer = exist_layers_list[exist_image_index][i]
                    #print('exist_layer:', exist_layer)
                    #print('Before num_times_layers:', num_times_layers[exist_layer])
                    num_times_layers[exist_layer] -= 1
                    #print('After num_times_layers:', num_times_layers[exist_layer])
                    # Only when no images using this layer, the layer could be exactly deleted
                    if num_times_layers[exist_layer] == 0:
                        #replacement_sz -= exist_layers_dict[exist_layer]
                        #print('Subtract exist layer size:', exist_layers_dict[exist_layer])
                        # Here using compressed layer size to replace layer size
                        replacement_sz -= exist_com_layers_dict[exist_layer]
                        print('Subtract exist layer size:', exist_com_layers_dict[exist_layer])
                    if replacement_sz <= 0: 
                        replacement_layers.append(str(i+1)) 
                        is_replaces.append(False)
                        break
                    # Last layer
                    elif i == layer_num - 1:
                        replacement_layers.append(str(i+1)) 
                        is_replaces.append(False)

            del images[index]
            del download_time[index]
            del num_access_time[index]
    

    # save the replacement information in images_replace.log
    # If the replace image has replaced before, modify the before information
    #print('replacement_images:', replacement_images)
    #print('replacement_layers:', replacement_layers)
    for image in replacement_images:
        delete_number = replacement_layers[replacement_images.index(image)]
        if image in replaced_images:
            unreplace_image_index = unreplace_images_list.index(image)
            max_num = len(unreplace_layers_list[unreplace_image_index])
            replace_index = replaced_images.index(image)
            # If the delete number more than the number of layers, no need to record
            if int(delete_number) < max_num:
                replaced_layer_nums[replace_index] = delete_number
            else:
                del replaced_layer_nums[replace_index]
                replaced_images.remove(image)
        else:
            app_name = imID(image)
            layer_num = layers[app_name]['max']
            # If the delete number more than the number of layers, no need to record
            if int(delete_number) < layer_num:
                replaced_images.append(image)
                replaced_layer_nums.append(delete_number)
    with open('/home/minion/YC/iscc19/Implementation/Algo/Replacement/images_replace.log', 'w') as writer:
        for image in replaced_images:
            writer.write(image+','+str(replaced_layer_nums[replaced_images.index(image)])+'\n')
    # Debug
    #print('replacement_images:', replacement_images)
    #print('replacement_layers:', replacement_layers)
    #print('replaced_images:', replaced_images)
    #print('replaced_layer_nums:', replaced_layer_nums)

    return replacement_images, replacement_layers, is_replaces

if __name__ == '__main__':
    total_sz = float(sys.argv[1])
    high_level = float(sys.argv[2])
    low_level = float(sys.argv[3])
    policy = sys.argv[4]

    start_time = time.time()

    analytics = get_analytics()
    images = get_allimages()

    #candidate_layers = get_layers(images)
    # num, layer that can delete, policy
    images, layers, is_replaces = replacement_algo(total_sz, high_level, low_level, images, policy)
    #images, layers = replacement_algo(replacement_sz, images, policy)
    #print(layers)
    print(images, layers)
    #for image, layer in zip(images, layers):
    for image, layer, is_replace in zip(images, layers, is_replaces):
        running_images = get_images(get_analytics())
        print('Replacing image: ' + image)
        print('Check running_images', running_images)
        if image in running_images:
            print('After lrp, ' + image + 'is running now. Cannot remove it')
            continue
        cmd = 'docker ps -a | grep Exit | cut -d " " -f 1 | xargs  docker rm'
        subprocess.run(cmd, shell=True)
        cmd = f'sed -i "1c {layer}" /home/minion/YC/YC-docker-engine/delete_layer_num'  
        #cmd = f'sed -i "1c {layer}" YC/YC-docker-engine/delete_layer_num'  
        subprocess.run(cmd, shell=True)
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
        # If image is the replaced image, the image should pull before delete
        if is_replace:
            cmd = f'docker pull {image}'
            #output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
            try:
                subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        print('time: ' + str(time.time()-start_time))
        cmd = f'docker rmi {image}'
        #output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        try:
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            #raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        #else:
        #    print('Successfully Remove layers in image: ' + image)

    print('time: ' + str(time.time()-start_time))
