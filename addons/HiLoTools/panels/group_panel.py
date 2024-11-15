import bpy
from bpy.types import Context, UILayout, Object

from addons.HiLoTools.operators.group_ops import OBJECT_OT_add_object_group, OBJECT_OT_remove_object_group, \
    OBJECT_OT_add_object_to_group, OBJECT_OT_remove_object_from_group, OBJECT_OT_rename_group, \
    OBJECT_OT_update_group_model_name
from addons.HiLoTools.operators.material_ops import MATRIAL_OT_create_default_material
from addons.HiLoTools.operators.object_ops import OBJECT_OT_generate_low_poly_object
from addons.HiLoTools.operators.selection_ops import OBJECT_OT_select_object
from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry

_ = bpy.app.translations.pgettext


def draw_in_group_model_button(layout: UILayout, model_object: Object):
    """
    绘制在面板中绘制与模型关联的按钮，包含：选择物体、从组中删除物体
    """
    if model_object:
        layout.operator(OBJECT_OT_select_object.bl_idname, text=model_object.name,
                        icon='HIDE_OFF',
                        translate=False).object_name = model_object.name
        layout.operator(OBJECT_OT_remove_object_from_group.bl_idname, text="", icon='X') \
            .object_name = model_object.name
    else:
        layout.label(text="Missing Object", icon='ERROR')
        layout.operator(OBJECT_OT_remove_object_from_group.bl_idname, text="", icon='X') \
            .object_name = ""


class VIEW3D_PT_ObjectGroupsPanel(bpy.types.Panel):
    """
    包含一个组列表的主面板
    """
    bl_label = "HiLoTool"
    bl_idname = 'VIEW3D_PT_object_groups_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HiLoTool"
    bl_order = 0
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene

        if context.mode == 'OBJECT':
            # 添加和删除物体组的按钮
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator(OBJECT_OT_add_object_group.bl_idname, icon='ADD')
            row.operator(OBJECT_OT_remove_object_group.bl_idname, icon='REMOVE')

            # 显示物体组列表
            col.template_list('OBJECT_UL_object_groups', '', scene, 'object_groups', scene, 'object_groups_index',
                              rows=2)

            if scene.display_mode == 'transparent':
                if not scene.background_material:
                    box = col.box()
                    box.label(text="To make the semi-transparent work, initialize the background material first",
                              icon='ERROR')
                    op = box.operator(MATRIAL_OT_create_default_material.bl_idname)
                    op.high_model = False
                    op.low_model = False
                else:
                    col.prop(scene, 'transparent_ungrouped')

            row = col.row(align=True)
            if len(scene.object_groups) > 0:
                row.prop_enum(scene, 'display_mode', 'default')
                row.prop_enum(scene, 'display_mode', 'transparent')
                row.prop_enum(scene, 'display_mode', 'focus')

            # 显示当前选中的物体组详情
            if 0 <= scene.object_groups_index < len(scene.object_groups):
                obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
                col = layout.column()
                row = col.row()
                row.label(text=obj_group.name, translate=False)
                row = row.row(align=True)
                row.alignment = 'RIGHT'
                row.operator(operator=OBJECT_OT_rename_group.bl_idname, icon='GREASEPENCIL').group_uuid = obj_group.uuid
                row.operator(operator=OBJECT_OT_update_group_model_name.bl_idname, icon='FILE_REFRESH', text="")\
                    .group_index = scene.object_groups_index

        elif context.mode == 'EDIT_MESH':
            # 显示物体组列表
            col = layout.column()
            col.template_list('OBJECT_UL_object_groups', '', scene, 'object_groups', scene, 'object_groups_index')
            col.enabled = False
            box = layout.box()
            box.label(text="Current Group")
            if context.object.group_uuid:
                grp, _ = get_group_entry(context.object.group_uuid)
                box.label(text=grp.name, translate=False)
                if grp.low_model == context.object:
                    box.label(text="Low-Poly Object")
                else:
                    box.label(text="High-Poly Object")
            else:
                box.label(text="Unassigned")

    def draw_header_preset(self, context):
        layout = self.layout
        scene = context.scene
        if scene.x_ray and (not scene.high_model_material or not scene.low_model_material):
            row = layout.row()
            row.alert = True
            op = row.operator(MATRIAL_OT_create_default_material.bl_idname)
            op.background = False
        layout.prop(scene, 'x_ray')


class VIEW3D_PT_LowModelPanel(bpy.types.Panel):
    """
    显示低模及相关操作的可折叠子面板
    """
    bl_parent_id = 'VIEW3D_PT_object_groups_panel'
    bl_label = ""
    bl_category = "HiLoTool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 0
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if context.mode == 'OBJECT':
            return 0 <= scene.object_groups_index < len(scene.object_groups)
        return False

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene
        if 0 <= scene.object_groups_index < len(scene.object_groups):
            obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
            low_col = layout.column(align=True)
            if not obj_group.low_model:
                low_col.label(text="Specify Low-Poly Object:")
                low_col.prop(obj_group, 'low_model', text="")
                layout.separator(type='LINE')
                low_col = layout.column(align=True)
                low_col.label(text="Generate from High-Poly:")
                low_col.operator(OBJECT_OT_generate_low_poly_object.bl_idname,
                                 icon='MESH_UVSPHERE')
            else:
                row = layout.row(align=True)
                draw_in_group_model_button(row, obj_group.low_model)
                layout.prop(obj_group, 'completion_status', text="Progress")

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Low-Poly", icon='SHADING_WIRE')

    def draw_header_preset(self, context):
        scene = context.scene
        layout = self.layout
        obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
        if not obj_group.low_model:
            layout.label(text="Unassigned", icon='ERROR')
        else:
            layout.label(text=obj_group.low_model.name, translate=False)


class VIEW3D_PT_HighListPanel(bpy.types.Panel):
    """
    显示高模列表的可折叠子面板
    """
    bl_parent_id = 'VIEW3D_PT_object_groups_panel'
    bl_label = ""
    bl_category = "HiLoTool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_order = 1
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if context.mode == 'OBJECT':
            return 0 <= scene.object_groups_index < len(scene.object_groups)
        return False

    def draw(self, context: Context):
        scene = context.scene
        layout = self.layout
        obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
        col = layout.column(align=True)
        for (index, sub_item) in enumerate(obj_group.high_models):
            row = col.row(align=True)
            draw_in_group_model_button(row, sub_item.high_model)
        # layout.alignment = 'RIGHT'
        row = layout.row()
        row.alignment = 'RIGHT'
        row.operator(OBJECT_OT_add_object_to_group.bl_idname, text="Add New High-Poly", icon='ADD')

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="High-Poly", icon='SHADING_RENDERED')

    def draw_header_preset(self, context):
        scene = context.scene
        layout = self.layout
        obj_group: ObjectGroup = scene.object_groups[scene.object_groups_index]
        i = len(obj_group.high_models)
        if i:
            layout.label(text=_("{} High-Polys").format(i))
        else:
            layout.label(text="No High-Poly")
