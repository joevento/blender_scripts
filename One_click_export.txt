import bpy
import os
import re
import time
import mathutils
import math

st = time.process_time()
print(st)

# Get the path of the main .blend file
main_blend_path = bpy.data.filepath
main_blend_dir = os.path.dirname(main_blend_path)
main_blend_name = os.path.basename(main_blend_path)
main_blend_base_name = os.path.splitext(main_blend_name)[0]

# Define the output directory as "props" within the main .blend file's directory
output_directory = os.path.join(main_blend_dir, "props")

# After getting the path of the main .blend file
main_glb_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}.glb")
main_usd_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}.usd")

# Function to export a scene as .usd
def export_usd(filepath):
    bpy.ops.wm.usd_export(
        filepath=filepath,
        selected_objects_only=False,
        visible_objects_only=False,
        export_animation=False,
        export_hair=False,
        export_vertices=True,
        export_vertex_groups=False,
        export_uvmaps=True,
        export_mesh_colors=True,
        export_normals=True,
        export_mesh_attributes=True,
        export_transforms=True,
        export_materials=True,
        export_meshes=True,
        export_lights=True,
        export_cameras=True,
        export_curves=True,
        export_particles=True,
        export_subdivision='BEST_MATCH',
        export_armatures=True,
        only_deform_bones=False,
        export_shapekeys=True,
        use_instancing=False,
        evaluation_mode='VIEWPORT',
        default_prim_path="/root",
        root_prim_path="/root",
        material_prim_path="/root/materials",
        generate_cycles_shaders=False,
        generate_preview_surface=True,
        generate_mdl=True,
        convert_uv_to_st=True,
        convert_orientation=False,
        export_global_forward_selection='NEGATIVE_Z',
        export_global_up_selection='Y',
        convert_to_cm=False,
        forward_axis='-Z',
        up_axis='Y',
        export_child_particles=False,
        export_as_overs=False,
        merge_transform_and_shape=False,
        export_custom_properties=True,
        add_properties_namespace=True,
        export_identity_transforms=True,
        apply_subdiv=True,
        author_blender_name=True,
        vertex_data_as_face_varying=False,
        frame_step=1,
        override_shutter=False,
        shutter_open=-0.25,
        shutter_close=0.25,
        init_scene_frame_range=False,
        export_textures=True,
        overwrite_textures=False,
        use_original_paths=False,
        light_intensity_scale=1,
        convert_light_to_nits=True,
        scale_light_radius=True,
        convert_world_material=True,
        xform_op_mode='SRT',
        relative_paths=True,
        usdz_downscale_size='KEEP',
        usdz_downscale_custom_size=128,
        usdz_is_arkit=False,
        export_blender_metadata=True,
        triangulate_meshes=False,
        quad_method='SHORTEST_DIAGONAL',
        ngon_method='BEAUTY',
        export_usd_kind=True,
        default_prim_kind='NONE',
        default_prim_custom_kind=""
    )

# Export the main scene as .glb
bpy.ops.export_scene.gltf(
    filepath=main_glb_filepath,
    export_format='GLB',
    use_selection=False,
    export_apply=True,
    export_yup=False
)

# Export the main scene as .usd
export_usd(filepath=main_usd_filepath)

# Render the main scene
def render_scene(blend_file_path):
    # Create a new camera object
    def create_camera():
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.camera_add()
        return bpy.context.object

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
        camera.location = center + mathutils.Vector((0, -max_dim * 4, max_dim * 2))
        camera.data.clip_end = max_dim * 10
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
        empty = bpy.context.object
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        camera.parent = empty
        empty.rotation_euler[2] = math.radians(45)
        bpy.context.view_layer.objects.active = camera
        camera.select_set(True)
        bpy.context.scene.camera = camera

    # Set render settings
    def set_render_settings():
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.samples = 1024
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
        blend_dir = os.path.dirname(blend_file_path)
        blend_filename = os.path.basename(blend_file_path)
        render_filename = os.path.splitext(blend_filename)[0] + '.png'
        bpy.context.scene.render.filepath = os.path.join(blend_dir, render_filename)
        bpy.ops.render.render(write_still=True)

    # Main function to render the scene
    def main_render():
        camera = create_camera()
        center, dimensions = calculate_scene_bounds()
        position_camera(camera, center, dimensions)
        set_render_settings()
        add_hdri('D:/AAA_joel_2024/downloads/kloofendal_43d_clear_puresky_4k.exr')
        render_scene()

    # Execute the render function
    main_render()

render_scene(main_blend_path)

# Ensure the directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

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

# Function to clean object names by removing .001, .002, etc.
def clean_name(name):
    return re.sub(r'\.\d{3}$', '', name)

# Function to gather objects from a specific collection
def gather_objects_from_collection(collection_name):
    collection = bpy.data.collections.get(collection_name)
    if collection:
        return [obj for obj in collection.objects]
    return []

# Function to find the root parent of an object
def find_root_parent(obj):
    while obj.parent is not None:
        obj = obj.parent
    return obj

