import bpy
from bpy.types import Context

from addons.HiLoTools.operators.material_ops import MATRIAL_OT_create_default_material, \
    MATRIAL_OT_restore_default_material


class VIEW3D_PT_MaterialPanel(bpy.types.Panel):
    bl_label = "材质"
    bl_category = "物体组管理"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context : Context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.operator(MATRIAL_OT_create_default_material.bl_idname, text="创建默认材质")
        row.operator(MATRIAL_OT_restore_default_material.bl_idname, icon="FILE_REFRESH", text="")
        layout.prop(scene, "background_material",text="背景材质")
        layout.prop(scene, "high_model_material",text="高模材质")
        layout.prop(scene, "low_model_material",text="低模材质")

        if scene.background_material:
            layout.prop(scene, "background_color",text="背景")
        if scene.high_model_material:
            layout.prop(scene, "high_model_color",text="高模")
        if scene.low_model_material:
            layout.prop(scene, "low_model_color",text="低模")