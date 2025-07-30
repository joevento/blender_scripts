import bpy
import re

# Delete the scene named "Scene"
scene_to_delete = "Scene"
if scene_to_delete in bpy.data.scenes:
    bpy.data.scenes.remove(bpy.data.scenes[scene_to_delete], do_unlink=True)

# Collect all objects in all remaining scenes
remaining_objects = set()
for scene in bpy.data.scenes:
    for obj in scene.objects:
        remaining_objects.add(obj)

# Delete objects not in any remaining scenes
for obj in bpy.data.objects:
    if obj not in remaining_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

# Cleanup unused data blocks
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# Remove .001, .002, etc. from the end of object names
pattern = re.compile(r"\.\d+$")
for obj in bpy.data.objects:
    new_name = pattern.sub("", obj.name)
    obj.name = new_name
