import bpy
import os
import re
import math

# Function to clean object names by removing .001, .002, etc.
def clean_name(name):
    return re.sub(r'\.\d{3}$', '', name)

# Function to find the root parent of an object
def find_root_parent(obj):
    while obj.parent is not None:
        obj = obj.parent
    return obj

# Create the .items.txt file for the main .blend file in its directory
def create_items_file():
    # Get the path of the main .blend file
    main_blend_path = bpy.data.filepath
    main_blend_dir = os.path.dirname(main_blend_path)
    main_blend_name = os.path.basename(main_blend_path)
    main_blend_base_name = os.path.splitext(main_blend_name)[0]

    # Define the path for the .items.txt file
    items_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}.items.txt")
    
    with open(items_filepath, 'w') as file:
        # Get the "Items" collection
        collection = bpy.data.collections.get("Items")
        if collection:
            for item_obj in collection.objects:
                # Get object data
                name = item_obj.name
                cleaned_name = clean_name(name)
                location = item_obj.location
                rotation = item_obj.rotation_euler
                
                # Convert rotation from radians to degrees
                rotation_deg = (math.degrees(rotation.x), math.degrees(rotation.y), math.degrees(rotation.z))
                
                # Get root parent's name for the 3D file names
                root_parent = find_root_parent(item_obj)
                root_cleaned_name = clean_name(root_parent.name)
                file_name_glb = f"{root_cleaned_name}.glb"
                file_name_usd = f"{root_cleaned_name}.usd"
                
                # Write to file in the format: name, 3d file (glb), 3d file (usd), x, y, z, rotx, roty, rotz
                file.write(f"{name}, {file_name_glb}, {file_name_usd}, {location.x}, {location.y}, {location.z}, {rotation_deg[0]}, {rotation_deg[1]}, {rotation_deg[2]}\n")
    
    print("Finished creating .items.txt file")

# Call the function to create the .items.txt file
create_items_file()
