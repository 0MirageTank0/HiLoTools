from bpy.props import BoolProperty
from bpy.types import Operator, Context

from addons.HiLoTools.utils.material_utils import create_material


class MATRIAL_OT_restore_default_material(Operator):
    bl_idname = 'material.restore_default_material'
    bl_label = "Restore Default Material"
    bl_description = "Restore Default Material"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.background_material or scene.high_model_material or scene.low_model_material

    def execute(self, context: Context):
        scene = context.scene
        if scene.background_material:
            scene.background_color = (0, 0, 0, 0.15)
        if scene.high_model_material:
            scene.high_model_color = (1, 0, 0, 1)
        if scene.low_model_material:
            scene.low_model_color = (1, 1, 1, 0.1)
        return {'FINISHED'}


class MATRIAL_OT_create_default_material(Operator):
    bl_idname = 'material.create_default_material'
    bl_label = "Create Default Material"
    bl_description = "Create Default Material"
    bl_options = {'REGISTER', 'UNDO'}

    background: BoolProperty(name="Background Material", description="Add Background Material", default=True)
    high_model: BoolProperty(name="High-Poly Material", description="Add High-Poly Material", default=True)
    low_model: BoolProperty(name="Low-Poly Material", description="Add Low-Poly Material", default=True)

    @classmethod
    def poll(cls, context: Context):
        scene = context.scene
        return not scene.background_material or not scene.high_model_material or not scene.low_model_material

    def execute(self, context: Context):
        scene = context.scene
        if self.background and not scene.background_material:
            scene.background_material = create_material('_background_material', (0, 0, 0, 0.15))
            scene.background_color = scene.background_material.diffuse_color
        if self.high_model and not scene.high_model_material:
            scene.high_model_material = create_material('_high_model_material', (1, 0, 0, 1))
            scene.high_model_color = scene.high_model_material.diffuse_color
        if self.low_model and not scene.low_model_material:
            scene.low_model_material = create_material('_low_model_material', (1, 1, 1, 0.1))
            scene.low_model_color = scene.low_model_material.diffuse_color

        return {'FINISHED'}