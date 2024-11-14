from typing import Optional

import bpy
from bpy.app.handlers import persistent
from bpy.types import Object, Scene

from addons.HiLoTools.properties.object_group import get_group_entry
from addons.HiLoTools.utils.text_utils import remove_text, show_text_on_object
_ = bpy.app.translations.pgettext

# 定义事件处理器
last_object_num: int = 0
handling = False
last_active_object: Optional[Object] = None
last_object_set = set()
index_in_edit = -1


def is_object_valid(obj):
    try:
        _ = obj.name
        return True
    except ReferenceError:
        return False


def on_object_num_changed(current_objects_set: set):
    global last_object_num, last_object_set
    current_object_num = len(current_objects_set)
    # 物体数量变化 添加了对象
    if current_object_num > last_object_num:
        # 检测新添加的对象
        new_object_set = current_objects_set - last_object_set
        for new_object in new_object_set:
            uuid = new_object.group_uuid
            if uuid:
                # 检查uuid是否存在
                grp, _ = get_group_entry(uuid)
                if not grp:  # 不存在组
                    new_object.group_uuid = ""
                    print("clear_uuid")
                else:  # 存在组
                    # 可能是撤销导致的物体增加 进行双重检查
                    if all(hm.high_model != new_object for hm in grp.high_models):
                        h = grp.high_models.add()
                        h.high_model = new_object
                        print("add_to_group")
                    else:
                        print("is undo,ignore add")
    # 物体数量变化 删除了对象
    else:
        del_object_set = last_object_set - current_objects_set
        for del_object in del_object_set:
            if is_object_valid(del_object):
                if del_object.type != "MESH":
                    return
                uuid = del_object.group_uuid
                if uuid:
                    grp, _ = get_group_entry(uuid)
                    # 如果是低模 则删除低模
                    if grp is not None:
                        if grp.low_model:
                            if grp.low_model == del_object and not grp.low_model.users_scene:
                                bpy.data.objects.remove(grp.low_model)
                                grp.low_model = None
                                print("remove_low_from_group")
                        else:
                            # 否则删除高模
                            for (index, item) in enumerate(grp.high_models):
                                if item.high_model == del_object:
                                    grp.high_models.remove(index)
                                    bpy.data.objects.remove(del_object)
                                    print("remove_high_from_group")
                                    break
                else:
                    if not del_object.users_scene:
                        bpy.data.objects.remove(del_object)
                    print("remove")
            else:
                print("auto_del")


def on_object_select_changed(current_active_object: Object):
    """处理物体模式下，所选物体发生变化的事件"""

    if current_active_object:
        if current_active_object.type != "MESH":
            return
        current_active_object.color = (1, 0, 0, 0.5)
        grp = None
        if current_active_object.group_uuid:
            grp, ignore = get_group_entry(current_active_object.group_uuid)
        if grp:
            is_low = False
            if grp.low_model == current_active_object:
                is_low = True
            show_text_on_object("{}({})".format(grp.name, _("Low-Poly" if is_low else "High-Poly")),
                                current_active_object.name)
        else:
            show_text_on_object(_("Not in any group"), current_active_object.name, (.9, 0, 0, 0.2))
        return
    remove_text(force=True)


def update_group_index(scene: Scene):
    """处理编辑模式下，组索引更新"""
    global index_in_edit
    active_object = bpy.context.object
    if active_object.group_uuid:
        _, index = get_group_entry(active_object.group_uuid)
        if index is not None:
            index_in_edit = index
            scene.object_groups_index = index
            return
    index_in_edit = -2


@persistent
def depsgraph_handler(scene: Scene):
    global index_in_edit, last_object_set, last_object_num, last_active_object, handling
    if bpy.context.mode == 'EDIT_MESH' and index_in_edit != -1:
        update_group_index(scene)
    else:
        index_in_edit = -1
    # 只在物体模式下才能执行如下逻辑
    if bpy.context.mode != "OBJECT":
        return
    if handling:
        return
    handling = True
    # 首先检查所选是否发生变化
    # 最大化的减少耗时函数的执行次数（因为当移动物体时，此函数会每帧执行）
    current_active_object = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if last_active_object != current_active_object:
        current_object_num = len(scene.objects)
        if current_object_num != last_object_num:
            current_object_set = set(scene.objects)
            if last_object_num != 0:  # 确保不是0
                on_object_num_changed(current_object_set)
            last_object_num = current_object_num
            last_object_set = current_object_set
        else:
            on_object_select_changed(current_active_object)
        last_active_object = current_active_object
    elif current_active_object is None:
        operators = bpy.context.window_manager.operators
        if operators and operators[-1].name == 'Delete':
            # 检查是否存在空数据
            for del_object in scene.objects:
                if not del_object.users_scene:
                    bpy.data.objects.remove(del_object)
                    print("first_removed_obj")
    handling = False


def depsgraph_register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)


def depsgraph_unregister():
    if bpy.app.handlers.depsgraph_update_post.count(depsgraph_handler):
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
