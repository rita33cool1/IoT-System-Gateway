import sys
import docker
import subprocess
import json

image_name = sys.argv[1]

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
layer_ids = []
for l in layers_rootfs:
    p = subprocess.Popen(['sudo', 'grep', '-r', l, '/var/lib/docker/image/overlay2'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    stdout,stderr = p.communicate()
    layer_ids.append(stdout.decode("utf-8").split('distribution/diffid-by-digest/sha256/')[1].split(':sha256')[0])
#print("Layers' sha256 in Registry (ex. Dockerhub)")
#for l in layer_ids:
#    print(l)

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

#print("Layers' sizes (bytes)")
#for l in layers_size:
#    print(l)
#print('Total image size: ' + str(sum_size) + ' bytes')


with open('/home/minion/YC/iscc19/Implementation/Algo/Download/compress_image_'+image_name.split(':')[1]+'.json', 'r') as reader:
    jf = json.loads(reader.read())
    jf['ImageCompressSize'] = jf['ImageSize']
    jf['ImageSize'] = str(sum_size)
    for l in jf['Layers']:
        for l_id in layer_ids:
            if l['LayerID'] == l_id[0:12]:
                l['CompressLayerSize'] = l['LayerSize']
                l['LayerSize'] = str(layers_size[layer_ids.index(l_id)])
with open('/home/minion/YC/iscc19/Implementation/Algo/Download/image_'+image_name.split(':')[1]+'.json', 'w') as writer:
    data = json.dumps(jf, separators=(',', ': '), indent=4)
    writer.write(data)
