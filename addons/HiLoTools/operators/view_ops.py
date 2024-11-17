import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Context

from addons.HiLoTools.properties.object_group import ObjectGroup
from addons.HiLoTools.utils.material_utils import clear_object_material, clear_group_material, apply_material_to_object, \
    apply_material_to_group, apply_material_to_group_high_model, apply_material_to_group_low_model

"""
注意:
目前实现X-Ray/半透效果的方式基于材质,因此无法区分当前应用的效果究竟是什么,所谓"退出半透/X-Ray"只是统一的删除所有材质.
这会导致物体丢失原有材质.

"""

is_dirty_background: bool = True


def mark_background_dirty():
    global is_dirty_background
    is_dirty_background = True


class OBJECT_OT_solo_group(Operator):
    """
    根据组的index,对其他组应用半透效果

    参数:
        group_index: 组的索引,会对其进行检查
        influence_ungrouped: 是否对未分组对象应用半透效果
        type: 触发类型
        -   TOGGLE: 状态切换(处理当用户在列表中点选小图标时的逻辑)
        -   DEFAULT: 默认,每次对无关组应用半透效果
        exit_solo: 退出半透,清除所有效果
    """
    bl_idname = 'object.solo_group'
    bl_label = "Solo Group"
    bl_description = "Solo Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty(options={'HIDDEN'})
    influence_ungrouped: BoolProperty(options={'HIDDEN'})
    type: EnumProperty(items=[
        ('TOGGLE', "", ""),
        ('DEFAULT', "", "")], default='DEFAULT', options={'HIDDEN'})
    exit_solo: BoolProperty(default=False, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if not scene.background_material:
            cls.poll_message_set("To make the semi-transparent work, initialize the background material first")
            return False
        return True

    def execute(self, context: Context):
        global is_dirty_background
        scene = context.scene
        if self.exit_solo:
            if self.influence_ungrouped:
                for obj in scene.objects:
                    if obj.type == 'MESH' and not obj.group_uuid:
                        obj.hide_select = False
                        clear_object_material(obj)
            for index, entry in enumerate(scene.object_groups):
                entry: ObjectGroup
                if entry.in_background_material:
                    entry.in_background_material = False
                    entry.is_active = True
                    clear_group_material(entry)
            is_dirty_background = True
        else:
            if self.group_index < 0 or self.group_index >= len(scene.object_groups):
                self.report({'ERROR'}, "Invalid Group Index")
                return {'CANCELLED'}
            if self.type == 'DEFAULT':
                # 处理背景
                if is_dirty_background:
                    for obj in scene.objects:
                        if obj.type == 'MESH' and not obj.group_uuid:
                            if self.influence_ungrouped:
                                obj.hide_select = True
                                apply_material_to_object(obj, scene.background_material)
                            else:
                                obj.hide_select = False
                                clear_object_material(obj)
                    is_dirty_background = False
                for index, entry in enumerate(scene.object_groups):
                    entry: ObjectGroup
                    entry.in_x_ray_material = False
                    if index == self.group_index:
                        if entry.in_background_material:
                            entry.in_background_material = False
                            entry.is_active = True
                            clear_group_material(entry)
                    else:
                        if not entry.in_background_material:
                            entry.in_background_material = True
                            entry.is_active = False
                            apply_material_to_group(entry, scene.background_material)
            elif self.type == 'TOGGLE':
                grp: ObjectGroup = scene.object_groups[self.group_index]
                grp.is_active = not grp.is_active
                grp.in_background_material = not grp.in_background_material
                if grp.is_active:
                    clear_group_material(grp)
                else:
                    apply_material_to_group(grp, scene.background_material)
                bpy.ops.object.select_all(action='SELECT')

        return {'FINISHED'}


class OBJECT_OT_local_view_group(Operator):
    """
    根据组的index,进入对应组的局部视图。（在局部视图中，默认不会选择任何物体，因为这无必要）

    参数:
        group_index: 组的索引,会对其进行检查
        type: 触发类型
        -   TOGGLE: 状态切换(处理当用户在列表中点选小图标时的逻辑)
        -   DEFAULT: 默认,每次只进入当前组的局部视图
        exit_local_view: 退出,清除所有效果
    """
    bl_idname = 'object.local_view_group'
    bl_label = "Local View Group"
    bl_description = "Switch to the local view of the current object group"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty(options={'HIDDEN'})
    type: EnumProperty(items=[
        ('TOGGLE', "", ""),
        ('DEFAULT', "", "")], default='DEFAULT', options={'HIDDEN'})
    exit_local_view: BoolProperty(default=False, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Can only be used in Object Mode")
            return False
        return True

    def execute(self, context: Context):
        scene = context.scene
        in_local_view = context.space_data.local_view
        if self.exit_local_view:
            if in_local_view:
                bpy.ops.view3d.localview()
            for entry in scene.object_groups:
                entry.is_active = True
        else:
            if self.group_index < 0 or self.group_index >= len(scene.object_groups):
                self.report({'ERROR'}, "Invalid Group Index")
                return {'CANCELLED'}
            # 确保始终先退出局部视图
            if in_local_view:
                bpy.ops.view3d.localview()

            if self.type == 'DEFAULT':
                for index, entry in enumerate(scene.object_groups):
                    if index == self.group_index:
                        entry.is_active = True
                    else:
                        entry.is_active = False
                bpy.ops.object.select_group(group_index=self.group_index, select_low=True, select_high=True)
                bpy.ops.view3d.localview()
            elif self.type == 'TOGGLE':
                bpy.ops.object.select_all(action='SELECT')
                grp: ObjectGroup = scene.object_groups[self.group_index]
                grp.is_active = not grp.is_active
                if grp.is_active:
                    bpy.ops.object.select_group(group_index=self.group_index,
                                                select_low=True, select_high=True,
                                                clear_selection=False)
                else:
                    bpy.ops.object.select_group(group_index=self.group_index,
                                                select_low=True, select_high=True,
                                                deselect=True, clear_selection=False)
                if not context.selected_objects:
                    self.report({'WARNING'}, "Please select at least one group")
                else:
                    bpy.ops.view3d.localview()
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


class OBJECT_OT_x_ray_group(Operator):
    """
    根据组的index,对组应用X-Ray效果

    参数:
        group_index: 组的索引,会对其进行检查
        clear_others_material: 是否清除无关组的材质
        exit_x_ray: 退出X-Ray,清除所有效果
    """
    bl_idname = 'object.x_ray_group'
    bl_label = "X-Ray Group"
    bl_description = "Switch to X-Ray mode for the object group"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty()
    clear_others_material: BoolProperty(default=False)
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
                group: ObjectGroup
                if index != self.group_index:
                    if group.in_x_ray_material:
                        clear_group_material(group)
                        group.in_x_ray_material = False
                        group.in_background_material = False
                else:
                    if not group.in_x_ray_material:
                        apply_material_to_group_high_model(grp, scene.high_model_material)
                        apply_material_to_group_low_model(grp, scene.low_model_material)
                        group.in_x_ray_material = True
        else:
            if not grp.in_x_ray_material:
                apply_material_to_group_high_model(grp, scene.high_model_material)
                apply_material_to_group_low_model(grp, scene.low_model_material)
                grp.in_x_ray_material = True
        return {'FINISHED'}
