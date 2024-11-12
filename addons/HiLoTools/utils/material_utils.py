import bpy
from bpy.types import Object, Material, Scene


def create_material(name, color=(1.0, 0.0, 0.0, 1.0), override=False):
    """
    创建一个新的材质并设置其颜色。
    如果存在则返回已存在的材质
    :param name: 材质的名称
    :param color: 材质的颜色 (R, G, B, A)，默认为红色
    :param override: 如果存在，是否覆盖
    :return: 创建的材质对象
    """
    # 检查是否存在同名材质，
    material: Material
    if name in bpy.data.materials:
        material = bpy.data.materials[name]
        if not override:
            return material
    else:
        material = bpy.data.materials.new(name=name)
    material.diffuse_color = color
    material.preview_render_type = 'FLAT'
    material.use_nodes = False
    return material


def apply_material_to_object(obj: Object, material):
    """将材质应用到物体"""
    if not obj.data.materials:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material


def clear_object_material(obj: Object):
    """清除物体的所有材质"""
    obj.data.materials.clear()