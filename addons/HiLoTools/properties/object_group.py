from typing import List, Tuple, Optional

import bpy
from bpy.props import PointerProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty
from bpy.types import Object, Context

from addons.HiLoTools.utils.material_utils import clear_object_material, apply_material_to_object


def mesh_object_poll(_, obj: Object):
    return obj.type == 'MESH' and not obj.group_info


class ObjectSubItem(bpy.types.PropertyGroup):
    high_model: PointerProperty(name="高模物体", type=Object, poll=mesh_object_poll)


class ObjectGroup(bpy.types.PropertyGroup):
    def update_active_object(self, context: Context):
        scene = context.scene
        object_groups: List[ObjectGroup] = scene.object_groups

        # 如果所有is_active都为False，则默认全选
        scene.active_all = not any(grp.is_active for grp in object_groups)

        # 处理背景物体的材质
        set_background_material = scene.display_mode == "transparent" and scene.background_material
        active = self.is_active or scene.active_all

        def set_material(obj):
            obj.hide_select = not active
            if active:
                clear_object_material(obj)
            elif set_background_material:
                apply_material_to_object(obj, scene.background_material)

        if self.low_model:
            set_material(self.low_model)
        for item in self.high_models:
            if item.high_model:
                set_material(item.high_model)

    def update_visible_object(self, context: Context):
        high_models = self.high_models
        for item in high_models:
            if item.high_model:
                item.high_model.hide_viewport = not self.is_visible
        if self.low_model:
            self.low_model.hide_viewport = not self.is_visible

    previous_low_model: PointerProperty(type=Object)  # 用于记录上一个 low_model 对象

    def update_low_model(self, context: Context):
        if self.previous_low_model:
            if self.low_model != self.previous_low_model:
                self.previous_low_model.group_info = ""
                # del self._previous_low_model["group"]
        if self.low_model:
            self.low_model.group_info = self.uuid
            # 如果此时高模预选框里面保存有此时的低模，则清除他
            if context.scene.selected_high_model == self.low_model:
                context.scene.selected_high_model = None
            # self.low_model["group"] = self
        self.previous_low_model = self.low_model

    uuid: StringProperty(name="唯一标识")
    is_active: BoolProperty(name="是否可被选择", default=False, update=update_active_object)
    is_visible: BoolProperty(name="是否可见", default=True, update=update_visible_object)
    group_name: StringProperty(name="组名", default="No Name")
    model_name: StringProperty(name="模型名", default="No Name")
    low_model: PointerProperty(type=Object, poll=mesh_object_poll,
                               update=update_low_model)
    completion_status: EnumProperty(name="完成状态", items=[
        ("pending", "pending", "还没开始"),
        ("ongoing", "ongoing", "正在制作中"),
        ("finished", "finished", "已完成"),
    ])
    high_models: CollectionProperty(name="高模物体组", type=ObjectSubItem)  # 存储多个高模物体


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
