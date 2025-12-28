import bpy
import util;

class MY_OT_SaveItem(bpy.types.Operator):
    bl_idname = "global.save_item"
    bl_label = "Add Item"

    def execute(self, context):
        if context.selected_nodes:
            item = context.window_manager.global_list.add()
            item.name = "Nodes"
        return {'FINISHED'}


class MY_OT_RemoveItem(bpy.types.Operator):
    bl_idname = "global.remove_item"
    bl_label = "Remove Item"

    def execute(self, context):
        wm = context.window_manager
        index = wm.global_list_index
        
        if 0 <= index < len(wm.global_list):
            wm.global_list.remove(index)

            if index > 0:
                wm.global_list_index = index - 1
                
        return {'FINISHED'}

class MY_OT_Load(bpy.types.Operator):
    bl_idname = "global.load"
    bl_label = "Load to Node Editor"

    def execute(self, context):
        return {'FINISHED'}

class MY_OT_Reload(bpy.types.Operator):
    bl_idname = "global.reload"
    bl_label = "Reload from File"

    def execute(self, context):
        return {'FINISHED'}