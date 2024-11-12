import bpy



def on_load_file(scene: bpy.types.Scene):
    pass


def load_register():
    bpy.app.handlers.load_post.append(on_load_file)


def load_unregister():
    bpy.app.handlers.load_post.remove(on_load_file)