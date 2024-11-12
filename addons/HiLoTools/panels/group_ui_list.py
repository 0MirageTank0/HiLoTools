import bpy


class OBJECT_UL_object_groups(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0, ):
        obj_group = item
        scene = context.scene
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(obj_group, "is_active", text="",
                     icon="RESTRICT_SELECT_OFF" if obj_group.is_active else
                     "RESTRICT_SELECT_ON",
                     emboss=False)
            row.prop(obj_group, "name", text="", emboss=False)
            if not obj_group.low_model:
                row.label(text="", icon='ERROR')
            row.prop(obj_group, "is_visible", text="", emboss=False,
                     icon='HIDE_OFF' if obj_group.is_visible else 'HIDE_ON')
            # 'UNLOCKED')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            row = layout.row()
            row.prop(obj_group, "is_active", text="", icon="RECORD_ON" if obj_group.is_active else "RECORD_OFF",
                     emboss=False)
