import os

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import AddonPreferences

from addons.HiLoTools.config import __addon_name__


class ExampleAddonPreferences(AddonPreferences):
    # this must match the add-on name (the folder name of the unzipped file)
    bl_idname = __addon_name__

    # https://docs.blender.org/api/current/bpy.props.html
    # 在 blender 编程运行期间，名称不能动态转换，因为它们是定义的
    # 当类被注册时，即我们需要重新启动 Blender 才能正确翻译属性名称。
    filepath: StringProperty(
        name="Resource Folder",
        default=os.path.join(os.path.expanduser("~"), "Documents", __addon_name__),
        subtype='DIR_PATH',
    )
    number: IntProperty(
        name="Int Config",
        default=2,
    )
    boolean: BoolProperty(
        name="Boolean Config",
        default=False,
    )

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="Add-on Preferences View")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")