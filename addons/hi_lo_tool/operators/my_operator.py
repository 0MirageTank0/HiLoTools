import bpy


class MyOperator(bpy.types.Operator):
    bl_idname = "object.my_operator"
    bl_label = "My Operator2"

    def execute(self, context):
        scene = context.scene
        self.report({'INFO'}, "My Operator Executed" + scene.my_properties)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MyOperator)


def unregister():
    bpy.utils.unregister_class(MyOperator)
