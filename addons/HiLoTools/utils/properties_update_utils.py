from typing import List

import bpy
from bpy.types import Object, Context, Scene

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
    index = scene.object_groups_index
    scene.active_group_uuid = scene.object_groups[index].uuid
    scene.selected_high_model = None
    if scene.display_mode == "transparent":
        bpy.ops.object.solo_group(group_index=index, influence_ungrouped=scene.transparent_ungrouped)
    elif scene.display_mode == "focus":
        bpy.ops.object.local_view_group(group_index=index)

    if scene.x_ray:
        bpy.ops.object.x_ray_group(group_index=index, clear_others_material=scene.display_mode != "transparent")

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_group(group_index=index, select_low=True, select_high=True)


def update_display_mode(self, context: Context):
    scene = context.scene

    if scene.display_mode != "transparent":
        bpy.ops.object.solo_group(exit_solo=True, influence_ungrouped=True)
    if scene.display_mode != "focus":
        bpy.ops.object.local_view_group(exit_local_view=True)

    update_select_group_index(self, context)
    # update_transparent_ungrouped(self, context)


prev_active_all = None


def update_transparent_ungrouped(self, context: Context):
    scene = context.scene
    # if not scene.transparent_ungrouped:
    #     bpy.ops.object.solo_group(exit_solo=True, influence_ungrouped=scene.transparent_ungrouped)
    update_select_group_index(self, context)


def update_x_ray(self, context: Context):
    scene = context.scene
    if not scene.x_ray:
        bpy.ops.object.x_ray_group(exit_x_ray=True)
    else:
        update_select_group_index(self, context)
    # scene = context.scene
    # grp = scene.object_groups[scene.object_groups_index]
    # if scene.transparent:
    #     if grp.low_model and scene.low_model_material:
    #         apply_material_to_object(grp.low_model, scene.low_model_material)
    #     if scene.high_model_material:
    #         for h in grp.high_models:
    #             if h.high_model:
    #                 apply_material_to_object(h.high_model, scene.high_model_material)
    # else:
    #     if grp.low_model:
    #         clear_object_material(grp.low_model)
    #     for h in grp.high_models:
    #         if h.high_model:
    #             clear_object_material(h.high_model)
