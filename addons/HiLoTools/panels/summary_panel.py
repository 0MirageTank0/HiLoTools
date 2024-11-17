import bpy

from addons.HiLoTools.operators.group_ops import GROUP_OT_select_group
from addons.HiLoTools.operators.object_ops import OBJECT_OT_update_model_name, OBJECT_OT_move_to_collection
from addons.HiLoTools.operators.selection_ops import OBJECT_OT_select_all_group, OBJECT_OT_select_ungrouped_objects, \
    OBJECT_OT_select_object, OBJECT_OT_select_group

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

        low_area = layout.column()
        high_area = layout.column()

        has_any_low: bool = False
        has_any_high: bool = False
        for grp in scene.object_groups:
            if has_any_high and has_any_low:
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
        if not has_any_low:
            low_area.label(text="No Low-Poly Exist", icon='SHADING_WIRE')
        if not has_any_high:
            high_area.label(text="No High-Poly Exist", icon='SHADING_RENDERED')

        for grp in scene.object_groups:
            has_high_in_group: bool = False
            for h in grp.high_models:
                if h.high_model:
                    has_high_in_group = True
                    if not scene.show_high_model_summary:
                        break
                    h_name = h.high_model.name
                    row = high_area.row()
                    row.label(text=h.high_model.name, translate=False)
                    row.operator(OBJECT_OT_select_object.bl_idname,
                                 text="", icon='RESTRICT_SELECT_OFF',
                                 translate=False, emboss=False).object_name = h_name
            if scene.show_low_model_summary:
                if has_any_low:
                    row = low_area.row()
                    if grp.low_model:
                        l_name = grp.low_model.name
                        alert = grp.completion_status != 'Finished'
                        row.alert = alert
                        row.label(text=l_name, translate=False)
                        row.alert = False
                        row.prop(grp, 'completion_status', text="", emboss=False,
                                 icon='ERROR' if grp.completion_status == 'Pending' else
                                 'MOD_REMESH' if grp.completion_status == 'Ongoing' else 'CHECKMARK')
                        row.operator(OBJECT_OT_select_object.bl_idname,
                                     text="", icon='RESTRICT_SELECT_OFF',
                                     translate=False, emboss=False).object_name = l_name
                    else:
                        if has_high_in_group:
                            row.alert = True
                            row.operator(operator=GROUP_OT_select_group.bl_idname,
                                         text=_("{} Has HighPoly But No LowPoly").format(grp.name),
                                         icon='ERROR', emboss=False).group_uuid = grp.uuid
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
