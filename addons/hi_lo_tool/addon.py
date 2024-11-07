import bpy

from addons.hi_lo_tool.operators.my_operator import MyOperator
from addons.hi_lo_tool.ui.my_panel import MyPanel,register as my_panel_register, unregister as my_panel_unregister
from addons.hi_lo_tool.properties.my_properties import MyProperties,register as my_properties_register, unregister as my_properties_unregister


def register():
    my_properties_register()
    my_panel_register()

    bpy.utils.register_class(MyOperator)
    bpy.types.Scene.my_properties = bpy.props.StringProperty(name="233")

def unregister():
    my_panel_unregister()
    my_properties_unregister()
    bpy.utils.unregister_class(MyOperator)
    del bpy.types.Scene.my_properties
