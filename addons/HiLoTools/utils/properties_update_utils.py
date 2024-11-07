from typing import List

import bpy
from bpy.types import Object, Context


def update_background_color(self, context: Context):
    scene = context.scene
    scene.background_material.diffuse_color = scene.background_color


def update_high_model_color(self, context: Context):
    scene = context.scene
    scene.high_model_material.diffuse_color = scene.high_model_color


def update_low_model_color(self, context: Context):
    scene = context.scene
    scene.low_model_material.diffuse_color = scene.low_model_color


def update_select_group_index(self, context: Context):
    if context.mode != 'OBJECT':
        return

    scene = context.scene
    object_groups: [] = scene.object_groups
    index = scene.object_groups_index

    bpy.ops.object.select_all(action='DESELECT')

    if context.space_data.local_view:
        bpy.ops.view3d.localview()

    # 选择高模物体
    if 0 <= index < len(object_groups):
        for i in object_groups[index].high_models:
            if i.high_model:
                i.high_model.hide_select = False  # 提前解锁 防止无法被选中
                i.high_model.select_set(True)
                context.view_layer.objects.active = i.high_model
    else:
        return
    # 选择低模物体
    low_model: Object = object_groups[index].low_model
    if low_model:
        low_model.hide_select = False  # 提前解锁 防止无法被选中
        low_model.select_set(True)
        context.view_layer.objects.active = low_model

    if scene.display_mode == "focus":
        bpy.ops.view3d.localview()
    elif scene.display_mode == "transparent":
        for i in object_groups:
            i.is_active = False
        object_groups[index].is_active = True


def update_display_mode(self, context: Context):
    scene = context.scene
    object_groups = scene.object_groups
    # 取消其他物体半透效果
    for i in object_groups:
        i.is_active = False
    # 退出聚焦模式
    if context.space_data.local_view:
        bpy.ops.view3d.localview()