import bpy


class MyPanel(bpy.types.Panel):
    bl_label = "My Panel"
    bl_idname = "OBJECT_PT_my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'My Addon'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "my_properties")
        layout.operator("object.my_operator")


def register():
    bpy.utils.register_class(MyPanel)


def unregister():
    bpy.utils.unregister_class(MyPanel)
