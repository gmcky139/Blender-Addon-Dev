import bpy

class VIEW3D_PT_fbx_export(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FBX Exporter"
    bl_label = "FBX Exporter"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # パス設定フィールド
        layout.prop(scene, "fbx_export_path")
        
        layout.separator()
        
        # 実行ボタン
        # icon='EXPORT' で標準のエクスポートアイコンを表示
        layout.operator("export.fbx_auto", text="Export Selected", icon='EXPORT')