# Function to create and export a scene
def create_and_export_scene(scene_name, objects, blend_filename, glb_filename, usd_filename, move_to_origin=False):
    bpy.ops.scene.new(type='NEW')
    new_scene = bpy.context.scene
    new_scene.name = scene_name
    bpy.ops.object.select_all(action='DESELECT')

    # Dictionary to map old objects to new objects
    old_to_new = {}

    for obj in objects:
        new_obj = copy_object(obj)
        new_scene.collection.objects.link(new_obj)
        old_to_new[obj] = new_obj

    # Restore parent-child relationships
    for obj in objects:
        if obj.parent is not None:
            old_to_new[obj].parent = old_to_new[obj.parent]
            old_to_new[obj].matrix_parent_inverse = obj.matrix_parent_inverse

    if move_to_origin:
        # Move the parent objects to the origin
        for obj in old_to_new.values():
            if obj.parent is None:
                obj.location = (0, 0, 0)

    bpy.context.window.scene = new_scene
    bpy.ops.wm.save_as_mainfile(filepath=blend_filename)

    # Select all objects in the new scene
    bpy.ops.object.select_all(action='SELECT')

    # Export the scene as .glb with specified settings
    bpy.ops.export_scene.gltf(
        filepath=glb_filename,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=False
    )

    # Export the scene as .usd
    export_usd(filepath=usd_filename)

    # Render the scene
    render_scene(blend_filename)

    # Deselect all objects before switching back
    bpy.ops.object.select_all(action='DESELECT')

    # Delete the new scene after saving and exporting
    bpy.ops.scene.delete()

# Get the list of objects in the "Items" collection
items_objects = gather_objects_from_collection("Items")

# Get the list of objects in the "Static" collection
static_objects = gather_objects_from_collection("Static")

# Create and export the static scene
static_blend_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}_empty.blend")
static_glb_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}_empty.glb")
static_usd_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}_empty.usd")
create_and_export_scene(f"{main_blend_base_name}_empty", static_objects, static_blend_filepath, static_glb_filepath, static_usd_filepath, move_to_origin=False)

# Filter items_objects to exclude objects also in static_objects
items_blend_objects = [obj for obj in items_objects if obj not in static_objects]

# Create and export the items scene
items_blend_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}_items.blend")
items_glb_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}_items.glb")
items_usd_filepath = os.path.join(main_blend_dir, f"{main_blend_base_name}_items.usd")
create_and_export_scene(f"{main_blend_base_name}_items", items_blend_objects, items_blend_filepath, items_glb_filepath, items_usd_filepath, move_to_origin=False)

# Export individual objects in the "Items" collection to the "props" directory
for obj in items_objects:
    if obj.parent is None:
        object_folder = os.path.join(output_directory, clean_name(obj.name))
        if not os.path.exists(object_folder):
            os.makedirs(object_folder)
        
        blend_filepath = os.path.join(object_folder, f"{clean_name(obj.name)}.blend")
        glb_filepath = os.path.join(object_folder, f"{clean_name(obj.name)}.glb")
        usd_filepath = os.path.join(object_folder, f"{clean_name(obj.name)}.usd")
        
        objs_to_link = get_all_children(obj)
        
        create_and_export_scene(clean_name(obj.name), objs_to_link, blend_filepath, glb_filepath, usd_filepath, move_to_origin=True)

# Create the .items.txt file for the main .blend file in its directory
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
            
            # Get root parent's name for the 3D file names
            root_parent = find_root_parent(item_obj)
            root_cleaned_name = clean_name(root_parent.name)
            file_name_glb = f"{root_cleaned_name}.glb"
            file_name_usd = f"{root_cleaned_name}.usd"
            
            # Write to file in the format: name, 3d file (glb), 3d file (usd), x, y, z, rotx, roty, rotz
            file.write(f"{name}, {file_name_glb}, {file_name_usd}, {location.x}, {location.y}, {location.z}, {rotation.x}, {rotation.y}, {rotation.z}\n")

def cleanup_blend_file():
    # Delete the scene named "Scene"
    scene_to_delete = "Scene"
    print(f"Attempting to delete scene: {scene_to_delete}")
    
    try:
        if scene_to_delete in bpy.data.scenes:
            scene = bpy.data.scenes[scene_to_delete]

            # Unlink objects
            for obj in scene.objects:
                bpy.data.objects.remove(obj, do_unlink=True)

            # Delay the delete, it might be that everything haven't been loaded succesfully or something before it do this step, which can crash
            bpy.app.timers.register(lambda: bpy.data.scenes.remove(scene, do_unlink=True), first_interval=1.0)
            print("Scene scheduled for deletion")
        
        # Update Blender
        bpy.context.view_layer.update()
    except Exception as e:
        print(f"Error while deleting scene: {e}")

# Function to find all .blend files in a directory and its subdirectories
def find_blend_files(directory):
    print(directory)
    blend_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            print(file)
            if file.endswith(".blend") and file != main_blend_name:
                blend_files.append(os.path.join(root, file))
    return blend_files

# List of blend files to clean up
blend_files = find_blend_files(main_blend_dir)
print(len(blend_files))

# Perform cleanup on each blend file
for blend_file in blend_files:
    print(blend_file)
    # Open the blend file
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    # Clean up the blend file
    cleanup_blend_file()
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)

# Optionally, print a message indicating the process is complete
print("Finished exporting objects in 'Items' collection and their children to individual .blend files, exporting as .glb and .usd files, and saving *_items.blend and *_empty.blend files.")

exec_time = time.process_time() - st
print("Exporting took: ", exec_time)
