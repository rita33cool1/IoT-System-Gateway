#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
__author__ = 'YuJung Wang'
__date__ = '2020/05'

import os
import copy
import docker

#overall_repo = 'yujungwang/iscc19'
overall_repo = os.environ['DOCKER_PROVIDER'] + '/' + os.environ['DOCKER_REPO']


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
        images_list.append(overall_repo+':s2-'+img[:-1]+'-'+img[-1])
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


#def get_available_size(total_size):
def get_available_size():
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


def get_allimages():
    exist_images = []
    client = docker.from_env()
    images = client.images.list(name=overall_repo)
    for image in images:
        #print(image)
        newstr = str(image).replace("<", "").replace(">","").replace("'","")
        #exist_images.append(newstr.split(' ')[1])
        #print(newstr.split(' ')[1])
        img = newstr.split(' ', 1)[1]
        if ', ' in img: 
            tmp_imgs = img.split(', ')            
            for tmp_img in tmp_imgs:
                exist_images.append(tmp_img)
        else:
            exist_images.append(img)
    return exist_images


def measure_storage():
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
    #print('exist_images:', exist_images)
    # Get the total size and existed images, unreplaced images
    # Here using compressed layer size to replace layer size
    get_available_size()



if __name__ == '__main__':
    measure_storage()
