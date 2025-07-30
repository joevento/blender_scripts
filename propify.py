import bpy
import os

# Define the directory where the new folders and .blend files will be saved
output_directory = "D:/AAA_joel_2024/Tietotalo_2024-03-06/K3/alue1/huoneet/props/"

# Ensure the directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get the list of selected objects at the start of the script
selected_objects = [obj for obj in bpy.context.selected_objects]

# Function to gather all children of an object
def get_all_children(obj, include_parent=True):
    objs = []
    if include_parent:
        objs.append(obj)
    for child in obj.children:
        objs.append(child)
        objs.extend(get_all_children(child, include_parent=False))
    return objs

# Function to copy object and its data properly
def copy_object(obj):
    new_obj = obj.copy()
    if obj.data:
        new_obj.data = obj.data.copy()
    return new_obj

# Iterate over the selected objects
for obj in selected_objects:
    # Skip objects that are already children of other objects
    if obj.parent is None:
        # Create a new folder for the object
        object_folder = os.path.join(output_directory, obj.name)
        if not os.path.exists(object_folder):
            os.makedirs(object_folder)
        
        # Create a new scene
        bpy.ops.scene.new(type='NEW')
        new_scene = bpy.context.scene
        
        # Deselect all objects in the new scene
        bpy.ops.object.select_all(action='DESELECT')
        
        # Get the object and all its children
        objs_to_link = get_all_children(obj)
        
        # Dictionary to map old objects to new objects
        old_to_new = {}
        
        # Link the object and its children to the new scene
        for o in objs_to_link:
            new_obj = copy_object(o)
            new_scene.collection.objects.link(new_obj)
            old_to_new[o] = new_obj
        
        # Restore parent-child relationships
        for o in objs_to_link:
            if o.parent is not None:
                old_to_new[o].parent = old_to_new[o.parent]
                old_to_new[o].matrix_parent_inverse = o.matrix_parent_inverse

        # Move the parent object to the origin
        old_to_new[obj].location = (0, 0, 0)
        
        # Set the new scene as the active scene
        bpy.context.window.scene = new_scene
        
        # Create a new .blend file name based on the object's name
        blend_filepath = os.path.join(object_folder, f"{obj.name}.blend")
        
        # Save the current scene as a new .blend file
        bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
        
        # Select all objects in the new scene
        bpy.ops.object.select_all(action='SELECT')
        
        # Export the object as .glb with specified settings
        glb_filepath = os.path.join(object_folder, f"{obj.name}.glb")
        bpy.ops.export_scene.gltf(
            filepath=glb_filepath,
            export_format='GLB',
            use_selection=True,
            export_apply=True,
            export_yup=False
        )
        
        # Deselect all objects before switching back
        bpy.ops.object.select_all(action='DESELECT')
        
        # Delete the new scene after saving and exporting
        bpy.ops.scene.delete()
    
# Optionally, print a message indicating the process is complete
print("Finished saving selected objects and their children to individual .blend files and exporting as .glb files.")
