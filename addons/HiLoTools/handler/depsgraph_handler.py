from typing import Optional, List

import bpy
from bpy.app.handlers import persistent
from bpy.types import Object, Scene

from addons.HiLoTools.properties.object_group import get_group_entry, ObjectGroup
from addons.HiLoTools.utils.properties_update_utils import next_select_group_index_no_callback
from addons.HiLoTools.utils.text_utils import remove_text, show_text_on_object

_ = bpy.app.translations.pgettext

# 定义事件处理器
last_object_num: int = 0
handling = False
last_selected_objects: List[Object] = []
last_object_set = set()


def is_object_valid(obj):
    try:
        _ = obj.name
        return True
    except ReferenceError:
        return False


def on_object_num_changed(current_objects_set: set):
    """
    处理删除或复制物体的事件.
    如果复制了组中的物体,则清除uuid
    如果删除了组内的物体,则清除关联,清除物体数据,防止0用户数据残留

    """
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
                    if grp.low_model == new_object or any(o.high_model == new_object for o in grp.high_models):
                        # 撤销删除导致的物体增加
                        print("undo del")
                        pass
                    else:
                        # 用户复制粘贴导致物体增加
                        new_object.group_uuid = ""
    # 物体数量变化 删除了对象
    else:
        del_object_set = last_object_set - current_objects_set
        for del_object in del_object_set:
            if is_object_valid(del_object):
                if del_object.type != "MESH":
                    continue
                uuid = del_object.group_uuid
                if uuid:
                    grp, _ = get_group_entry(uuid)
                    # 如果是低模 则删除低模
                    if grp is not None:
                        if grp.low_model:
                            if grp.low_model == del_object and not grp.low_model.users_scene:
                                bpy.data.objects.remove(grp.low_model)
                                grp.low_model = None
                        # 否则删除高模
                        for (index, item) in enumerate(grp.high_models):
                            if item.high_model == del_object:
                                grp.high_models.remove(index)
                                bpy.data.objects.remove(del_object)
                                print("remove_high_from_group")
                else:
                    if not del_object.users_scene:
                        bpy.data.objects.remove(del_object)
                    print("remove")
            else:
                print("auto_del")


def on_object_select_changed(selected_objects: List[Object]):
    """
    处理物体模式下，所选物体发生变化的事件
    如果选择范围仅限于一个组，则显示组名+所选物体
    如果选择范围多个组、或选择了多个无关物体、不在同一个组中的物体，则什么也不做
    如果选择了一个组中的低模或者一个组中的高模，则显示组名（高/低模）+所选物体
    """
    if not selected_objects:
        return
    if any(obj.type != 'MESH' for obj in selected_objects):
        return
    selected_group = None
    selected_group_index = -1
    selection_have_low: bool = False
    selection_have_high: bool = False
    mixed_selection: bool = False
    display_object = None
    for selected_object in selected_objects:
        if selected_object.type != "MESH":
            continue
        selected_object.color = (1, 0, 0, 0.5)
        grp = None
        if selected_object.group_uuid:
            grp, selected_group_index = get_group_entry(selected_object.group_uuid)
        if grp:
            if selected_group is None:
                selected_group = grp
            elif selected_group != grp:
                # 选择了多个组 结束
                mixed_selection = True
                break
            if grp.low_model == selected_object:
                selection_have_low = True
            else:
                selection_have_high = True
        else:
            if len(selected_objects) > 1:
                # 选择了多个不在同一个组内的物体 结束
                mixed_selection = True
                break
            else:
                display_object = selected_object
    # 在显示之前，先清除内容
    remove_text(force=True)
    if mixed_selection:
        return

    scene = bpy.context.scene
    if scene.sync_select:
        next_select_group_index_no_callback()
        scene.object_groups_index = selected_group_index

    if display_object is not None:
        show_text_on_object(_("Not in any group"), display_object.name, (.9, 0, 0, 0.2))
        return

    name_str = ",".join([o.name for o in selected_objects])
    if selection_have_low and selection_have_high:
        show_text_on_object("{}".format(selected_group.name), name_str)
    elif selection_have_low:
        # 只可能有一个低模
        show_text_on_object("{}({})".format(selected_group.name, _("Low-Poly")),
                            selected_objects[0].name)
    elif selection_have_high:
        show_text_on_object("{}({})".format(selected_group.name, _("High-Poly")),
                            name_str)
    return


@persistent
def depsgraph_handler(scene: Scene):
    global last_object_set, last_object_num, last_selected_objects, handling
    # 只在物体模式下才能执行如下逻辑
    if bpy.context.mode != "OBJECT":
        return
    if handling:
        return
    handling = True
    # 首先检查所选是否发生变化
    # 最大化的减少耗时函数的执行次数（因为当移动物体时，此函数会每帧执行）
    selected_objects = bpy.context.selected_objects
    current_selected_objects = selected_objects
    if last_selected_objects != current_selected_objects:
        current_object_num = len(scene.objects)
        if current_object_num != last_object_num:
            current_object_set = set(scene.objects)
            if last_object_num != 0:  # 确保不是0
                on_object_num_changed(current_object_set)
            last_object_num = current_object_num
            last_object_set = current_object_set
        else:
            if scene.print_selected_object:
                on_object_select_changed(selected_objects)
        last_selected_objects = current_selected_objects
    elif current_selected_objects is None:
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
