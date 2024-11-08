
from typing import Optional
import bpy
from bpy.types import Object, Scene
from addons.HiLoTools.utils.text_utils import remove_text, show_text_on_object
from addons.HiLoTools.utils.entry_utils import get_group_entry

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
            uuid = new_object.group_info
            if uuid:
                # 检查uuid是否存在
                grp, _ = get_group_entry(uuid)
                if not grp:  # 不存在组
                    new_object.group_info = ""
                    print("clear_uuid")
                else:  # 存在组 高模则拷贝
                    h = grp.high_models.add()
                    h.high_model = new_object
                    print("add_to_group")
    # 物体数量变化 删除了对象
    else:
        del_object_set = last_object_set - current_objects_set
        for del_object in del_object_set:
            if is_object_valid(del_object):
                uuid = del_object.group_info
                if uuid:
                    grp, _ = get_group_entry(uuid)
                    # 如果是低模 则删除低模
                    if grp.low_model is not None and (not grp.low_model.users_scene):
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


def on_object_select_changed(current_active_object: Object):
    """处理物体模式下，所选物体发生变化的事件"""
    if current_active_object:
        current_active_object.color = (1,0,0,0.5)
        grp = None
        if current_active_object.group_info:
            grp, _ = get_group_entry(current_active_object.group_info)
        if grp:
            show_text_on_object(grp.group_name, current_active_object.name)
        else:
            show_text_on_object("不属于任何组", current_active_object.name, (.9, 0, 0, 1))
        return
    remove_text(force=True)


def update_group_index(scene: Scene):
    """处理编辑模式下，组索引更新"""
    global index_in_edit
    active_object = bpy.context.object
    if active_object.group_info:
        _, index = get_group_entry(active_object.group_info)
        if index is not None:
            index_in_edit = index
            scene.object_groups_index = index
            return
    index_in_edit = -2


def depsgraph_handler(scene: Scene):
    global index_in_edit, last_object_set, last_object_num, last_active_object, handling
    if bpy.context.mode == "EDIT_MESH" and index_in_edit != -1:
        update_group_index(scene)
    else:
        index_in_edit = -1

    # 只在物体模式下才能执行如下逻辑
    if bpy.context.mode != "OBJECT":
        return
    if handling:
        return
    handling = True

    current_object_set = set(scene.objects)
    current_object_num = len(current_object_set)
    if current_object_num != last_object_num:
        if last_object_num != 0:  # 确保不是0
            on_object_num_changed(current_object_set)
        last_object_num = current_object_num
        last_object_set = current_object_set
    else:
        current_active_object = bpy.context.object
        if last_active_object != current_active_object:
            on_object_select_changed(current_active_object)
        last_active_object = current_active_object
    handling = False


def depsgraph_register():
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)


def depsgraph_unregister():
    if bpy.app.handlers.depsgraph_update_post.count(depsgraph_handler):
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)