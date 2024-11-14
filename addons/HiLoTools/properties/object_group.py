from typing import List, Tuple, Optional

import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty
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
    model_name: StringProperty(name="Mesh Name", default="No Name")
    low_model: PointerProperty(type=Object, poll=mesh_object_poll,
                               update=update_low_model)
    completion_status: EnumProperty(name="Progress", items=[
        ('Pending', "Pending", "The production of low-poly has not yet begun"),
        ('Ongoing', "Ongoing", "Low poly is in the process of being made"),
        ('Finished', "Finished", "The low-poly has been made"),
    ])
    high_models: CollectionProperty(type=ObjectSubItem)  # 存储多个高模物体


def get_group_entry(uuid) -> Tuple[Optional[ObjectGroup], int]:
    # entry : ObjectGroup
    for (index, entry) in enumerate(bpy.context.scene.object_groups):
        if entry.uuid == uuid:
            return entry, index
    return None, -1


def add_group_entry(group: ObjectGroup):
    return


def del_group_entry(uuid):
    return
