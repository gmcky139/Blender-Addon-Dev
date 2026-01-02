import bpy
import os
import json
from contextlib import contextmanager

IS_UPDATING = False

"""動的探索をやろうとした残骸
EXCLUDE_PROPS = {
    'rna_type', 'name', 'type', 'location', 'width', 'height', 
    'select', 'dimensions', 'inputs', 'outputs', 'internal_links', 
    'parent', 'label', 'color', 'use_custom_color', 'hide'
}"""


@contextmanager
def prevent_update():
    global IS_UPDATING
    IS_UPDATING = True
    try:
        yield
    finally:
        IS_UPDATING = False

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "global_list_data.json")

def update_list(item_uid, new_name = None, new_data = None):
    if IS_UPDATING:
        return

    current_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                current_data = json.load(f)
        except:
            current_data = []
    
    found = False
    for entry in current_data:
        if entry.get("uid") == item_uid:
            if new_name:
                entry["name"] = new_name
            if new_data:
                entry["node_data"] = json.dumps(new_data, separators=(',', ':'))
            found = True
            break

    if found:
        with open(DATA_FILE, 'w') as f:
            json.dump(current_data, f, indent=4)
        load_from_json()
    else:
        pass

def update_name_in_json(self, context):
    update_list(self.uid, new_name=self.name)

def update_data_in_json(item, data):
    update_list(item.uid, new_data = data)

def load_from_json():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)

            wm = bpy.context.window_manager

            with prevent_update():
                wm.global_list.clear()

                for d in data:
                    item = wm.global_list.add()
                    item.uid = d["uid"]
                    item.name = d["name"]
                    item.node_data = d["node_data"]

        except json.JSONDecodeError:
            print("ファイルの中身は壊れている")

        finally:
            IS_UPDATING = False

def store_to_json():
    wm = bpy.context.window_manager

    data_list = []

    for item in wm.global_list:
        data = {
            "uid": item.uid,
            "name": item.name,
            "node_data": item.node_data
        }
        
        data_list.append(data)

    
    with open(DATA_FILE, 'w') as f:
        json.dump(data_list, f, indent=4)


