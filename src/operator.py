import bpy
import json
import os

class EXPORT_OT_fbx_auto(bpy.types.Operator):
    bl_idname = "export.fbx_auto"
    bl_label = "Export FBX and Metadata"
    bl_description = "Export selected objects to FBX and generate metadata JSON for Unity"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.selected_objects and context.scene.fbx_export_path)

    def execute(self, context):
        export_dir = context.scene.fbx_export_path

        if not os.path.exists(export_dir):
            self.report({'ERROR'}, f"Export directory does not exist: {export_dir}")
            return {'CANCELLED'}

        obs = context.selected_objects

        if not obs:
            self.report({'ERROR'}, "No objects selected for export")
            return {'CANCELLED'}

        for obj in obs:
            bpy.context.view_layer.objects.active = obj

            name = obj.name.replace(" ", "_")
            fbx_path = os.path.join(export_dir, f"{name}.fbx")
            json_path = os.path.join(export_dir, f"{name}.json")

            bpy.ops.export_scene.fbx(
                filepath=fbx_path,
                use_selection=True,
                axis_forward='-Z',
                axis_up='Y',
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_ALL',
                use_mesh_modifiers=True,
                mesh_smooth_type='OFF'
            )

            metadata = {
                "scaleFactor": 1.0,
                "generateColliders": "COL" in obj.name,
                "isStatic": True,
                "vfxType": "horror_leaking_steam"
            }

            with open(json_path, 'w') as f:
                json.dump(metadata, f, indent=4)

        self.report({'INFO'}, f"Exported {len(obs)} objects to {export_dir}")
        return {'FINISHED'}