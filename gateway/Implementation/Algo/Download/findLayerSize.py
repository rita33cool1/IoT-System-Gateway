import sys
import docker
import subprocess

# Replace "overlay2" by other file system if your docker use other file system such as "aufs"

image_name = sys.argv[1]

# Layers in RootFS
client = docker.from_env()
image = client.images.get(image_name)
layers_rootfs = []
for l in image.attrs['RootFS']['Layers']:
    layers_rootfs.append(l.split('sha256:')[1].rstrip())
print("Layers' sha256 in [RootFS]")
for l in layers_rootfs:
    print(l)

# Layer ids
layer_ids = []
for l in layers_rootfs:
    p = subprocess.Popen(['sudo', 'grep', '-r', l, '/var/lib/docker/image/overlay2'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    stdout,stderr = p.communicate()
    layer_ids.append(stdout.decode("utf-8").split('distribution/diffid-by-digest/sha256/')[1].split(':sha256')[0])
print("Layers' sha256 in Registry (ex. Dockerhub)")
for l in layer_ids:
    print(l)

# Diff-id
layer_files = []
for l in layers_rootfs:
    p = subprocess.Popen(['sudo', 'grep', '-r', l, '/var/lib/docker/image/overlay2'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    stdout,stderr = p.communicate()
    layer_files.append(stdout.decode("utf-8").split('/diff:')[0].split('layerdb/sha256/')[-1])
print("Layers' file name stored in layerdb")
for l in layer_files:
    print(l)

# Layer sizes
layers_size = []
sum_size = 0
for l in layer_files:
    file_name = '/var/lib/docker/image/overlay2/layerdb/sha256/'+l+'/size'
    p = subprocess.Popen(['sudo', 'cat', file_name],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    stdout,stderr = p.communicate()
    layers_size.append(stdout.decode("utf-8"))
    sum_size += int(stdout.decode("utf-8"))

# Print progressive layers size in reverse order
layers_size.reverse()
progressive_size = 0
print("Layers' progressive sizes (bytes)")
layer_size_dict = "{'max':"+str(len(layers_size))
for i in range(len(layers_size)):
    progressive_size += int(layers_size[i])
    layer_size_dict = layer_size_dict + ", '" + str(i+1) + "':" + str(progressive_size)
layer_size_dict = layer_size_dict + "}"
print(layer_size_dict)
 
print('Total image size: ' + str(sum_size) + ' bytes')
print('Total image size: ' + str(float(sum_size)/1024/1024/1024) + ' GB')

