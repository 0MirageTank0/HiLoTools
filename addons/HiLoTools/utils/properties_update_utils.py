"""
包含一系列主要属性的回调函数
"""
import bpy
from bpy.types import Context

from addons.HiLoTools.operators.view_ops import mark_background_dirty

ignore_next_callback: bool = False


def update_background_color(self, context: Context):
    scene = context.scene
    scene.background_material.diffuse_color = scene.background_color


def update_high_model_color(self, context: Context):
    scene = context.scene
    scene.high_model_material.diffuse_color = scene.high_model_color


def update_low_model_color(self, context: Context):
    scene = context.scene
    scene.low_model_material.diffuse_color = scene.low_model_color


def next_select_group_index_no_callback():
    global ignore_next_callback
    ignore_next_callback = True


def update_select_group_index(self, context: Context):
    """处理当前组索引变更"""
    global ignore_next_callback
    if ignore_next_callback:
        ignore_next_callback = False
        return
    if context.mode != 'OBJECT':
        return
    scene = context.scene
    index = scene.object_groups_index
    # 在其他更新回调事件中会调用此事件，因此需要确保index合法
    if index < 0 or index >= len(scene.object_groups):
        return
    scene.selected_high_model = None
    # 首先处理显示模式的逻辑
    if scene.display_mode == 'transparent':
        if scene.background_material:
            bpy.ops.object.solo_group(group_index=index, influence_ungrouped=scene.transparent_ungrouped)
    elif scene.display_mode == 'focus':
        bpy.ops.object.local_view_group(group_index=index)
    # x_ray需要在其后进行处理
    if scene.x_ray:
        if scene.high_model_material and scene.low_model_material:
            # 如果当前处于transparent模式，则不能清除材质。
            bpy.ops.object.x_ray_group(group_index=index,
                                       clear_others_material=scene.display_mode != 'transparent')
    # 最终处理物体选择逻辑
    bpy.ops.object.select_group(group_index=index, select_low=True, select_high=True)


def update_display_mode(self, context: Context):
    scene = context.scene

    if scene.display_mode != 'transparent':
        if scene.background_material:
            bpy.ops.object.solo_group(exit_solo=True, influence_ungrouped=True)
    if scene.display_mode != 'focus':
        bpy.ops.object.local_view_group(exit_local_view=True)

    update_select_group_index(self, context)
    # update_transparent_ungrouped(self, context)


prev_active_all = None


def update_transparent_ungrouped(self, context: Context):
    scene = context.scene
    mark_background_dirty()
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
