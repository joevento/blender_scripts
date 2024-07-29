import bpy

active_obj = bpy.context.active_object
selected_objs = bpy.context.selected_objects

for obj in selected_objs:
    if obj != active_obj:
        # Calculate relative coordinates
        relative_coords = active_obj.location - obj.location
        print(f"{relative_coords}")
