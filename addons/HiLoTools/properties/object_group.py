"""
物体组结构
最核心的结构,高低模配对的数据基础
"""
import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty
from typing import Tuple, Optional
from bpy.types import Object, Context

from addons.HiLoTools.utils.group_utils import set_attribute_for_group


def mesh_object_poll(_, obj: Object):
    return obj.type == 'MESH' and not obj.group_uuid


class ObjectSubItem(bpy.types.PropertyGroup):
    high_model: PointerProperty(name="High-Poly", type=Object, poll=mesh_object_poll)


class ObjectGroup(bpy.types.PropertyGroup):
    def update_active_object(self, context: Context):
        set_attribute_for_group(self, 'hide_select', not self.is_active)

    def update_visible_object(self, context: Context):
        set_attribute_for_group(self, 'hide_viewport', not self.is_visible)

    def update_low_model(self, context: Context):
        if self.low_model:
            self.low_model.group_uuid = self.uuid

    name: StringProperty(default="No Name")
    uuid: StringProperty()
    is_active: BoolProperty(name="Active", default=True, update=update_active_object)
    is_visible: BoolProperty(name="Visible", default=True, update=update_visible_object)
    in_background_material: BoolProperty(default=False)
    in_x_ray_material: BoolProperty(default=False)
    model_name: StringProperty(name="Mesh Name", default="No Name")
    low_model: PointerProperty(type=Object, poll=mesh_object_poll,
                               update=update_low_model)
    completion_status: EnumProperty(name="Progress", items=[
        ('Pending', "Pending", "The production of low-poly has not yet begun"),
        ('Ongoing', "Ongoing", "Low poly is in the process of being made"),
        ('Finished', "Finished", "The low-poly has been made"),
    ])
    high_models: CollectionProperty(type=ObjectSubItem)  # 存储多个高模物体


group_cache: dict = {}


def init_group_dict():
    group_cache.clear()
    for (index, entry) in enumerate(bpy.context.scene.object_groups):
        group_cache[entry.uuid] = index


# def get_group_entry(uuid) -> Tuple[Optional[ObjectGroup], int]:
#     # entry : ObjectGroup
#     group_cache.get(uuid)
#     for (index, entry) in enumerate(bpy.context.scene.object_groups):
#         if entry.uuid == uuid:
#             return entry, index
#     return None, -1


def get_group_index(uuid) -> int:
    return group_cache.get(uuid, -1)


inited: bool = False


def get_group_entry(uuid) -> Tuple[Optional[ObjectGroup], int]:
    global inited
    index = get_group_index(uuid)
    if index != -1:
        return bpy.context.scene.object_groups[index], index
    elif not inited:
        inited = True
        init_group_dict()
        return get_group_entry(uuid)
    return None, -1


def add_group_entry(group: ObjectGroup):
    group_cache[group.uuid] = len(bpy.context.scene.object_groups) - 1
    return


def del_group_entry(uuid):
    init_group_dict()
    return
