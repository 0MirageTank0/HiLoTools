from typing import Tuple, List

import bpy

from addons.HiLoTools.operators.selection_ops import OBJECT_OT_switch_group_selection, OBJECT_OT_hover_select

addon_keymaps: List[Tuple[bpy.types.KeyMap,bpy.types.KeyMapItem]] = []


def key_register():
    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(OBJECT_OT_switch_group_selection.bl_idname,
                                  type='WHEELUPMOUSE', value='PRESS', ctrl=True)
        kmi.properties.selection = 'HIGH'
        addon_keymaps.append((km, kmi))
        # Ctrl + Down
        kmi = km.keymap_items.new(OBJECT_OT_switch_group_selection.bl_idname,
                                  type='WHEELDOWNMOUSE', value='PRESS', ctrl=True)
        kmi.properties.selection = 'LOW'
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        # 添加Alt键绑定
        kmi = km.keymap_items.new(OBJECT_OT_hover_select.bl_idname,
                                  type='LEFT_ALT', value='PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))


def key_unregister():
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
