bl_info = {
    "name": "My Container Addon",
    "author": "Koji Umeda",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > My Tab",
    "description": "Dev Container Test Addon",
    "category": "Development",
}

import bpy
import importlib
import os
from . import ui
from . import operator


DATA_FILE = os.path.join(os.path.dirname(__file__), "global_list_data.json")

class GlobalItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="New Item")
    value: bpy.props.IntProperty(name="Value", default=0)

pyfiles = [
    ui,
    operator
]

for p in pyfiles:
    if str(p) in locals():
        importlib.reload(p)

classes = [
    GlobalItem,
    ui.MY_UL_List,
    operator.MY_OT_AddItem,
    operator.MY_OT_RemoveItem,
    operator.MY_OT_ForceLoad,
    ui.NODE_PT_my_panel
]

def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.WindowManager.global_list = bpy.props.CollectionProperty(type=GlobalItem)
    bpy.types.WindowManager.global_list_index = bpy.props.IntProperty()

def unregister():
    del bpy.types.WindowManager.global_list
    del bpy.types.WindowManager.global_list_index

    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()