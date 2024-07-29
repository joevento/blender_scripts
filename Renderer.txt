import bpy
import mathutils
import math
import os

# Create a new camera object
def create_camera():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Add a new camera
    bpy.ops.object.camera_add()
    camera = bpy.context.object

    return camera

# Calculate the bounding box center and dimensions of all objects
def calculate_scene_bounds():
    min_coords = mathutils.Vector((float('inf'), float('inf'), float('inf')))
    max_coords = mathutils.Vector((float('-inf'), float('-inf'), float('-inf')))

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for vertex in obj.bound_box:
                vertex_world = obj.matrix_world @ mathutils.Vector(vertex)
                min_coords = mathutils.Vector((min(min_coords[i], vertex_world[i]) for i in range(3)))
                max_coords = mathutils.Vector((max(max_coords[i], vertex_world[i]) for i in range(3)))

    center = (min_coords + max_coords) / 2
    dimensions = max_coords - min_coords

    return center, dimensions

# Position the camera to see all objects
def position_camera(camera, center, dimensions):
    max_dim = max(dimensions)

    # Move the camera back further to ensure all vertices are visible
    camera.location = center + mathutils.Vector((0, -max_dim * 4, max_dim * 2))
    camera.data.clip_end = max_dim * 10

    # Add an empty object at the center for the camera to track to
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
    empty = bpy.context.object

    # Add Track To constraint
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    # Parent the camera to the empty
    camera.parent = empty

    # Rotate the empty 45 degrees around the Z axis
    empty.rotation_euler[2] = math.radians(45)

    # Ensure the camera is selected to see the results in the viewport
    bpy.context.view_layer.objects.active = camera
    camera.select_set(True)

    # Set this camera as the scene camera
    bpy.context.scene.camera = camera

# Set render settings
def set_render_settings():
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 1024

    # Enable transparent film
    bpy.context.scene.render.film_transparent = True

# Add HDRI to the scene
def add_hdri(hdri_path):
        new_world = bpy.data.worlds.new("NewWorld")
        bpy.context.scene.world = new_world
        new_world.use_nodes = True
        tree = new_world.node_tree
        links = tree.links
        for node in tree.nodes:
            tree.nodes.remove(node)
        hdri_node = tree.nodes.new(type='ShaderNodeTexEnvironment')
        hdri_node.image = bpy.data.images.load(hdri_path)
        hdri_node.location = -300, 0
        bg_node = tree.nodes.new(type='ShaderNodeBackground')
        bg_node.location = 0, 0
        output_node = tree.nodes.new(type='ShaderNodeOutputWorld')
        output_node.location = 300, 0
        links.new(hdri_node.outputs['Color'], bg_node.inputs['Color'])
        links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# Render the scene
def render_scene():
    # Get the current .blend file path
    blend_file_path = bpy.data.filepath
    blend_dir = os.path.dirname(blend_file_path)
    blend_filename = os.path.basename(blend_file_path)
    render_filename = os.path.splitext(blend_filename)[0] + '.png'

    # Set the output path
    bpy.context.scene.render.filepath = os.path.join(blend_dir, render_filename)

    # Render the image
    bpy.ops.render.render(write_still=True)

# Main function
def main():
    camera = create_camera()
    center, dimensions = calculate_scene_bounds()
    position_camera(camera, center, dimensions)
    set_render_settings()
    add_hdri('D:/AAA_joel_2024/downloads/kloofendal_43d_clear_puresky_4k.exr')
    render_scene()

# Execute the script
main()
