import bpy

from bpy.types import Object, Material
from bpy.props import CollectionProperty, IntProperty, PointerProperty, EnumProperty, BoolProperty, StringProperty, \
    FloatVectorProperty

from addons.HiLoTools.properties.object_group import mesh_object_poll, ObjectGroup
from addons.HiLoTools.utils.properties_update_utils import update_background_color, update_high_model_color, \
    update_low_model_color, update_display_mode, \
    update_select_group_index, update_x_ray, update_transparent_ungrouped

addon_properties = {
    bpy.types.Scene: {
        "property_name": StringProperty(name="property_name"),
        "object_groups": CollectionProperty(type=ObjectGroup),
        "object_groups_index": IntProperty(name="Current Selected Group Index", update=update_select_group_index),
        "selected_high_model": PointerProperty(name="High-Poly Object",
                                               description="Select an object to add as a high-poly to this group.\n"
                                                           "(Note: Automatically filter non-mesh and objects already "
                                                           "in other groups)",
                                               type=Object, poll=mesh_object_poll),
        "display_mode": EnumProperty(name="Display Mode",
                                     items=[
                                         ('default', "Default", "Default option, no special effect"),
                                         ('focus', "Focus", "Switch to the local view of the group"),
                                         ('transparent', "Semi-Transparent", "Make other groups transparent")
                                     ],
                                     update=update_display_mode),
        "transparent_ungrouped": BoolProperty(name="Affects Out-Of-Group",
                                              description="Translucent: All objects that do not belong to any group",
                                              update=update_transparent_ungrouped),
        "x_ray": BoolProperty(name="X Ray",
                              description="X-ray fluoroscopy of the currently active group is used to more clearly see "
                                          "the shape difference between low and high poly",
                              update=update_x_ray),
        "low_suffix": StringProperty(name="Low-Poly Mesh Suffix", default="_low"),
        "high_suffix": StringProperty(name="High-Poly Mesh Suffix", default="_high"),
        "background_material": PointerProperty(name="Background Material",
                                               description="Material used for inactive objects in Semi-Transparent mode"
                                                           ", which is only used for plug-in visuals "
                                                           "and should not be exported for production purposes",
                                               type=Material),
        "background_color": FloatVectorProperty(name="Background Color", subtype='COLOR', min=0, max=1, size=4,
                                                default=(0, 0, 0, 1), update=update_background_color),
        "high_model_material": PointerProperty(name="X-Ray High-Poly",
                                               description="Material used for high-poly objects in X-Ray mode, "
                                                           "which is only used for plug-in visuals "
                                                           "and should not be exported for production purposes",
                                               type=Material),
        "high_model_color": FloatVectorProperty(name="X-Ray High-Poly Color", subtype='COLOR', min=0, max=1, size=4,
                                                default=(0, 0, 0, 1), update=update_high_model_color),
        "low_model_material": PointerProperty(name="X-Ray Low-Poly",
                                              description="Material used for low-poly objects in X-Ray mode, "
                                                          "which is only used for plug-in visuals "
                                                          "and should not be exported for production purposes",
                                              type=Material),
        "low_model_color": FloatVectorProperty(name="X-Ray Low-Poly Color", subtype='COLOR', min=0, max=1, size=4,
                                               default=(0, 0, 0, 1), update=update_low_model_color),
        "sync_select": BoolProperty(name="Sync Selection",
                                    description="Synchronizes the active group to the currently selected",
                                    default=False),
        "show_remark_group_summary": BoolProperty(name="All Remarked Group",
                                                  description="All groups that contain remark.\n"
                                                              "(click to toggle the folding status)", default=True),
        "show_high_model_summary": BoolProperty(name="All High-Poly",
                                                description="All groups of high-poly.\n"
                                                            "(click to toggle the folding status)", default=True),
        "show_low_model_summary": BoolProperty(name="All Low-Poly",
                                               description="All groups of low-poly.\n"
                                                           "(click to toggle the folding status)", default=True),
        "show_unassigned_model_summary": BoolProperty(name="Ungrouped Objects",
                                                      description="All ungrouped objects.\n"
                                                                  "(click to toggle the folding status)", default=True),
        "low_exist_warning_sign": BoolProperty(name="Low-Poly does not exist")
    },
    bpy.types.Object: {
        "group_uuid": StringProperty(name="UUID",
                                     description="Warning: Do not modify this value. This value is used to quickly "
                                                 "determine the object's affiliation without having to iterate "
                                                 "through the contents of the entire group for matching"),
    }
}
