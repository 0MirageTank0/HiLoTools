import bpy
from bpy.types import Context, UILayout, Object

from addons.HiLoTools.operators.material_ops import MATRIAL_OT_create_default_material
from addons.HiLoTools.operators.group_ops import OBJECT_OT_add_object_group, OBJECT_OT_remove_object_group, \
    OBJECT_OT_add_object_to_group, OBJECT_OT_remove_object_from_group, OBJECT_OT_rename_group
from addons.HiLoTools.operators.object_ops import OBJECT_OT_generate_low_poly_object
from addons.HiLoTools.operators.selection_ops import OBJECT_OT_select_object
from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry, ObjectSubItem


def draw_in_group_model_button(layout: UILayout, model_object: Object):
    if model_object:
        layout.operator(OBJECT_OT_select_object.bl_idname, text=model_object.name,
                        icon='HIDE_OFF',
                        translate=False).object_name = model_object.name
        layout.operator(OBJECT_OT_remove_object_from_group.bl_idname, text="", icon='X') \
            .object_name = model_object.name
    else:
        layout.label(text="缺失物体", icon='ERROR')
        layout.operator(OBJECT_OT_remove_object_from_group.bl_idname, text="", icon='X') \
            .object_name = ""


class VIEW3D_PT_ObjectGroupsPanel(bpy.types.Panel):
    bl_label = "物体组管理"
    bl_idname = "VIEW3D_PT_object_groups_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '物体组管理'
    bl_order = 0
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene

        if context.mode == 'OBJECT':
            # 添加和删除物体组的按钮
            row = layout.row(align=True)
            row.operator(OBJECT_OT_add_object_group.bl_idname, text="添加物体组")
            row.operator(OBJECT_OT_remove_object_group.bl_idname, text="删除物体组")

            # 显示物体组列表
            layout.template_list("OBJECT_UL_object_groups", "", scene, "object_groups", scene, "object_groups_index", rows=2)

            if scene.display_mode == "transparent":
                if not scene.background_material:
                    box = layout.box()
                    box.label(text="为了使半透正常工作，先初始化背景材质", icon='ERROR')
                    op = box.operator(MATRIAL_OT_create_default_material.bl_idname, text="初始化背景材质")
                    op.high_model = False
                    op.low_model = False
                else:
                    layout.prop(scene, "transparent_ungrouped")

            row = layout.row(align=True)
            if len(scene.object_groups) > 0:
                row.label(text="模式")
                row.prop_enum(scene, "display_mode", "default")
                row.prop_enum(scene, "display_mode", "transparent")
                row.prop_enum(scene, "display_mode", "focus")

            # 显示当前选中的物体组详情
            if 0 <= scene.object_groups_index < len(scene.object_groups):
                obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
                col = layout.column()
                row = col.row(align=True)
                row.label(text="当前组:" + obj_group.group_name)
                row.operator(OBJECT_OT_rename_group.bl_idname, text="组重命名").group_uuid = obj_group.uuid
                box = col.box()
                box.label(text="低模:", icon='SHADING_WIRE')
                low_col = box.column(align=True)
                if not obj_group.low_model:
                    low_col.prop(obj_group, "low_model", text="低模物体")
                    low_col.operator(OBJECT_OT_generate_low_poly_object.bl_idname, text="生成低模物体")
                else:
                    row = low_col.row(align=True)
                    draw_in_group_model_button(row, obj_group.low_model)
                    low_col.prop(obj_group, "completion_status", text="进度")

                if len(obj_group.high_models) <= 1:
                    box = col.box()
                    box.label(text="高模:", icon='SHADING_RENDERED')
                    col = box.column(align=True)
                    if len(obj_group.high_models) == 1:
                        row = col.row(align=True)
                        first_high_model: ObjectSubItem = obj_group.high_models[0]
                        draw_in_group_model_button(row, first_high_model.high_model)
                        # box.separator()

                    col.operator(OBJECT_OT_add_object_to_group.bl_idname, text="添加新高模", icon='ADD')

        else:
            # 显示物体组列表
            col = layout.column()
            col.template_list("OBJECT_UL_object_groups", "", scene, "object_groups", scene, "object_groups_index")
            col.enabled = False
            box = layout.box()
            box.label(text="当前组别")
            if context.object.group_info:
                grp, _ = get_group_entry(context.object.group_info)
                box.label(text=grp.group_name)
                if grp.low_model == context.object:
                    box.label(text="低模物体")
                else:
                    box.label(text="高模物体")
            else:
                box.label(text="未分组")

    def draw_header_preset(self, context):
        layout = self.layout
        layout.label(text="ook1")


class VIEW3D_PT_HighListPanel(bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_object_groups_panel"
    bl_label = "高模物体列表"
    bl_category = "物体组管理"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context: Context):
        scene = context.scene
        if context.mode != 'OBJECT':
            return False
        if len(scene.object_groups) and 0 <= scene.object_groups_index < len(scene.object_groups):
            obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
            if len(obj_group.high_models) <= 1:
                return False
            else:
                return True
        else:
            return False

    def draw(self, context: Context):
        scene = context.scene
        layout = self.layout
        obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
        box = layout.box()
        col = box.column(align=True)
        for (index, sub_item) in enumerate(obj_group.high_models):
            row = col.row(align=True)
            draw_in_group_model_button(row, sub_item.high_model)

        box.operator(OBJECT_OT_add_object_to_group.bl_idname, text="添加新高模", icon='ADD')
