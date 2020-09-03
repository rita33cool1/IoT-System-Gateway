#!/bin/bash

date_time=$(date +"%m%d_%H%M")
algorithm=$(cat YC/iscc19/Algorithm.txt)
cd YC/iscc19/Implementation/Gateway/PubImages
echo "goto PubImages"
#file=./Implementation/Gateway/PubImages/original/$algorithm
#if [ -d $file ]; then
#    rm -r $file
#fi
python3 DownResPubImages.py original/"$algorithm"
echo "PubImage"
