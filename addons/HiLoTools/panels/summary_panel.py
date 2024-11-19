from typing import Dict

import bpy

from addons.HiLoTools.operators.group_ops import GROUP_OT_select_group
from addons.HiLoTools.operators.object_ops import OBJECT_OT_update_model_name, OBJECT_OT_move_to_collection
from addons.HiLoTools.operators.selection_ops import OBJECT_OT_select_all_group, OBJECT_OT_select_ungrouped_objects, \
    OBJECT_OT_select_object, OBJECT_OT_select_remark_group, OBJECT_OT_select_group

_ = bpy.app.translations.pgettext


class VIEW3D_PT_SummaryPanel(bpy.types.Panel):
    """
    汇总面板,对当前工程的总览信息
    """
    bl_label = "Summary"
    bl_category = "HiLoTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='IMGDISPLAY')

    def draw(self, context):
        scene = context.scene
        obj_name_set = set()
        layout = self.layout

        layout.operator(operator=OBJECT_OT_update_model_name.bl_idname, icon='FILE_REFRESH',
                        text="Updated all object names")
        layout.operator(operator=OBJECT_OT_move_to_collection.bl_idname, icon='OUTLINER_COLLECTION')

        remark_area = layout.column()
        low_area = layout.column()
        high_area = layout.column()

        has_any_remark: bool = False
        has_any_low: bool = False
        has_any_high: bool = False
        for grp in scene.object_groups:
            if has_any_high and has_any_low and has_any_remark:
                break
            if not has_any_low and grp.low_model:
                has_any_low = True
                low_area = low_area.box()
                title_row = low_area.row()
                title_row.prop(scene, 'show_low_model_summary', emboss=False, text="All Low-Poly",
                               icon='SHADING_WIRE' if scene.show_low_model_summary else 'DOWNARROW_HLT')
                title_row.operator(operator=OBJECT_OT_select_all_group.bl_idname,
                                   text="Select All").select_range = 'LOW'
                if scene.show_low_model_summary:
                    low_area.separator(type='LINE')
            if not has_any_high and grp.high_models:
                for h in grp.high_models:
                    if h.high_model:
                        has_any_high = True
                        high_area = high_area.box()
                        title_row = high_area.row()
                        title_row.prop(scene, 'show_high_model_summary', emboss=False, text="All High-Poly",
                                       icon='SHADING_RENDERED' if scene.show_high_model_summary else 'DOWNARROW_HLT')
                        title_row.operator(operator=OBJECT_OT_select_all_group.bl_idname,
                                           text="Select All").select_range = 'HIGH'
                        if scene.show_high_model_summary:
                            high_area.separator(type='LINE')
                        break
            if not has_any_remark and grp.remark:
                has_any_remark = True
                remark_area = remark_area.box()
                title_row = remark_area.row()
                title_row.prop(scene, 'show_remark_group_summary', emboss=False, text="All Remarked Group",
                               icon='TEXT' if scene.show_remark_group_summary else 'DOWNARROW_HLT')
                if scene.show_remark_group_summary:
                    remark_area.separator(type='LINE')
                    remark_area = remark_area.column(align=True)

        if not has_any_remark:
            remark_area.label(text="No Remarked Group", icon='TEXT')
        if not has_any_low:
            low_area.label(text="No Low-Poly Exist", icon='SHADING_WIRE')
        if not has_any_high:
            high_area.label(text="No High-Poly Exist", icon='SHADING_RENDERED')

        remark_group: Dict[str, bpy.types.UILayout] = {}

        for grp in scene.object_groups:

            if scene.show_remark_group_summary and grp.remark:
                group_area = remark_group.get(grp.remark)
                if not group_area:
                    group_area = remark_area.box()
                    group_area = group_area.column(align=True)
                    title_row = group_area.row()
                    title_row.label(text=grp.remark)
                    title_row.operator(operator=OBJECT_OT_select_remark_group.bl_idname,
                                       text="Select All").remark = grp.remark
                    # group_area.separator(type='SPACE')
                    group_area = group_area.column(align=True)
                    remark_group[grp.remark] = group_area
                line = group_area.row()
                line.alignment = 'LEFT'
                line.operator(operator=GROUP_OT_select_group.bl_idname,
                              emboss=False, icon='DOT',
                              text=grp.name).group_uuid = grp.uuid

            has_high_in_group: bool = False
            single_group = high_area
            if scene.show_high_model_summary and len(grp.high_models) > 1:
                single_group = high_area.box()
            for h in grp.high_models:
                if h.high_model:
                    has_high_in_group = True
                    if not scene.show_high_model_summary:
                        break
                    h_name = h.high_model.name
                    row = single_group.row()
                    row.alignment = 'LEFT'
                    row.operator(OBJECT_OT_select_object.bl_idname,
                                 text=h.high_model.name,
                                 translate=False, emboss=False).object_name = h_name
            if scene.show_low_model_summary:
                if has_any_low:
                    row = low_area.row()
                    if grp.low_model:
                        l_name = grp.low_model.name
                        left_part = row.row()
                        left_part.alignment = 'LEFT'
                        left_part.operator(OBJECT_OT_select_object.bl_idname,
                                           text=l_name,
                                           translate=False, emboss=False).object_name = l_name
                        # row.label(text=l_name, translate=False)
                        right_part = row.row()
                        right_part.alignment = 'RIGHT'
                        right_part.prop(grp, 'completion_status', text="", emboss=False, icon_only=True,
                                        icon='BLANK1' if grp.completion_status == 'Pending' else
                                        'MOD_REMESH' if grp.completion_status == 'Ongoing' else 'CHECKMARK')

                    else:
                        if has_high_in_group:
                            row.alert = True
                            row.operator(operator=GROUP_OT_select_group.bl_idname,
                                         text=_("{} Has HighPoly But No LowPoly").format(grp.name),
                                         icon='ERROR').group_uuid = grp.uuid
        layout.separator(type='LINE')
        empty = True
        for obj in scene.objects:
            if obj.type == 'MESH':
                if not obj.group_uuid:
                    obj_name_set.add(obj.name)
                    empty = False
        if empty:
            layout.label(text="No Ungrouped Objects Exist", icon='SHADING_SOLID')
        else:
            box = layout.box()
            row = box.row()
            row.prop(scene, 'show_unassigned_model_summary', emboss=False, text="Ungrouped Objects",
                     icon='SHADING_SOLID' if scene.show_unassigned_model_summary else 'DOWNARROW_HLT')
            row.operator(operator=OBJECT_OT_select_ungrouped_objects.bl_idname, text="Select All")
            if scene.show_unassigned_model_summary:
                box.separator(type='LINE')
                for obj_name in obj_name_set:
                    row = box.row()
                    row.label(text=obj_name, translate=False)
                    row.operator(OBJECT_OT_select_object.bl_idname,
                                 text="", icon='RESTRICT_SELECT_OFF',
                                 translate=False, emboss=False).object_name = obj_name
