import math
import random
import time
from typing import Optional
import bpy
import blf
import gpu
from bpy_extras import view3d_utils
import gpu_extras.batch
from bpy.types import Context, Object
from mathutils import Vector

# 设置全局变量存储文字提示的状态
show_text = False
text_display_time = 1.0  # 显示时间（秒）
start_time = 0
text_position = (0, 0)
handler = None
fontId = 0
gpuShader = gpu.shader.from_builtin('UNIFORM_COLOR')
text_location_in_3d: Vector
credible_location: bool = False


def draw_rect(pos1, pos2, col):
    gpu.state.blend_set('ALPHA')
    gpuShader.bind()
    gpuShader.uniform_float('color', col)
    vpos = (pos1[0], pos1[1]), (pos2[0], pos1[1]), (pos2[0], pos2[1]), (pos1[0], pos2[1])
    gpu_extras.batch.batch_for_shader(gpuShader, type='TRI_FAN', content={'pos': vpos}).draw(gpuShader)


def draw_textbox(fontid, text, second_text, center, margin, bg_color, ):
    txt_w, txt_h = blf.dimensions(fontid, text)
    box_w = txt_w + 2 * margin
    box_h = txt_h + 2 * margin
    cx, cy = center

    cy += margin + txt_h
    # Box
    draw_rect(
        (cx - box_w / 2, cy + box_h / 2),
        (cx + box_w / 2, cy - box_h / 2),
        bg_color,
    )
    # Text
    blf.position(fontid, cx - txt_w / 2, cy - txt_h / 2, 0)
    blf.draw(fontid, text)
    if second_text:
        blf.size(fontid, 20)
        txt_w, txt_h = blf.dimensions(fontid, second_text)
        cy = center[1] - (txt_h + margin)
        box_w = txt_w + 2 * margin
        box_h = txt_h + 2 * margin
        draw_rect(
            (cx - box_w / 2, cy + box_h / 2),
            (cx + box_w / 2, cy - box_h / 2),
            bg_color,
        )
        blf.position(fontid, cx - txt_w / 2, cy - txt_h / 2, 0)
        blf.draw(fontid, second_text)


def draw_callback_px(display_text, display_second_text):
    """绘制文字提示的回调函数"""
    if show_text:
        global credible_location, text_location_in_3d
        if not credible_location:
            text_location_in_3d = get_selected_objects_centroid(bpy.context)
            credible_location = True
        pos = text_location_in_3d
        if pos is None:
            return
        true_text_position = calculate_text_position(bpy.context, pos)

        # 设置文字大小和颜色
        blf.size(fontId, 28)
        blf.shadow_offset(fontId, 1, -1)
        blf.shadow(fontId, 5, .1, .1, .1, 1)
        blf.color(fontId, .9, .9, 1, 1)

        draw_textbox(
            fontid=fontId,
            text=display_text,
            second_text=display_second_text,
            center=true_text_position,
            margin=20,
            bg_color=(.25, .25, .25, .15),
        )
        # blf.size(fontId, 50)
        # DrawTextbox(
        #     fontid=fontId,
        #     text=display_text,
        #     center=text_position,
        #     margin=40,
        #     bg_color=(1, .75, .75, .15),
        # )


def get_object_centroid(obj: Object, sample_size=250) -> Vector:
    """计算网格的质心"""
    mesh: bpy.types.Mesh = obj.data
    world_matrix = obj.matrix_world
    vertices = mesh.vertices

    vertices_num = len(vertices)
    if vertices_num == 0:
        return obj.location
    total_position = Vector((0.0, 0.0, 0.0))
    if vertices_num <= sample_size:
        for vertex in vertices:
            world_vertex = world_matrix @ vertex.co
            total_position += world_vertex
        centroid = total_position / vertices_num
    else:
        sampled_vertices = random.sample(list(vertices), sample_size)
        total_position = Vector((0.0, 0.0, 0.0))
        for vertex in sampled_vertices:
            world_vertex = world_matrix @ vertex.co
            total_position += world_vertex
        centroid = total_position / sample_size

    return centroid


def get_selected_objects_centroid(context: Context, sample_size=250) -> Optional[Vector]:
    # 获取所有选中物体的质心
    selected_objects = context.selected_objects

    if not selected_objects:
        return None

    # 初始化总位置向量和物体计数器
    total_position = Vector((0.0, 0.0, 0.0))
    object_count = len(selected_objects)

    # 计算所有选中物体的质心
    for obj in selected_objects:
        if obj.type != 'MESH':
            continue
        object_centroid = get_object_centroid(obj, sample_size)
        total_position += object_centroid

    # 计算平均位置
    centroid = total_position / object_count

    return centroid


def calculate_text_position(context: Context, obj_location):
    """将3D世界坐标转换为2D屏幕坐标"""
    region = context.region
    rv3d = context.space_data.region_3d
    coord_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, obj_location)
    return coord_2d


def show_text_on_object(display_text, display_second_text):
    """在所选物体的质心位置显示文字提示"""
    global show_text, start_time, text_position, handler, credible_location
    obj = bpy.context.object
    if obj:
        start_time = time.time()
        if show_text:
            return
        # 开始显示文字
        show_text = True
        credible_location = False
        # 添加绘制回调
        handler = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (display_text, display_second_text),
                                                         'WINDOW', 'POST_PIXEL')

        # 设置定时器
        bpy.app.timers.register(remove_text, first_interval=text_display_time)


def remove_text(force=False):
    """隐藏文字提示"""
    global show_text, handler, credible_location
    if force or (time.time() - start_time >= text_display_time):
        if not show_text:
            return
        show_text = False
        credible_location = False
        # 移除绘制回调
        bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        handler = None
        return None  # 停止定时器
    return 0.1  # 持续调用直到时间结束