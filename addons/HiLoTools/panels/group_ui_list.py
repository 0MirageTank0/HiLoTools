import bpy

from addons.HiLoTools.operators.view_ops import OBJECT_OT_solo_group, OBJECT_OT_local_view_group
from addons.HiLoTools.properties.object_group import ObjectGroup


class OBJECT_UL_object_groups(bpy.types.UIList):
    """
    绘制组的列表
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0, ):
        obj_group: ObjectGroup = item
        scene = context.scene
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            if scene.display_mode == 'transparent':
                prop = row.operator(operator=OBJECT_OT_solo_group.bl_idname, text="",
                                    icon='VIS_SEL_11' if obj_group.is_active else 'VIS_SEL_00', emboss=False)
                prop.type = 'TOGGLE'
                prop.group_index = index
            elif scene.display_mode == 'default':
                row.prop(obj_group, 'is_active', text="",
                         icon='RESTRICT_SELECT_OFF' if obj_group.is_active else 'RESTRICT_SELECT_ON', emboss=False)
            elif scene.display_mode == 'focus':
                prop = row.operator(operator=OBJECT_OT_local_view_group.bl_idname, text="",
                                    icon='VIS_SEL_11' if obj_group.is_active else 'VIS_SEL_00', emboss=False)
                prop.type = 'TOGGLE'
                prop.group_index = index
            row.prop(obj_group, 'name', text="", emboss=False)
            if obj_group.name != obj_group.mesh_name:
                mesh_name = row.row()
                mesh_name.enabled = False
                mesh_name.label(text=obj_group.mesh_name)
            if not obj_group.low_model:
                warning_sign = row.row()
                warning_sign.enabled = False
                warning_sign.prop(scene, 'low_exist_warning_sign', icon='ERROR', text="", emboss=False)
            else:
                completion_sign = row.row()
                completion_sign.enabled = False
                if obj_group.completion_status == 'Finished':
                    completion_sign.prop(obj_group, 'completion_status', icon_only=True,
                                         text="", icon='CHECKMARK', emboss=False)
                elif obj_group.completion_status == 'Ongoing':
                    completion_sign.prop(obj_group, 'completion_status', icon_only=True,
                                         text="", icon='SEQ_CHROMA_SCOPE', emboss=False)
            if scene.display_mode != 'focus':
                row.prop(obj_group, 'is_visible', text="", emboss=False,
                         icon='HIDE_OFF' if obj_group.is_visible else 'HIDE_ON')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            row = layout.row()
            row.prop(obj_group, 'is_active', text="", icon='RECORD_ON' if obj_group.is_active else 'RECORD_OFF',
                     emboss=False)
