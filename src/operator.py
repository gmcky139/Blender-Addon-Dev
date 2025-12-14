import bpy

class MY_OT_AddItem(bpy.types.Operator):
    bl_idname = "global.add_item"
    bl_label = "Add Item"

    def execute(self, context):
        item = context.window_manager.global_list.add()
        item.name = "Global Item"
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

class MY_OT_ForceLoad(bpy.types.Operator):
    bl_idname = "my_global.force_load"
    bl_label = "Reload from File"

    def execute(self, context):
        return {'FINISHED'}