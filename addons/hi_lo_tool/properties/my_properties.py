import bpy


class MyProperties(bpy.types.PropertyGroup):
    my_property: bpy.props.StringProperty(
        name="My Property",
        description="A simple string property",
        default="Hello World"
    )


def register():
    bpy.utils.register_class(MyProperties)


def unregister():
    bpy.utils.unregister_class(MyProperties)
