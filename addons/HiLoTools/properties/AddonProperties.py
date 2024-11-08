import bpy

from bpy.types import Object, Context, Material
from bpy.props import CollectionProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty, StringProperty, \
    FloatVectorProperty
from typing import List

from addons.HiLoTools.utils.properties_update_utils import update_background_color, update_high_model_color, \
    update_low_model_color, update_display_mode, \
    update_select_group_index
from addons.HiLoTools.utils.material_utils import apply_material_to_object, clear_material


def mesh_object_poll(_, obj: Object):
    return obj.type == 'MESH' and not obj.group_info


class ObjectSubItem(bpy.types.PropertyGroup):
    high_model: PointerProperty(name="高模物体", type=Object, poll=mesh_object_poll)


# 定义一个类来存储多对一的物体组
class ObjectGroup(bpy.types.PropertyGroup):
    def update_active_object(self, context: Context):
        scene = context.scene
        object_groups: List[ObjectGroup] = scene.object_groups
        scene.active_all = False
        # 如果所有is_active都为False，则默认全选
        if not any(obj.is_active for obj in object_groups):
            scene.active_all = True
        if scene.display_mode != "transparent" or not scene.background_material:
            # 如果背景材质为空，则不处理
            return

        # 对所有物体设置背景材质
        if scene.transparent_ungrouped:
            for obj in scene.objects:
                obj.hide_select = True
                apply_material_to_object(self.low_model, scene.background_material)
        # 如果当前被取消active，则设置为背景材质
        if not (self.is_active or scene.active_all):
            # 如果已经对所有物体进行了设置背景材质，则无需再次设置
            if not scene.transparent_ungrouped:
                if self.low_model:
                    self.low_model.hide_select = True
                    apply_material_to_object(self.low_model, scene.background_material)
                for item in self.high_models:
                    if item.high_model:
                        item.high_model.hide_select = True
                        apply_material_to_object(item.high_model, scene.background_material)
        else:  # 否则 清除材质
            if self.low_model:
                self.low_model.hide_select = False
                clear_material(self.low_model)
            for item in self.high_models:
                if item.high_model:
                    item.high_model.hide_select = False
                    clear_material(item.high_model)

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
    is_locked: BoolProperty(name="是否锁定高模", default=False)
    is_visible: BoolProperty(name="是否可见", default=True, update=update_visible_object)
    group_name: StringProperty(name="组名", default="No Name")
    model_name: StringProperty(name="模型名", default="No Name")
    low_model: PointerProperty(type=Object, poll=mesh_object_poll,
                               update=update_low_model)
    high_models: CollectionProperty(name="高模物体组", type=ObjectSubItem)  # 存储多个高模物体 


addon_properties = {
    bpy.types.Scene: {
        "property_name": StringProperty(name="property_name"),
        "object_groups": CollectionProperty(type=ObjectGroup),
        "object_groups_index": IntProperty(name="当前选取组索引", update=update_select_group_index),
        "selected_high_model": PointerProperty(type=Object, poll=mesh_object_poll),
        "show_high_model_panel": BoolProperty(name="显示高模列表", default=False),
        "display_mode": EnumProperty(name="使能模式",
                                     items=[
                                         ("default", "默认", "选择活动组"),
                                         ("focus", "聚焦", "切换到组的局部视图"),
                                         ("transparent", "半透其他", "将无关组透明")
                                     ],
                                     update=update_display_mode),
        "transparent_ungrouped": BoolProperty(name="影响组外物体",description="半透将同样影响不属于任何组的物体"),
        "active_all": BoolProperty(name="全部使能", default=True),
        "low_suffix": StringProperty(name="低模后缀", default="_low"),
        "high_suffix": StringProperty(name="高模后缀", default="_high"),
        "background_material": PointerProperty(name="背景材质", type=Material),
        "background_color": FloatVectorProperty(name="背景颜色", subtype='COLOR', min=0, max=1, size=4,
                                                default=(0, 0, 0, 1), update=update_background_color),
        "high_model_material": PointerProperty(name="高模材质", type=Material),
        "high_model_color": FloatVectorProperty(name="高模颜色", subtype='COLOR', min=0, max=1, size=4,
                                                default=(0, 0, 0, 1), update=update_high_model_color),
        "low_model_material": PointerProperty(name="低模材质", type=Material),
        "low_model_color": FloatVectorProperty(name="低模颜色", subtype='COLOR', min=0, max=1, size=4,
                                               default=(0, 0, 0, 1), update=update_low_model_color),

    },
    bpy.types.Object: {
        "group_info": StringProperty(name="UUID"),
    }
}