from typing import Optional

import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty
from bpy.types import Operator, Context, Object
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

from addons.HiLoTools.properties.AddonProperties import ObjectGroup
from addons.HiLoTools.utils.entry_utils import get_group_entry


class OBJECT_OT_switch_group_selection(Operator):
    bl_idname = "object.select_group_object"
    bl_label = "组内切换"
    bl_description = "根据active_object，切换组内物体"
    bl_options = {"REGISTER", 'UNDO'}

    selection: EnumProperty(name="选择范围", description="选择模式",
                            items=[("ALL", "全部", "选择全部范围"), ("HIGH MODEL", "高模", "只选择高模"),
                                   ("LOW MODEL", "低模", "只选择低模")])  
    update_select_index: BoolProperty(name="更新索引", description="是否更新组索引，若开启则自动根据所选切换组",
                                      default=False)  

    def execute(self, context: Context):
        active_obj: Object = context.active_object
        scene = context.scene

        if not active_obj:
            return {"CANCELLED"}

        target_index = -1
        if active_obj.group_info:
            _, target_index = get_group_entry(active_obj.group_info)

        if target_index < 0:
            self.report({'WARNING'}, "此物体不属于任何组")
            return {"CANCELLED"}

        object_groups: ObjectGroup = scene.object_groups[target_index]

        bpy.ops.object.select_all(action='DESELECT')

        if self.selection == 'HIGH MODEL' or self.selection == 'ALL':
            for item in object_groups.high_models:
                if item.high_model:
                    item.high_model.select_set(True)
                    context.view_layer.objects.active = item.high_model

        if self.selection == 'LOW MODEL' or self.selection == 'ALL':
            if object_groups.low_model:
                object_groups.low_model.select_set(True)
                context.view_layer.objects.active = object_groups.low_model

        if self.update_select_index:
            scene.object_groups_index = target_index

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
                    with context.temp_override(active_object=obj):
                        bpy.ops.object.select_group_object(selection="ALL", update_select_index=True)
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