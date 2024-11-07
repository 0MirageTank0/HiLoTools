import bpy
from bpy.types import Object


def create_material(name, color=(1.0, 0.0, 0.0, 1.0)):
    """
    创建一个新的材质并设置其颜色。

    :param name: 材质的名称
    :param color: 材质的颜色 (R, G, B, A)，默认为红色
    :return: 创建的材质对象
    """
    # 检查是否存在同名材质，如果存在则返回已存在的材质
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = color
    material.preview_render_type = 'FLAT'
    material.use_nodes = False
    return material


# 定义将材质应用到物体的函数
def apply_material_to_object(obj: Object, material):
    if not obj.data.materials:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material
