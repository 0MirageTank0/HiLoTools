import bpy
from bpy.app.handlers import persistent

from addons.HiLoTools.properties.object_group import init_group_dict


@persistent
def on_load_file(scene: bpy.types.Scene):
    init_group_dict()


def load_register():
    bpy.app.handlers.load_post.append(on_load_file)


def load_unregister():
    bpy.app.handlers.load_post.remove(on_load_file)
