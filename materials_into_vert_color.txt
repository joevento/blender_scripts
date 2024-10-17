import bpy

obj = bpy.context.active_object
if obj.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

if not obj.data.color_attributes:
    obj.data.color_attributes.new(name="Col", domain='CORNER', type='FLOAT_COLOR')

bpy.context.object.data.color_attributes.active = obj.data.color_attributes["Col"]

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.bake_type = 'DIFFUSE'
bpy.context.scene.cycles.samples = 1
bpy.context.scene.render.bake.target = 'VERTEX_COLORS'
bpy.context.scene.render.bake.use_selected_to_active = False
bpy.context.scene.render.bake.use_clear = True

for material_index, material_slot in enumerate(obj.material_slots):
    obj.active_material_index = material_index
    obj.active_material = material_slot.material
    bpy.ops.object.bake(type='DIFFUSE')

print("Baking materials to active color attribute completed successfully.")
