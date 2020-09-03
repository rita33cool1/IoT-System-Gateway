#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'YuJung Wang'
__date__ = '2020/06'

import sys 
import docker
import subprocess

if __name__ == '__main__':
    image_name = sys.argv[1]
    tag_name = sys.argv[2]
    out_name = f'image_{tag_name}.json'

    # Layers in RootFS
    client = docker.from_env()
    image = client.images.get(image_name)
    layers_rootfs = []
    for l in image.attrs['RootFS']['Layers']:
        layers_rootfs.append(l.split('sha256:')[1].rstrip())
    #print("Layers' sha256 in [RootFS]")
    #for l in layers_rootfs:
    #    print(l)

    # Layer ids
    # Replace "overlay2" by other file system
    # if your docker use other file system such as "aufs"  
    layer_ids = []
    for l in layers_rootfs:
        p = subprocess.Popen(['sudo', 'grep', '-r', l, '/var/lib/docker/image/overlay2'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        stdout,stderr = p.communicate()
        layer_ids.append(stdout.decode("utf-8").split('distribution/diffid-by-digest/sha256/')[1].split(':sha256')[0])
    print("Layers' sha256 in Registry (ex. Dockerhub)")
    for l in layer_ids:
        print(l[:12])

    # Diff-id
    layer_files = []
    for l in layers_rootfs:
        p = subprocess.Popen(['sudo', 'grep', '-r', l, '/var/lib/docker/image/overlay2'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        stdout,stderr = p.communicate()
        layer_files.append(stdout.decode("utf-8").split('/diff:')[0].split('layerdb/sha256/')[-1])
    #print("Layers' file name stored in layerdb")
    #for l in layer_files:
    #    print(l)

    # Layer sizes
    layers_size = []
    sum_size = 0
    for l in layer_files:
        file_name = '/var/lib/docker/image/overlay2/layerdb/sha256/'+l+'/size'
        p = subprocess.Popen(['sudo', 'cat', file_name],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        stdout,stderr = p.communicate()
        layers_size.append(stdout.decode("utf-8"))
        sum_size += int(stdout.decode("utf-8"))


    # Write file
    out_file = open(out_name, 'w')
    # Head
    out_file.write(f'{{\n    "Layers": [\n')
    # Layers    
    for i in range(len(layers_size)-1):
        out_file.write(f'        {{\n            "CompressLayerSize": "",\n')
        out_file.write(f'            "LayerSize": "{layers_size[i]}",\n')
        out_file.write(f'            "LayerID": "{layer_ids[i][:12]}"\n        }},\n')
    out_file.write(f'        {{\n            "CompressLayerSize": "",\n')
    out_file.write(f'            "LayerSize": "{layers_size[-1]}",\n')
    out_file.write(f'            "LayerID": "{layer_ids[-1][:12]}"\n        }}\n')
    
    # End
    out_file.write(f'    ],\n    "ImageName": "{tag_name}",\n')    
    out_file.write(f'    "ImageSize": "{sum_size}",\n')    
    out_file.write(f'    "ImageCompressSize": ""\n}}')    
    out_file.close()
