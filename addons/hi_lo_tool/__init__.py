import bpy
from addons.hi_lo_tool.addon import register as addon_register
from addons.hi_lo_tool.addon import unregister as addon_unregister

bl_info = {
    "name": "My Blender Addon",
    "blender": (2, 80, 0),
    "category": "Object",
}


def register():
    addon_register()


def unregister():
    addon_unregister()