def SerializeNodes(context, cTree = None):
    if cTree is None:
        nodes = context.selected_nodes
        tree = context.space_data.edit_tree
        if tree is None:
            tree = context.space_data.node_tree

        data = {
            "nodes": [],
            "links": []
        }
    else:
        tree = cTree
        nodes = tree.nodes

        data = {
            "nodes": [],
            "links": [],
            "interface": {"inputs": [], "outputs": []}
        }

        if hasattr(tree, "interface"):
            for item in tree.interface.items_tree:
                if item.item_type != 'SOCKET':
                    continue

                sock_data = {
                    "name": item.name,
                    "type": item.socket_type,
                    "default_value": None
                }

                if hasattr(item, "default_value"):
                    try:
                        sock_data["default_value"] = list(item.default_value)
                    except:
                        sock_data["default_value"] = item.default_value

                if item.in_out == 'INPUT':
                    data["interface"]["inputs"].append(sock_data)
                elif item.in_out == 'OUTPUT':
                    data["interface"]["outputs"].append(sock_data)
   

    sel_names = [n.name for n in nodes]

    target_props = [
        "operation",        # Math, Vector Math, Boolean
        "blend_type",       # Mix Node
        "data_type",        # Mix Node (Float/Vector/Color...)
        "mode",             # Map Range
        "distribution",     # Brick Texture, Voronoi
        "subsurface_method", # Principled BSDF
        "noise_dimensions", # Noise Texture (2D/3D/4D)
        "noise_type",       # Noise Texture (fBM...)
        "normalize",        # Noise Texture (normalize)
        "feature",          # Voronoi (F1, F2...)
        "distance",         # Voronoi (Euclidean...)
        "use_clamp",        # Math Node Checkbox
        "clamp_result",     # Mix Node Checkbox
        "clamp_factor",     # Mix Node Checkbox (Old)
        "interpolation",    # Image Texture
        "interpolation_type", # Map Range
        "color_mode",       # Gradient Texture
        "wave_type",        # Wave Texture
        "wave_profile",     # Wave Texture
        "rings_direction",  # Wave Texture
        "projection",       # Image Texture
        "extension",        # Image Texture
    ]

    for node in nodes:
        node_data = {
            "name": node.name,
            "type": node.bl_idname,
            "location": (node.location.x, node.location.y),
            "width": node.width,
            "inputs": [],
            "outputs": [],
            "properties": {}
        }

        for prop_name in target_props:
            if hasattr(node, prop_name):
                val = getattr(node, prop_name)
                node_data["properties"][prop_name] = val

        for i, sock in enumerate(node.inputs):
            if not sock.is_linked and hasattr(sock, "default_value"):
                val = sock.default_value

                try:
                    val = list(val)
                except:
                    pass

                node_data["inputs"].append({"index": i, "value": val})

        for i, sock in enumerate(node.outputs):
            if hasattr(sock, "default_value"):
                val = sock.default_value

                try:
                    val = list(val)
                except:
                    pass

                node_data["outputs"].append({"index": i, "value": val})

        if node.bl_idname == 'ShaderNodeValToRGB':
            ramp = node.color_ramp
            ramp_data = {
                "color_mode": ramp.color_mode,
                "interpolation": ramp.interpolation,
                "elements": []
            }
            for elt in ramp.elements:
                ramp_data["elements"].append({
                    "position": elt.position,
                    "color": list(elt.color)
                })
            node_data["special_data"] = {
                "type": "ramp",
                "data": ramp_data
            }
        elif node.bl_idname in ('ShaderNodeRGBCurve', 'ShaderNodeVectorCurve'):
            curve_mapping = node.mapping
            curve_data = {
                "curves": []
            }

            for curve in curve_mapping.curves:
                point_data = []
                for p in curve.points:
                    point_data.append({
                        "location": (p.location.x, p.location.y),
                        "handle_type": p.handle_type
                    })
                curve_data["curves"].append(point_data)

            curve_data["clip_min_x"] = curve_mapping.clip_min_x
            curve_data["clip_min_y"] = curve_mapping.clip_min_y
            curve_data["clip_max_x"] = curve_mapping.clip_max_x
            curve_data["clip_max_y"] = curve_mapping.clip_max_y
            curve_data["use_clip"] = curve_mapping.use_clip
               
            node_data["special_data"] = {
                "type": "curve",
                "data": curve_data
            }

        elif node.bl_idname == 'ShaderNodeTexImage':
            img_data = {}
            if node.image:
                img_data["image_name"] = node.image.name

                img_data["filepath"] = node.image.filepath

                if hasattr(node.image, "colorspace_settings"):
                    img_data["color_space"] = node.image.colorspace_settings.name

                img_data["source"] = node.image.source
                img_data["alpha_mode"] = node.image.alpha_mode
           
            node_data["special_data"] = {"type": "image", "data": img_data}
       
        elif node.type == 'GROUP':
            group_data = {}
            if node.node_tree:
                childTree = node.node_tree
                group_data["tree_name"] = childTree.name
                group_data["tree_type"] = childTree.bl_idname
                group_data["node_data"] = SerializeNodes(context, childTree)

            node_data["special_data"] = {"type": "group", "data": group_data}

        data["nodes"].append(node_data)
   
    for link in tree.links:
        if link.from_node.name in sel_names and link.to_node.name in sel_names:
            link_data = {
                "from_node": link.from_node.name,
                "from_socket_index": -1,
                "to_node": link.to_node.name,
                "to_socket_index": -1
            }

            for i, sock in enumerate(link.from_node.outputs):
                if sock == link.from_socket:
                    link_data["from_socket_index"] = i
                    break
           
            for i, sock in enumerate(link.to_node.inputs):
                if sock == link.to_socket:
                    link_data["to_socket_index"] = i
                    break
           
            data["links"].append(link_data)

    return data


