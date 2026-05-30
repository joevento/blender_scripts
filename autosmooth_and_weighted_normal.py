import bpy
import math

# Configuration
SMOOTHING_ANGLE_DEGREES = 50.0
WEIGHTED_NORMAL_WEIGHT = 100
KEEP_SHARP = True

def setup_mesh_modifiers():
    smooth_angle_rad = math.radians(SMOOTHING_ANGLE_DEGREES)

    original_active = bpy.context.view_layer.objects.active
    original_selected = bpy.context.selected_objects[:]

    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']

    for obj in mesh_objects:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        smooth_mod = None
        for mod in obj.modifiers:
            if mod.type == 'NODES' and "Smooth by Angle" in mod.name:
                smooth_mod = mod
                break
        
        if not smooth_mod:
            bpy.ops.object.shade_auto_smooth(angle=smooth_angle_rad)
            for mod in obj.modifiers:
                if mod.type == 'NODES' and "Smooth by Angle" in mod.name:
                    smooth_mod = mod
                    break
        else:
            if smooth_mod.node_group:
                for prop in smooth_mod.keys():
                    if ("Socket" in prop or "Input" in prop) and isinstance(smooth_mod[prop], float):
                        smooth_mod[prop] = smooth_angle_rad
                        break

        if smooth_mod:
            smooth_mod.use_pin_to_last = False

        weighted_mod = next((m for m in obj.modifiers if m.type == 'WEIGHTED_NORMAL'), None)
        if not weighted_mod:
            weighted_mod = obj.modifiers.new(name="Weighted Normal", type='WEIGHTED_NORMAL')
            weighted_mod.keep_sharp = KEEP_SHARP
            weighted_mod.weight = WEIGHTED_NORMAL_WEIGHT
        else:
            weighted_mod.keep_sharp = KEEP_SHARP
            weighted_mod.weight = WEIGHTED_NORMAL_WEIGHT

        if smooth_mod and weighted_mod:
            smooth_idx = obj.modifiers.find(smooth_mod.name)
            weighted_idx = obj.modifiers.find(weighted_mod.name)

            if smooth_idx > weighted_idx:
                obj.modifiers.move(smooth_idx, weighted_idx)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in original_selected:
        try:
            obj.select_set(True)
        except:
            pass
    bpy.context.view_layer.objects.active = original_active

if __name__ == "__main__":
    setup_mesh_modifiers()

