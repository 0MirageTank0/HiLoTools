import bpy
from bpy.types import Object, Scene

from addons.HiLoTools.utils.text_utils import remove_text, show_text_on_object
from addons.HiLoTools.utils.entry_utils import get_group_entry

# 定义事件处理器
last_object_num: int = 0
handling = False
last_active_object: Object
last_objects = set()
index_in_edit = -1


def is_object_valid(obj):
    try:
        _ = obj.name
        return True
    except ReferenceError:
        return False


def on_object_removed(scene: Scene):
    global index_in_edit
    if bpy.context.mode == "EDIT_MESH":
        if index_in_edit == -1:
            active_object = bpy.context.object
            if active_object.group_info:
                _, index = get_group_entry(active_object.group_info)
                if index is not None:
                    index_in_edit = index
                    scene.object_groups_index = index
                else:
                    index_in_edit = -2
        return
    else:
        index_in_edit = -1
    if bpy.context.mode != "OBJECT":
        return
    # 判断是否删除了物体
    global last_object_num, handling, last_objects

    current_object_num = len(scene.objects)
    if current_object_num != last_object_num:
        if handling:
            return
        # 获取当前场景中的所有对象
        current_objects = set(scene.objects)
        if last_object_num == 0:
            last_objects = current_objects
            last_object_num = current_object_num
            return
        handling = True
        # 物体数量变化
        if current_object_num > last_object_num:
            # 检测新添加的对象
            new_object_set = current_objects - last_objects
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
        else:
            del_object_set = last_objects - current_objects
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

        last_object_num = current_object_num
        last_objects = current_objects
        handling = False
    else:
        global last_active_object
        active_object = bpy.context.active_object
        if active_object:
            if active_object.group_info:
                grp, _ = get_group_entry(active_object.group_info)
                if grp:
                    show_text_on_object(grp.group_name, active_object.name)
            else:
                remove_text(True)
        last_active_object = active_object


def depsgraph_register():
    bpy.app.handlers.depsgraph_update_post.append(on_object_removed)


def depsgraph_unregister():
    bpy.app.handlers.depsgraph_update_post.remove(on_object_removed)