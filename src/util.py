import bpy

def SerializeNodes(context):
    nodes = context.selected_nodes
    tree = context.space_data.node_tree

    data = {
        "node": [],
        "link": []
    }

    sel_names = [n.name for n in nodes]

    for node in nodes:
        node_data = {
            "name": node.name,
            "id": node.bl_idname,
            "location": (node.location.x, node.location.y),
            "width": node.width,
            "inputs": [],
            "properties": {}
        }

        for i, sock in enumerate(node.inputs):
            if not sock.is_linked and hasattr(sock, "default_value"):
                val = sock.default_value
                if hasattr(val, "to_tuple"):
                    val = val.to_tuple()
                if hasattr(val, "to_list"):
                    val = val.to_list()

                node_data["inputs"].append({"index": i, "value": val})

        if hasattr(node, "operation"):
            node_data["properties"]["operation"] = node.operation
        if hasattr(node, "blend_type"):
            node_data["properties"]["blend_type"] = node.blend_type
        
        data["node"].append(node_data)
    

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
            
            data["link"].append(link_data)

    return data


def DeserializeNodes(context, data):
    tree = context.space_data.node_tree