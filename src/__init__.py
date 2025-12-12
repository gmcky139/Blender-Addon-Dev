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

class VIEW3D_PT_my_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Tab"
    bl_label = "Test Panel"

    def draw(self, context):
        self.layout.label(text="Hello Work!")

def register():
    bpy.utils.register_class(VIEW3D_PT_my_panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_my_panel)

if __name__ == "__main__":
    register()