def DeserializeNodes(self, context, data, iTree = None):
    tree = context.space_data.edit_tree
    if tree is None:
        tree = context.space_data.node_tree

    if iTree:
        tree = iTree

    for n in tree.nodes:
        n.select = False

    node_map = {}

    node_list = data.get("nodes", [])

    for n_data in node_list:
        try:
            new_node = tree.nodes.new(n_data["type"])
        except RuntimeError:
            print(f"Node Type Not Found: {n_data['type']}")
            continue
        new_node.location = n_data["location"]
        new_node.width = n_data["width"]
        new_node.select = True
        node_map[n_data["name"]] = new_node

        special = n_data.get("special_data")

        if special:
            sType = special["type"]
            sData = special["data"]

            if sType == "ramp" and hasattr(new_node, "color_ramp"):
                ramp = new_node.color_ramp
                ramp.color_mode = sData.get("color_mode", 'RGB')
                ramp.interpolation = sData.get("interpolation", 'LINEAR')

                elements_data = sData.get("elements", [])

                while len(ramp.elements) < len(elements_data):
                    ramp.elements.new(1.0)
                while len(ramp.elements) > len(elements_data):
                    ramp.elements.remove(ramp.elements[-1])

                for i, elt_d in enumerate(elements_data):
                    elt = ramp.elements[i]
                    elt.position = elt_d["position"]
                    elt.color = elt_d["color"]

            elif sType == "curve" and hasattr(new_node, "mapping"):
                mapping = new_node.mapping
                mapping.clip_min_x = sData.get("clip_min_x", 0.0)
                mapping.clip_min_y = sData.get("clip_min_y", 0.0)
                mapping.clip_max_x = sData.get("clip_max_x", 1.0)
                mapping.clip_max_y = sData.get("clip_max_y", 1.0)
                mapping.use_clip = sData.get("use_clip", False)

                saved_curve = sData.get("curves", [])

                for i, points_list in enumerate(saved_curve):
                    if i >= len(mapping.curves):
                        break

                    curve = mapping.curves[i]

                    while len(curve.points) < len(points_list):
                        curve.points.new(0.0, 0.0)
                    while len(curve.points) > len(points_list):
                        curve.points.remove(curve.points[-1])

                    for j, p_data in enumerate(points_list):
                        p = curve.points[j]
                        p.location.x = p_data["location"][0]
                        p.location.y = p_data["location"][1]
                        p.handle_type = p_data.get("handle_type", 'AUTO')

                if hasattr(mapping, "update"):
                    mapping.update()

            elif sType == "image":
                img_name = sData.get("image_name")
                filepath = sData.get("filepath", "")

                image = None

                if img_name:
                    image = bpy.data.images.get(img_name)

                if not image and filepath:
                    try:
                        image = bpy.data.images.load(filepath, check_existing=True)
                    except RuntimeError:
                        print(f"ロード失敗: {filepath}")

                if image:
                    new_node.image = image
                    if "color_space" in sData and hasattr(image, "colorspace_settings"):
                        image.colorspace_settings.name = sData["color_space"]
                    if "source" in sData:
                        image.source = sData["source"]
                    if "alpha_mode" in sData:
                        image.alpha_mode = sData["alpha_mode"]
                   
                else:
                    self.report({'WARNING'}, f"画像 '{img_name}' (パス: {filepath}) が見つかりませんでした")

            elif sType == "group":
                tree_name = sData.get("tree_name")

                if tree_name:
                    found_group = bpy.data.node_groups.get(tree_name)

                    if found_group:
                        new_node.node_tree = found_group
                   
                    else:
                        group_type = sData.get("tree_type", "ShaderNodeTree")
                        new_group = bpy.data.node_groups.new(name = tree_name, type = group_type)

                        inner_data = sData.get("node_data")

                        if inner_data:
                            interface_data = inner_data.get("interface")

                            if interface_data and hasattr(new_group, "interface"):
                                for sock_d in interface_data.get("inputs", []):
                                    sk = new_group.interface.new_socket(name = sock_d["name"], in_out = 'INPUT', socket_type = sock_d["type"])

                                    if "default_value" in sock_d and hasattr(sk, "default_value"):
                                        try:
                                            sk.default_value = sock_d["default_value"]
                                        except:
                                            pass
                               
                                for sock_d in interface_data.get("outputs", []):
                                    new_group.interface.new_socket(name = sock_d["name"], in_out = 'OUTPUT', socket_type = sock_d["type"])
                            DeserializeNodes(self, context, inner_data, new_group)
                           
                        new_node.node_tree = new_group

                       
           
        for prop, val in n_data["properties"].items():
            if hasattr(new_node, prop):
                try:
                    setattr(new_node,prop,val)
                except AttributeError:
                    pass
                except TypeError:
                    pass
       
        for inp in n_data["inputs"]:
            idx = inp["index"]
            val = inp["value"]

            if idx < len(new_node.inputs):
                try:
                    new_node.inputs[idx].default_value = val
                except:
                    pass

        for otp in n_data["outputs"]:
            idx = otp["index"]
            val = otp["value"]

            if idx < len(new_node.outputs):
                try:
                    new_node.outputs[idx].default_value = val
                except:
                    pass



   

    for l_data in data["links"]:
        try:
            node_from = node_map[l_data["from_node"]]
            node_to = node_map[l_data["to_node"]]

            socket_out = node_from.outputs[l_data["from_socket_index"]]
            socket_in = node_to.inputs[l_data["to_socket_index"]]

            tree.links.new(socket_out, socket_in)

        except KeyError:
            pass
        except IndexError:
            print("Link Error: Socket index out of range")

    return {'FINISHED'}