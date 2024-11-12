import bpy

from bpy.types import Object, Material
from bpy.props import CollectionProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty, StringProperty, \
    FloatVectorProperty

from addons.HiLoTools.properties.object_group import mesh_object_poll, ObjectGroup
from addons.HiLoTools.utils.properties_update_utils import update_background_color, update_high_model_color, \
    update_low_model_color, update_display_mode, \
    update_select_group_index, update_active_all, update_transparent_ungrouped

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
        "transparent_ungrouped": BoolProperty(name="影响组外物体", description="半透不属于任何组的物体",
                                              update=update_transparent_ungrouped),
        "active_all": BoolProperty(name="全部使能", default=True, update=update_active_all),
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
