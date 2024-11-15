import bpy

from addons.HiLoTools.config import __addon_name__
from addons.HiLoTools.handler.depsgraph_handler import depsgraph_register, depsgraph_unregister
from addons.HiLoTools.handler.load_handler import load_register, load_unregister
from addons.HiLoTools.handler.tab_handler import tab_register, tab_unregister
from addons.HiLoTools.i18n.dictionary import dictionary
from addons.HiLoTools.operators.selection_ops import OBJECT_OT_switch_group_selection, OBJECT_OT_hover_select
from addons.HiLoTools.properties.properties import addon_properties
from common.class_loader import auto_load
from common.class_loader.auto_load import add_properties, remove_properties
from common.i18n.dictionary import common_dictionary
from common.i18n.i18n import load_dictionary

# Add-on info
bl_info = {
    "name": "Basic Add-on Sample",
    "author": "[You name]",
    "blender": (3, 5, 0),
    "version": (0, 0, 1),
    "description": "This is a template for building addons",
    "warning": "",
    "doc_url": "[documentation url]",
    "tracker_url": "[contact email]",
    "support": "COMMUNITY",
    "category": "3D View"
}

addon_keymaps = []


def key_register():
    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(OBJECT_OT_switch_group_selection.bl_idname, type='WHEELUPMOUSE', value='PRESS',
                                  ctrl=True)
        kmi.properties.selection = 'HIGH'
        addon_keymaps.append((km, kmi))
        # 绑定Ctrl + Down为查找最小值
        kmi = km.keymap_items.new(OBJECT_OT_switch_group_selection.bl_idname, 'WHEELDOWNMOUSE', 'PRESS', ctrl=True)
        kmi.properties.selection = 'LOW'
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        # 添加Alt键绑定
        kmi = km.keymap_items.new(OBJECT_OT_hover_select.bl_idname, 'LEFT_ALT', 'PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))


def key_unregister():
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    print("registering")
    # Register classes
    auto_load.init()
    auto_load.register()
    add_properties(addon_properties)

    # Internationalization
    load_dictionary(dictionary)
    try:
        bpy.app.translations.register(__addon_name__, common_dictionary)
    except ValueError:
        print("发生了错误..")

    key_register()
    tab_register()
    load_register()
    depsgraph_register()
    print("{} addon is installed.".format(bl_info["name"]))


def unregister():
    # Internationalization
    bpy.app.translations.unregister(__addon_name__)
    # unRegister classes
    auto_load.unregister()
    remove_properties(addon_properties)
    key_unregister()
    tab_unregister()
    load_unregister()
    depsgraph_unregister()
    print("{} addon is uninstalled.".format(bl_info["name"]))
