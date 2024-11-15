import bpy
from bpy.types import Context

from addons.HiLoTools.operators.material_ops import MATRIAL_OT_create_default_material, \
    MATRIAL_OT_restore_default_material


class VIEW3D_PT_MaterialPanel(bpy.types.Panel):
    """
    材质面板,用于添加修改默认材质
    """
    bl_label = "Material"
    bl_category = "HiLoTool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.operator(MATRIAL_OT_create_default_material.bl_idname)
        row.operator(MATRIAL_OT_restore_default_material.bl_idname, icon='FILE_REFRESH', text="")
        col = layout.column(align=True)
        col.prop(scene, 'background_material', text="Background Material")
        col.prop(scene, 'high_model_material', text="High-Poly Material")
        col.prop(scene, 'low_model_material', text="Low-Poly Material")
        col.separator()
        if scene.background_material:
            col.prop(scene, 'background_color', text="Background Color", text_ctxt="hl")
        if scene.high_model_material:
            col.prop(scene, 'high_model_color', text="High-Poly Color")
        if scene.low_model_material:
            col.prop(scene, 'low_model_color', text="Low-Poly Color")
            