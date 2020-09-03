
file_names = [
        "s2-yolo-2",
        "s2-yolo-3",
        "s2-yolo-4",
        "s2-yolo-5",
        "s2-audio-1",
        "s2-audio-2",
        "s2-audio-3",
        "s2-audio-4",
        "s2-audio-5"
    ]

#file_names = ["s2-yolo-2"]

for name in file_names:
    # Read file
    in_name = "msg_" + name + ".txt"
    in_file = open(in_name, 'r')
    in_content = in_file.read()
    exist_parts = in_content.split(": Already exists")
    layer_names = []
    # Already existed layers
    for i in range(0, len(exist_parts)-1):
        #print(exist_parts[i])
        length = len(exist_parts[i])
        layer_names.append(exist_parts[i][-12:])
    
    # Pulled layers
    parts = exist_parts[len(exist_parts)-1].split(": Pull complete")
    for i in range(0, len(parts)-1):
        #print(parts[i])
        length = len(parts[i])
        layer_names.append(parts[i][-12:])
    in_file.close()

    # Write file
    out_name = "image_" + name + ".json"
    out_file = open(out_name, 'w')
    # Head
    out_file.write('{\n    "ImageName": "s2-yolo-2",\n    "ImageSize": "1.41 GB",\n    "Layers":\n    [\n')
    out_file.write('        {\n            "LayerID": "' + layer_names[0] + '",\n')
    out_file.write('            "LayerSize": ""\n        }')
    # Layers    
    for i in range(1, len(layer_names)):
        out_file.write(',\n        {\n            "LayerID": "' + layer_names[i] + '",\n')
        out_file.write('            "LayerSize": ""\n        }')
    # End
    out_file.write('\n    ]\n}')    

    out_file.close()
