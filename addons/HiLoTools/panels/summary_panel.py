import bpy

from addons.HiLoTools.operators.selection_ops import OBJECT_OT_select_all_group, OBJECT_OT_select_ungrouped_objects, \
    OBJECT_OT_select_object
from addons.HiLoTools.properties.object_group import ObjectGroup


class VIEW3D_PT_SummaryPanel(bpy.types.Panel):
    bl_label = "汇总"
    bl_category = "物体组管理"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        scene = context.scene
        obj_name_set = set()
        layout = self.layout

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
                title_row.label(text=f"全部低模", icon="SHADING_WIRE")
                title_row.operator(operator=OBJECT_OT_select_all_group.bl_idname, text="选择全部").select_range = "LOW"
                low_area.separator(type="LINE")
            if not has_any_high and grp.high_models:
                for h in grp.high_models:
                    if h.high_model:
                        has_any_high = True
                        high_area = high_area.box()
                        title_row = high_area.row()
                        title_row.label(text=f"全部高模", icon="SHADING_RENDERED")
                        title_row.operator(operator=OBJECT_OT_select_all_group.bl_idname, text="选择全部").select_range = "HIGH"
                        high_area.separator(type="LINE")
                        break
        if not has_any_low:
            low_area.label(text=f"不存在低模物体", icon="SHADING_WIRE")
        if not has_any_high:
            high_area.label(text=f"不存在高模物体", icon="SHADING_RENDERED")

        for grp in scene.object_groups:
            has_high_in_group: bool = False
            for h in grp.high_models:
                if h.high_model:
                    has_high_in_group = True
                    h_name = h.high_model.name
                    row = high_area.row()
                    row.prop(h.high_model, "name", text="", emboss=False)
                    row.operator(OBJECT_OT_select_object.bl_idname,
                                 text="", icon='RESTRICT_SELECT_OFF', translate=False).object_name = h_name
            if has_any_low:
                row = low_area.row()
                if grp.low_model:
                    l_name = grp.low_model.name
                    row.alert = grp.completion_status != "finished"
                    row.label(text=l_name, translate=False)
                    if row.alert:
                        row.label(text=grp.completion_status)
                    else:
                        row.label(icon="CHECKMARK", text="")
                    row.operator(OBJECT_OT_select_object.bl_idname,
                                 text="", icon='RESTRICT_SELECT_OFF', translate=False).object_name = l_name
                else:
                    if has_high_in_group:
                        row.alert = True
                        row.label(text=f"{grp.name}组 存在高模但无低模",icon='ERROR')

        # if any(grp.low_model for grp in scene.object_groups):
        #     box = layout.box()
        #     row = box.row()
        #     row.label(text=f"低模", icon="SHADING_WIRE")
        #     row.operator(operator=OBJECT_OT_select_all_group.bl_idname, text="选择全部").select_range = "LOW"
        #     box.separator(type="LINE")
        #     for grp in scene.object_groups:
        #         if grp.low_model:
        #             l_name = grp.low_model.name
        #             row = box.row()
        #             row.alert = grp.completion_status != "finished"
        #             row.label(text=l_name, translate=False)
        #             if row.alert:
        #                 row.label(text=grp.completion_status)
        #             else:
        #                 row.label(icon="CHECKMARK", text="")
        #             row.operator(OBJECT_OT_select_object.bl_idname,
        #                          text="", icon='RESTRICT_SELECT_OFF', translate=False).object_name = l_name
        #
        # else:
        #     layout.label(text=f"不存在低模物体", icon="SHADING_WIRE")
        # if any(grp.high_models for grp in scene.object_groups):
        #     box = layout.box()
        #     row = box.row()
        #     row.label(text=f"高模", icon="SHADING_RENDERED")
        #     row.operator(operator=OBJECT_OT_select_all_group.bl_idname, text="选择全部").select_range = "HIGH"
        #     box.separator(type="LINE")
        #     for grp in scene.object_groups:
        #         for h in grp.high_models:
        #             if h.high_model:
        #                 h_name = h.high_model.name
        #                 row = box.row()
        #                 row.prop(h.high_model, "name", text="", emboss=False)
        #                 row.operator(OBJECT_OT_select_object.bl_idname,
        #                              text="",icon='RESTRICT_SELECT_OFF', translate=False).object_name = h_name
        # else:
        #     layout.label(text=f"不存在高模物体", icon="SHADING_RENDERED")

        layout.separator(type="LINE")
        empty = True
        for obj in scene.objects:
            if obj.type == "MESH":
                if not obj.group_uuid:
                    obj_name_set.add(obj.name)
                    empty = False
        if empty:
            layout.label(text="不存在未分组的物体", icon="SHADING_SOLID")
        else:
            box = layout.box()
            row = box.row()
            row.label(text=f"未分组的物体")
            row.operator(operator=OBJECT_OT_select_ungrouped_objects.bl_idname, text="选择全部")
            box.separator(type="LINE")
            for obj_name in obj_name_set:
                box.label(text=obj_name, translate=False)
