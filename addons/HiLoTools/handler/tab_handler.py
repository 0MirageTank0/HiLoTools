import bpy
from bpy.types import Object

from addons.HiLoTools.properties.object_group import get_group_entry

handling: bool = False


def mode_change_callback():
    """
    处理进入编辑模式的逻辑:
    如果是一个组中的高模与低模,则自动的切换到低模的编辑模式.
    因为同时编辑高模低模通常没有意义
    """
    global handling
    if handling:
        return
    handling = True
    if bpy.context.mode == 'EDIT_MESH':
        context = bpy.context
        scene = context.scene
        selected_objects = context.selected_objects
        if not selected_objects:
            handling = False
            return
        group_uuid: str = selected_objects[0].group_uuid
        if len(selected_objects) == 1:
            # 只选择了一个物体 自动更新index
            index = -1
            if group_uuid:
                _, index = get_group_entry(group_uuid)
            scene.object_groups_index = index
        else:
            # 选择了多个物体，检查所选是否全部属于同一个组
            if group_uuid:
                for selected_object in selected_objects:
                    if group_uuid != selected_object.group_uuid:
                        group_uuid = ""
                        break
                index = -1
                if group_uuid:
                    low_model: Object = NotImplemented
                    grp, index = get_group_entry(group_uuid)
                    if grp.low_model:
                        for selected_object in selected_objects:
                            if grp.low_model == selected_object:
                                low_model = grp.low_model
                                break
                        if low_model:
                            # 选择了低模，则自动切换为低模
                            bpy.ops.object.mode_set(mode='OBJECT')
                            bpy.ops.object.select_all(action='DESELECT')
                            low_model.select_set(True)
                            bpy.context.view_layer.objects.active = low_model
                            bpy.ops.object.mode_set(mode='EDIT')
                scene.object_groups_index = index
    handling = False


# 启动操作并监听Tab键的按下
def tab_register():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "mode"),
        owner="object_mode_check",
        notify=mode_change_callback,
        args=()
    )


def tab_unregister():
    bpy.msgbus.clear_by_owner("object_mode_check")
