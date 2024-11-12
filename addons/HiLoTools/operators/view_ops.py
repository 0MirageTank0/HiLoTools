import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Context

from addons.HiLoTools.properties.object_group import ObjectGroup
from addons.HiLoTools.utils.material_utils import clear_object_material, clear_group_material, apply_material_to_object, \
    apply_material_to_group, apply_material_to_group_high_model, apply_material_to_group_low_model


class OBJECT_OT_solo_group(Operator):
    bl_idname = "object.solo_group"
    bl_label = "Solo Group"
    bl_description = "Solo Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty(name="Group Index")
    influence_ungrouped: BoolProperty()
    type: EnumProperty(items=[
        ('APPEND', "追加显示组", "在组的active属性发生变化时调用"),
        ('ERASE', "单独去除组", "在组的active属性发生变化时调用"),
        ('DEFAULT', "", "")], default='DEFAULT')
    exit_solo: BoolProperty(default=False)

    def execute(self, context: Context):
        scene = context.scene
        if self.exit_solo:
            if self.influence_ungrouped:
                for obj in scene.objects:
                    if obj.type == "MESH":
                        obj.hide_select = False
                        clear_object_material(obj)
            for index, entry in enumerate(scene.object_groups):
                entry: ObjectGroup
                entry.is_active = True
                clear_group_material(entry)
        else:
            if self.group_index < 0 or self.group_index >= len(scene.object_groups):
                self.report({'ERROR'}, "Invalid Group Index")
                return {'CANCELLED'}
            if self.type == 'DEFAULT':
                # 处理背景
                for obj in scene.objects:
                    if obj.type == "MESH" and not obj.group_uuid:
                        if self.influence_ungrouped:
                            obj.hide_select = True
                            apply_material_to_object(obj, scene.background_material)
                        else:
                            obj.hide_select = False
                            clear_object_material(obj)
                for index, entry in enumerate(scene.object_groups):
                    entry: ObjectGroup
                    if index == self.group_index:
                        entry.is_active = True
                        # clear_group_material(entry) # is_active的回调中会调用此函数,因此无需调用
                    else:
                        entry.is_active = False
                        # apply_material_to_group(entry, scene.background_material)# is_active的回调中会调用此函数,因此无需调用
            else:
                grp: ObjectGroup = scene.object_groups[self.group_index]
                # APPEND/ERASE是发生在is_active的回调中,因此不处理is_active
                if self.type == 'APPEND':
                    clear_group_material(grp)
                elif self.type == 'ERASE':
                    apply_material_to_group(grp, scene.background_material)
        return {'FINISHED'}


class OBJECT_OT_local_view_group(Operator):
    bl_idname = "object.local_view_group"
    bl_label = "Local View Group"
    bl_description = "切换到当前物体组的本地视图"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty(name="Group Index")
    exit_local_view: BoolProperty(default=False)

    def execute(self, context: Context):
        scene = context.scene
        in_local_view = context.space_data.local_view
        if self.exit_local_view:
            if in_local_view:
                bpy.ops.view3d.localview()
        else:
            if self.group_index < 0 or self.group_index >= len(scene.object_groups):
                self.report({'ERROR'}, "Invalid Group Index")
                return {'CANCELLED'}
            if in_local_view:
                bpy.ops.view3d.localview()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_group(group_index=self.group_index, select_low=True, select_high=True)
            bpy.ops.view3d.localview()
        return {'FINISHED'}


class OBJECT_OT_x_ray_group(Operator):
    bl_idname = "object.x_ray_group"
    bl_label = "X-Ray Group"
    bl_description = "切换到物体组的X-Ray模式"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty()
    clear_others_material: BoolProperty(default=False, description="是否需要清除其他组的材质")
    exit_x_ray: BoolProperty(default=False)

    # noinspection PyTypeChecker
    def execute(self, context: Context):
        scene = context.scene
        grp: ObjectGroup
        if self.exit_x_ray:
            self.group_index = -99999999
            self.clear_others_material = True
            grp = None
        else:
            if self.group_index < 0 or self.group_index >= len(scene.object_groups):
                self.report({'ERROR'}, "Invalid Group Index")
                return {'CANCELLED'}
            grp = scene.object_groups[self.group_index]
        if self.clear_others_material:
            for index, group in enumerate(scene.object_groups):
                if index != self.group_index:
                    clear_group_material(group)
                else:
                    apply_material_to_group_high_model(grp, scene.high_model_material)
                    apply_material_to_group_low_model(grp, scene.low_model_material)
        else:
            apply_material_to_group_high_model(grp, scene.high_model_material)
            apply_material_to_group_low_model(grp, scene.low_model_material)
        return {'FINISHED'}
