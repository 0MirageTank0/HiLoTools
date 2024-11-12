from typing import Optional

import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty, IntProperty
from bpy.types import Operator, Context, Object
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry


class OBJECT_OT_select_group(Operator):
    bl_idname = "object.select_group"
    bl_label = "选择组"
    bl_description = "选择组"
    bl_options = {"REGISTER", 'UNDO'}

    group_index: IntProperty()
    select_low: BoolProperty()
    select_high: BoolProperty()
    clear_selection: BoolProperty(default=True)

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
                        item.high_model.select_set(True)
                        context.view_layer.objects.active = item.high_model
            if self.select_low and grp.low_model:
                grp.low_model.select_set(True)
                context.view_layer.objects.active = grp.low_model
        else:
            return {'CANCELLED'}
        return {'FINISHED'}


class OBJECT_OT_switch_group_selection(Operator):
    bl_idname = "object.switch_group_selection"
    bl_label = "组内切换"
    bl_description = "根据active_object，切换组内物体"
    bl_options = {"REGISTER", 'UNDO'}

    selection: EnumProperty(name="选择范围", description="选择模式",
                            items=[("ALL", "全部", "选择全部范围"), ("HIGH MODEL", "高模", "只选择高模"),
                                   ("LOW MODEL", "低模", "只选择低模")])

    def execute(self, context: Context):
        active_obj: Object = context.active_object

        if not active_obj:
            return {"CANCELLED"}

        if not active_obj.group_info:
            self.report({'WARNING'}, "此物体不属于任何组")
            return {"CANCELLED"}

        _, group_index = get_group_entry(active_obj.group_info)
        if group_index < 0:
            self.report({'WARNING'}, "过期的UUID")
            return {"CANCELLED"}

        bpy.ops.object.select_all(action='DESELECT')
        select_low = self.selection == 'LOW MODEL'
        select_high = self.selection == 'HIGH MODEL'
        if self.selection == 'ALL':
            select_high = select_low = True
        bpy.ops.object.select_group(group_index=group_index, select_low=select_low, select_high=select_high)

        return {"FINISHED"}


class OBJECT_OT_hover_select(Operator):
    bl_idname = "object.hover_select"
    bl_label = "Hover Select with Alt Key"
    bl_description = "Select object under mouse while Alt is pressed"
    bl_options = {'REGISTER', 'UNDO'}

    current_object: StringProperty()

    def modal(self, context, event):
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
            if obj:
                if self.current_object != obj.name:
                    self.current_object = obj.name
                    _, index = get_group_entry(obj.group_info)
                    bpy.ops.object.select_group(group_index=index, select_low=True, select_high=True)
            else:
                # 鼠标移出物体范围时取消选择
                bpy.ops.object.select_all(action='DESELECT')
                self.current_object = ""

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

    def get_object_under_mouse(self, context: Context, region, region_3d, coord) -> Optional[Object]:
        # 转换鼠标坐标到 3D 空间的射线
        view_vector = region_2d_to_vector_3d(region, region_3d, coord)
        ray_origin = region_2d_to_origin_3d(region, region_3d, coord)

        # 执行射线检测
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            context.view_layer.depsgraph, ray_origin, view_vector
        )
        return obj if result else None


class OBJECT_OT_select_object(Operator):
    bl_idname = "object.select_object"
    bl_label = "选择物体"
    bl_options = {'REGISTER', 'UNDO'}

    object_name: bpy.props.StringProperty(name="Object Name")

    def execute(self, context: Context):
        # 获取指定名称的物体
        obj = bpy.data.objects.get(self.object_name)
        if obj:
            if obj.users_scene and obj.users_scene[0] == context.scene:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
            else:
                self.report({'WARNING'}, f"{self.object_name} 物体存在，但 不在当前场景中")
        else:
            self.report({'WARNING'}, f"未找到物体 {self.object_name}")
        return {'FINISHED'}


class OBJECT_OT_select_all_group(Operator):
    bl_idname = "object.select_all_group"
    bl_label = "全选组"
    bl_description = "全选所有组物体"
    bl_options = {"REGISTER", "UNDO"}

    select_range: EnumProperty(name="Range", items=[
        ("ALL", "全部", "选择全部"),
        ("HIGH", "高模", "只选择高模"),
        ("LOW", "低模", "只选择低模"),
    ])
    clear_selection: BoolProperty(name="Clear Selection", default=True)

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return bool(scene.object_groups)

    def execute(self, context):
        scene = context.scene
        select_low: bool = self.select_range == "LOW"
        select_high: bool = self.select_range == "HIGH"
        if self.select_range == "ALL":
            select_low = select_high = True
        if self.clear_selection:
            bpy.ops.object.select_all(action='DESELECT')
        for index in range(len(scene.object_groups)):
            bpy.ops.object.select_group(group_index=index, select_low=select_low, select_high=select_high)

        return {'FINISHED'}


class OBJECT_OT_select_ungrouped_objects(Operator):
    bl_idname = "object.select_ungrouped_objects"
    bl_label = "选择未分组对象"
    bl_description = "选择未分组的对象"
    bl_options = {"REGISTER", "UNDO"}

    clear_selection: BoolProperty(name="Clear Selection", default=True)

    def execute(self, context):
        scene = context.scene

        if self.clear_selection:
            bpy.ops.object.select_all(action='DESELECT')

        for obj in scene.objects:
            if obj.type == "MESH" and not obj.group_info:
                obj.select_set(True)

        return {'FINISHED'}
