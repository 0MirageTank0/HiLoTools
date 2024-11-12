from typing import List

import bpy
from bpy.types import Object, Context

from addons.HiLoTools.utils.material_utils import clear_object_material, apply_material_to_object
from addons.HiLoTools.properties.object_group import ObjectGroup


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
    """处理当前组索引变更"""
    if context.mode != 'OBJECT':
        return

    scene = context.scene
    object_groups: [ObjectGroup] = scene.object_groups
    index = scene.object_groups_index

    scene.selected_high_model = None
    bpy.ops.object.select_all(action='DESELECT')

    if 0 <= index < len(scene.object_groups):
        bpy.ops.object.select_group(group_index=index, select_low=True, select_high=True)
    else:
        return

    if scene.display_mode == "focus":
        if context.space_data.local_view:
            bpy.ops.view3d.localview()
        bpy.ops.view3d.localview()
    elif scene.display_mode == "transparent":
        for i in object_groups:
            i.is_active = False
        object_groups[index].is_active = True


def update_display_mode(self, context: Context):
    scene = context.scene
    object_groups: List[ObjectGroup] = scene.object_groups

    def set_material(o, hide: bool):
        o.hide_select = hide
        if hide:
            apply_material_to_object(o, scene.background_material)
        else:
            clear_object_material(o)

    if scene.display_mode != "transparent":
        for i in object_groups:
            i.is_active = False
        for obj in scene.objects:
            if obj.type == "MESH":
                set_material(obj, False)
    else:
        if scene.transparent_ungrouped:
            for obj in scene.objects:
                if obj.type == "MESH":
                    set_material(obj, True)
        for i in scene.object_groups:
            i.is_active = False

    # 退出聚焦模式
    if scene.display_mode != "focus":
        if context.space_data.local_view:
            bpy.ops.view3d.localview()
    else:

        bpy.ops.view3d.localview()


prev_active_all = None


def update_active_all(self, context: Context):
    """更新所有组的状态"""
    scene = context.scene
    global prev_active_all
    if prev_active_all != scene.active_all:
        def set_active(obj):
            obj.hide_select = not scene.active_all
            if scene.display_mode == "transparent":
                if scene.active_all:
                    clear_object_material(obj)
                else:
                    apply_material_to_object(obj, scene.background_material)

        for grp in scene.object_groups:
            grp: ObjectGroup
            if grp.low_model:
                set_active(grp.low_model)
            for item in grp.high_models:
                if item.high_model:
                    set_active(item.high_model)

        prev_active_all = scene.active_all


def update_transparent_ungrouped(self, context: Context):
    scene = context.scene

    def set_material(o):
        o.hide_select = scene.transparent_ungrouped
        if not scene.transparent_ungrouped:
            clear_object_material(o)
        else:
            apply_material_to_object(o, scene.background_material)

    for obj in scene.objects:
        if obj.type == "MESH":
            if not obj.group_info:
                set_material(obj)
