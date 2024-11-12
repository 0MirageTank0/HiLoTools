import bpy


class OBJECT_UL_object_groups(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0, ):
        obj_group = item
        scene = context.scene
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(obj_group, "is_active", text="",
                     icon="RESTRICT_SELECT_OFF" if obj_group.is_active else
                     "VIS_SEL_11" if scene.active_all else "RESTRICT_SELECT_ON",
                     emboss=False)
            row.prop(obj_group, "group_name", text="", emboss=False)
            if not obj_group.low_model:
                row.label(text="无低模物体", icon='ERROR')
            row.prop(obj_group, "is_visible", text="", emboss=False,
                     icon='HIDE_OFF' if obj_group.is_visible else 'HIDE_ON')
            # 'UNLOCKED')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            row = layout.row()
            row.prop(obj_group, "is_active", text="", icon="RECORD_ON" if obj_group.is_active else "RECORD_OFF",
                     emboss=False)

    def filter_items(self, context, data, propname):
        sorted_array = []
        items = getattr(data, propname)
        # Filter
        if self.filter_name:
            filtered = bpy.types.UI_UL_list.filter_items_by_name(
                self.filter_name,
                self.bitflag_filter_item,
                items,
                propname="group_name",
                reverse=False)
        else:
            filtered = [self.bitflag_filter_item] * len(items)
        if self.use_filter_sort_alpha:
            sorted_array = bpy.types.UI_UL_list.sort_items_by_name(items, propname="group_name")
        return filtered, sorted_array
