import bpy

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    # Check if the object has a mesh data block
    if obj.type == 'MESH':
        # Rename the mesh data block to the name of the object
        obj.data.name = obj.name

print("Renaming completed.")
