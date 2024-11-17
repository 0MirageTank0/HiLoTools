import os

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import AddonPreferences
import rna_keymap_ui

from addons.HiLoTools.config import __addon_name__
from addons.HiLoTools.handler.hotkey_handler import addon_keymaps


class HiLoAddonPreferences(AddonPreferences):
    bl_idname = __addon_name__

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        kc = bpy.context.window_manager.keyconfigs.addon
        for km, kmi in addon_keymaps:
            km = km.active()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
