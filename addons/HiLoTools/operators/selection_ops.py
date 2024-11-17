from typing import Optional, List

import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty
from bpy.types import Operator, Context, Object
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

from addons.HiLoTools.handler.tab_handler import next_edit_mode_change_no_callback
from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry
_ = bpy.app.translations.pgettext

class OBJECT_OT_select_group(Operator):
    """
    选择根据index,在画面中选择组的成员

    参数:
        group_index: 组索引,会对此进行检查,不合法则跳过
        select_low: 是否选择组内的低模
        select_high: 是否选择组内的高模
        deselect: 是否反转选择(即从当前所选范围内去除高模或者去除低模),默认为假
        clear_selection: 是否在执行之前清除视图中的选择,默认为真
    """
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
            if self.select_low and grp.low_model:
                grp.low_model.select_set(not self.deselect)
                context.view_layer.objects.active = grp.low_model
        else:
            return {'CANCELLED'}
        return {'FINISHED'}


class OBJECT_OT_switch_group_selection(Operator):
    """
    根据当前所选的物体,反推出组,从而选择组的特定部分
    此方法可以处理选择多个物体的情况

    参数:
        selection: 选择范围
        -    ALL: 选择整个组
        -    LOW: 只选择组的低模
        -    HIGH: 只选择组的高模

    例子:
        当前选择了物体A.通过此函数可快速的切换到物体A所对应的所有高模(如果其本身是高模则选择组内所有高模)
        如果当前选择了多个物体,则对每一个物体进行同样的处理过程

    """
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
        selected_objects: List[Object] = \
            [obj for obj in context.selected_objects if obj.type == 'MESH' and obj.group_uuid]
        edit_switch: bool = False

        if context.mode == 'EDIT_MESH':
            edit_switch = True
            bpy.ops.object.mode_set(mode='OBJECT')
            next_edit_mode_change_no_callback()

        if not selected_objects:
            return {'CANCELLED'}

        group_index_list: List[int] = []
        for selected_object in selected_objects:
            ignore, group_index = get_group_entry(selected_object.group_uuid)
            if group_index >= 0:
                group_index_list.append(group_index)

        if not group_index_list:
            return {'CANCELLED'}

        select_low = self.selection == 'LOW'
        select_high = self.selection == 'HIGH'
        if self.selection == 'ALL':
            select_high = select_low = True
        bpy.ops.object.select_all(action='DESELECT')
        for group_index in group_index_list:
            bpy.ops.object.select_group(group_index=group_index, select_low=select_low,
                                        select_high=select_high, clear_selection=False)

        # 反馈：如果切换后没有任何物体，则进行提示
        if not context.selected_objects:
            last_obj: Object = selected_objects[0]
            for obj in selected_objects:
                obj.select_set(True)
                last_obj = obj
            context.view_layer.objects.active = last_obj
            info = "Low-Poly does not exist or is hidden" if select_low else "High-Poly does not exist or is hidden"
            self.report({'WARNING'}, info)

        if edit_switch:
            context.view_layer.objects.active = context.selected_objects[0]
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


class OBJECT_OT_hover_select(Operator):
    """
    按住Alt时,对鼠标所选的物体进行全选组的操作

    参数:
        无
        (_current_group_index用于内部记录)

    """
    bl_idname = 'object.hover_select'
    bl_label = "Hover Select"
    bl_description = "Select object under mouse"
    bl_options = {'REGISTER', 'UNDO'}

    current_group_uuid: StringProperty(options={'HIDDEN'})

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
                    self.current_group_uuid = obj.group_uuid
                    _, index = get_group_entry(obj.group_uuid)
                    if index >= 0:
                        scene.object_groups_index = index
            elif self.current_group_uuid:
                # 鼠标移出物体范围时取消选择
                bpy.ops.object.select_all(action='DESELECT')
                self.current_group_uuid = ""

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

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
    """
    选择指定名称的物体

    参数:
        object_name: 物体名称
    """
    bl_idname = 'object.select_object'
    bl_label = "Select Object"
    bl_description = "Select Object"
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
            obj = context.view_layer.objects.get(self.object_name)
            if obj:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
            else:
                self.report({'WARNING'}, _("{} object exists, but not in the current scene").format(self.object_name))
        else:
            self.report({'WARNING'}, _("Object {} not found").format(self.object_name))
        return {'FINISHED'}


class OBJECT_OT_select_all_group(Operator):
    """
    选择所有组(可进行组内高模/低模部分选择)

    参数:
        select_range: 选择范围
        -   ALL:选择全部范围
        -   HIGH: 选择高模范围
        -   LOW: 选择低模范围
        clear_selection: 是否在执行前先清除视图中选择的物体,默认为真

    """
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
    """
    选择所有未分组的物体

    参数:
        clear_selection: 是否在执行前先清除视图中选择的物体,默认为真
    """
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
                if obj.users_scene and obj.users_scene[0] == scene:
                    obj.select_set(True)
                else:
                    self.report({'WARNING'}, "The object cannot be selected because it is not in the current scene")

        return {'FINISHED'}
