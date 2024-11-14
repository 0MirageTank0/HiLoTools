from typing import Optional

import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty
from bpy.types import Operator, Context, Object
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry


class OBJECT_OT_select_group(Operator):
    bl_idname = 'object.select_group'
    bl_label = "Select Group"
    bl_description = "Select Group"
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty()
    select_low: BoolProperty()
    select_high: BoolProperty()
    deselect: BoolProperty(default=False)
    clear_selection: BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Can only be used in Object Mode")
            return False
        return True

    def execute(self, context):
        scene = context.scene

        if self.group_index >= len(scene.object_groups) or self.group_index < 0:
            return {'CANCELLED'}
        grp: ObjectGroup = scene.object_groups[self.group_index]
        if grp is not None:
            if self.clear_selection:
                bpy.ops.object.select_all(action='DESELECT')
            if self.select_high:
                for item in grp.high_models:
                    if item.high_model:
                        item.high_model.select_set(not self.deselect)
                        context.view_layer.objects.active = item.high_model
            if self.select_low and grp.low_model:
                grp.low_model.select_set(not self.deselect)
                context.view_layer.objects.active = grp.low_model
        else:
            return {'CANCELLED'}
        return {'FINISHED'}


class OBJECT_OT_switch_group_selection(Operator):
    bl_idname = 'object.switch_group_selection'
    bl_label = "Switch within Group"
    bl_description = "Switch objects within group based on current active item"
    bl_options = {'REGISTER', 'UNDO'}

    selection: EnumProperty(name="Selection Range", description="Selection Mode",
                            items=[('ALL', "All", "Select All"),
                                   ('HIGH', "High-Poly", "Select Only High-Poly"),
                                   ('LOW', "Low-Poly", "Select Only Low-Poly")])

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH' and context.mode != 'OBJECT':
            cls.poll_message_set("Can only be used in Object Mode or Edit Mode")
            return False
        return True

    def execute(self, context: Context):
        active_obj: Object = context.active_object
        edit_switch: bool = False

        if context.mode == 'EDIT_MESH':
            edit_switch = True
            bpy.ops.object.mode_set(mode='OBJECT')

        if not active_obj:
            return {'CANCELLED'}

        if not active_obj.group_uuid:
            self.report({'WARNING'}, "This object does not belong to any group")
            return {'CANCELLED'}

        _, group_index = get_group_entry(active_obj.group_uuid)
        if group_index < 0:
            self.report({'WARNING'}, "Expired UUID")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        select_low = self.selection == 'LOW'
        select_high = self.selection == 'HIGH'
        if self.selection == 'ALL':
            select_high = select_low = True
        bpy.ops.object.select_group(group_index=group_index, select_low=select_low, select_high=select_high)

        if edit_switch:
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


class OBJECT_OT_hover_select(Operator):
    bl_idname = 'object.hover_select'
    bl_label = "Hover Select with Alt Key"
    bl_description = "Select object under mouse while Alt is pressed"
    bl_options = {'REGISTER', 'UNDO'}

    current_group_uuid: StringProperty()

    def modal(self, context, event):
        scene = context.scene
        # 当松开 Alt 键时，停止操作
        if event.type == 'LEFT_ALT' and event.value == 'RELEASE':
            # bpy.ops.object.select_all(action='DESELECT')
            return {'FINISHED'}

        # 检测鼠标移动事件
        if event.type == 'MOUSEMOVE':
            # 获取当前鼠标位置指向的物体
            region = context.region
            region_3d = context.region_data
            coord = (event.mouse_region_x, event.mouse_region_y)
            obj = self.get_object_under_mouse(context, region, region_3d, coord)

            # 如果指向新物体，更新选择状态
            if obj and obj.group_uuid:
                if self.current_group_uuid != obj.group_uuid:
                    _, index = get_group_entry(obj.group_uuid)
                    self.current_group_uuid = obj.group_uuid
                    if index >= 0:
                        print(index)
                        scene.object_groups_index = index
            else:
                # 鼠标移出物体范围时取消选择
                bpy.ops.object.select_all(action='DESELECT')
                self.current_group_uuid = ""

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # 检查 Alt 键是否按下
        if event.alt:
            # 设置操作的 'modal' 模式
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Please hold Alt key to activate hover select.")
            return {'CANCELLED'}

    @staticmethod
    def get_object_under_mouse(context: Context, region, region_3d, coord) -> Optional[Object]:
        # 转换鼠标坐标到 3D 空间的射线
        view_vector = region_2d_to_vector_3d(region, region_3d, coord)
        ray_origin = region_2d_to_origin_3d(region, region_3d, coord)

        # 执行射线检测
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            context.view_layer.depsgraph, ray_origin, view_vector
        )
        return obj if result else None


class OBJECT_OT_select_object(Operator):
    bl_idname = 'object.select_object'
    bl_label = "Select Object"
    bl_options = {'REGISTER', 'UNDO'}

    object_name: bpy.props.StringProperty(name="Object Name", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Can only be used in Object Mode")
            return False
        return True

    def execute(self, context: Context):
        # 获取指定名称的物体
        obj = bpy.data.objects.get(self.object_name)
        if obj:
            if obj.users_scene and obj.users_scene[0] == context.scene:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
            else:
                self.report({'WARNING'}, "{} object exists, but not in the current scene".format(self.object_name))
        else:
            self.report({'WARNING'}, "Object {} not found".format(self.object_name))
        return {'FINISHED'}


class OBJECT_OT_select_all_group(Operator):
    bl_idname = 'object.select_all_group'
    bl_label = "Select All Groups"
    bl_description = "Select all objects in all groups"
    bl_options = {'REGISTER', 'UNDO'}

    select_range: EnumProperty(name="Selection Range", description="Selection Mode",
                               items=[('ALL', "All", "Select All"),
                                      ('HIGH', "High-Poly", "Select Only High-Poly"),
                                      ('LOW', "Low-Poly", "Select Only Low-Poly")])
    clear_selection: BoolProperty(name="Clear Selection", default=True)

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if context.mode != 'OBJECT':
            cls.poll_message_set("Can only be used in Object Mode")
            return False
        return bool(scene.object_groups)

    def execute(self, context):
        scene = context.scene
        select_low: bool = self.select_range == 'LOW'
        select_high: bool = self.select_range == 'HIGH'
        if self.select_range == 'ALL':
            select_low = select_high = True
        if self.clear_selection:
            bpy.ops.object.select_all(action='DESELECT')
        for index in range(len(scene.object_groups)):
            bpy.ops.object.select_group(group_index=index,
                                        select_low=select_low,
                                        select_high=select_high,
                                        clear_selection=False)

        return {'FINISHED'}


class OBJECT_OT_select_ungrouped_objects(Operator):
    bl_idname = 'object.select_ungrouped_objects'
    bl_label = "Select Ungrouped Objects"
    bl_description = "Select objects not in any group"
    bl_options = {'REGISTER', 'UNDO'}

    clear_selection: BoolProperty(name="Clear Selection", default=True)

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Can only be used in Object Mode")
            return False
        return True

    def execute(self, context):
        scene = context.scene

        if self.clear_selection:
            bpy.ops.object.select_all(action='DESELECT')

        for obj in scene.objects:
            if obj.type == 'MESH' and not obj.group_uuid:
                obj.select_set(True)

        return {'FINISHED'}
