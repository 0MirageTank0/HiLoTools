import uuid
from typing import List

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Context, Object

from addons.HiLoTools.operators.object_ops import OBJECT_OT_update_model_name
from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry, add_group_entry, del_group_entry
from addons.HiLoTools.utils.material_utils import clear_object_material

_ = bpy.app.translations.pgettext


class OBJECT_OT_add_object_group(Operator):
    """
    创建一个组(操作会弹出用户窗口)

    参数:
        name: 组名
        mesh_name: 网格名称(作为网格重命名时的前缀)
        separate_grouping: 是否独立分组
    """
    bl_idname = 'object.add_object_group'
    bl_label = "Add Group"
    bl_description = "Create a new group with the selected objects as the High-Poly of the new group"

    def update_group_name(self, _):
        self.mesh_name = self.name

    name: StringProperty(name="Group Name",
                         description="The display name of this group, which does not affect the actual name of the "
                                     "object",
                         default="New Group",
                         update=update_group_name,
                         options={'SKIP_SAVE'})
    mesh_name: StringProperty(name="Mesh Name",
                              description="A prefix that denotes both low-poly and high-poly objects, "
                                          "which works when renaming",
                              options={'SKIP_SAVE'})
    separate_grouping: BoolProperty(name="Separate grouping",
                                    description="Place each selected object individually in a different new group")

    def execute(self, context: Context):
        scene = context.scene
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH' and not obj.group_uuid]

        def create_group(group_name, mesh_name, high_models: List[Object]):
            obj_group: ObjectGroup = scene.object_groups.add()
            obj_group.name = group_name
            obj_group.mesh_name = mesh_name
            obj_group.uuid = str(uuid.uuid4())
            add_group_entry(obj_group)
            for sub_obj in high_models:
                sub_item = obj_group.high_models.add()
                sub_item.high_model = sub_obj
                sub_obj.group_uuid = obj_group.uuid

        if not self.separate_grouping:
            if len(selected_objects) == 0:
                self.mesh_name = self.name
            create_group(self.name, self.mesh_name, selected_objects)
        else:
            for high_model in selected_objects:
                grp_name = high_model.name.rsplit("_", 1)[0]
                create_group(grp_name, grp_name, [high_model])

        scene.object_groups_index = len(scene.object_groups) - 1

        self.report({'INFO'}, "Object group added")
        return {'FINISHED'}

    def invoke(self, context, event):
        for obj in context.selected_objects:
            if obj.type == 'MESH' and not obj.group_uuid:
                split_name = obj.name.rsplit("_", 1)
                self.name = split_name[0]
                self.mesh_name = obj.name
                break
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        selected_mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH' and not obj.group_uuid]
        ignored_objects = [obj for obj in context.selected_objects if obj.type == 'MESH' and obj.group_uuid]
        selected_num = len(selected_mesh_objects)

        layout = self.layout
        if selected_num > 1:
            col = layout.column()
            col.prop(self, 'separate_grouping')
        col = layout.column(align=True)
        col.prop(self, 'name')
        if selected_num == 0:
            return
        col.prop(self, 'mesh_name')
        if selected_num > 1 and self.separate_grouping:
            col.enabled = False
            col.label(text="Separate grouping is enabled, so each object will be in its own group")
        box = layout.box()
        box = box.column(align=True)
        if selected_num == 1:
            box.label(text="Selected high-poly object:", icon='RESTRICT_SELECT_OFF')
            box.label(text=selected_mesh_objects[0].name, translate=False)
        elif selected_num > 1:
            title = box.row()
            title.label(text="Selected high-poly objects:", icon='RESTRICT_SELECT_OFF')
            if self.separate_grouping:
                title = title.row()
                title.alignment = 'RIGHT'
                title.label(text='Group Name', icon='OUTLINER_OB_GROUP_INSTANCE')
            for obj in selected_mesh_objects:
                col = box.row(align=True)
                # col = col.row()
                # col = col.row()
                col.label(text=obj.name, translate=False)
                if self.separate_grouping:
                    col = col.row()
                    col.alignment = 'RIGHT'
                    col.label(text=obj.name.rsplit("_", 1)[0], translate=False)
        if ignored_objects:
            box = layout.box()
            box = box.column(align=True)
            box.enabled = False
            box.label(text="Ignored objects:", icon='TRASH')
            box.alert = True
            for obj in ignored_objects:
                box.label(text=obj.name, translate=False)
            box.alert = False
            box.label(text="Objects will be ignored if they are already in another group")


class OBJECT_OT_remove_object_group(Operator):
    """
    删除所选的组

    参数:
        无
        (所选索引是Scene.object_groups)
    """
    bl_idname = 'object.remove_object_group'
    bl_label = "Delete Group"
    bl_description = "Deletes the selected group (does not delete objects in the group)"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        index = scene.object_groups_index
        valid = 0 <= index < len(scene.object_groups)
        if not valid:
            cls.poll_message_set("Please select a group")
        return valid

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        group: ObjectGroup = scene.object_groups[index]
        if group.low_model:
            group.low_model.group_uuid = ""
        for item in group.high_models:
            print(item.high_model, item.high_model.group_uuid)
            if item.high_model:
                item.high_model.group_uuid = ""
        del_group_entry(group)
        scene.object_groups.remove(index)
        scene.object_groups_index = min(index, len(scene.object_groups) - 1)
        self.report({'INFO'}, "Object group deleted")
        return {'FINISHED'}


class OBJECT_OT_add_object_to_group(Operator):
    """
    将所选物体作为高模添加到组中

    参数:
        update_object_name: 是否在添加后更新高模名称
        (需要Scene.selected_high_model)
    """
    bl_idname = 'object.add_object_to_group'
    bl_label = "Add Object to Group"
    bl_description = "Add object to the currently selected object group"
    bl_options = {'REGISTER', 'UNDO'}

    update_object_name: BoolProperty(name="Update Name", description="Update the suffix for the high-poly object name")

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        selected_high_model = scene.selected_high_model

        if selected_high_model:
            if 0 <= index < len(scene.object_groups):
                if selected_high_model.group_uuid:
                    grp, _ = get_group_entry(selected_high_model.group_uuid)
                    if grp:
                        self.report({'WARNING'}, "Object already in group" + grp.name)
                        return {'CANCELLED'}
                high_group = scene.object_groups[index].high_models
                group = high_group.add()
                group.high_model = selected_high_model
                selected_high_model.group_uuid = scene.object_groups[index].uuid
                scene.selected_high_model = None
                if self.update_object_name:
                    bpy.ops.object.update_group_model_name(group_index=index,
                                                           update_low_model=False,
                                                           update_high_model=self.update_object_name)
                # 重新计算当前的画面(可能位于solo模式)
                scene.object_groups_index = scene.object_groups_index
                context.area.tag_redraw()
                self.report({'INFO'}, "Added to the currently selected object group")
                return {'FINISHED'}
        self.report({'WARNING'}, "Please select a high-poly object")
        return {'CANCELLED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        scene = context.scene
        layout = self.layout
        layout.prop(self, 'update_object_name')
        layout.prop(scene, 'selected_high_model', text="Select High-Poly Objects", icon='SHADING_RENDERED')


class OBJECT_OT_remove_object_from_group(Operator):
    """
    从组中删除物体

    参数:
        object_name: 欲删除的物体名
    """
    bl_idname = 'object.remove_object_from_group'
    bl_label = "Remove Object from Group"
    bl_description = "Remove selected objects from the currently selected object group"
    bl_options = {'REGISTER', 'UNDO'}

    object_name: StringProperty(name="Object Name", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        scene = context.scene
        index = scene.object_groups_index
        valid = 0 <= index < len(scene.object_groups)
        if not valid:
            cls.poll_message_set("Error Index")
        return valid

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        group: ObjectGroup = scene.object_groups[index]

        def clean_up(ob: Object, is_low: bool):
            suffix = scene.low_suffix if is_low else scene.high_suffix
            if ob.name.startswith(group.mesh_name) and ob.name.endswith(suffix):
                ob.name = ob.name.replace(suffix, "")
            # 清除材质,用于避免x-ray模式下,被删除的物体没有清除x-ray的材质
            clear_object_material(ob)
            # 重新计算当前的画面(可能位于solo模式)
            scene.object_groups_index = scene.object_groups_index

        if self.object_name:
            if group.low_model and group.low_model.name == self.object_name:
                obj = group.low_model  # 提前保存 用于update_view
                group.low_model.group_uuid = ""
                group.low_model = None
                clean_up(obj, True)
                self.report({'INFO'}, "Removed from object group")
                return {'FINISHED'}

            i: int = 0
            for h in group.high_models:
                if h.high_model and h.high_model.name == self.object_name:
                    obj = h.high_model  # 提前保存 用于update_view
                    h.high_model.group_uuid = ""
                    group.high_models.remove(i)
                    clean_up(obj, False)
                    self.report({'INFO'}, "Removed from object group")
                    return {'FINISHED'}
                i += 1
            self.report({'WARNING'}, "Object not found")
            return {'CANCELLED'}
        else:
            removed_num: int = 0
            for i in range(len(group.high_models) - 1, -1, -1):
                if not group.high_models[i].high_model:
                    group.high_models.remove(i)
                    removed_num += 1
            if removed_num:
                self.report({'INFO'}, _("Cleared {} empty objects").format(removed_num))
                return {'FINISHED'}
            else:
                self.report({'INFO'}, "No empty objects found")
            return {'CANCELLED'}


class OBJECT_OT_rename_group(Operator):
    """
    组重命名,附带网格命名功能

    参数:
        new_display_name: 新组名
        new_mesh_name: 新网格名(作为网格重命名时的前缀)
        auto_update_name: 是否令新网格名与新组名同步更新
        update_mesh_name: 是否更新网格名称
        update_low_model: 是否更新低模名称
        update_high_model: 是否更新高模名称
    """
    bl_idname = 'object.rename_group'
    bl_label = "Rename Group"
    bl_description = "Rename the current group and synchronize high-poly and low-poly names"
    bl_options = {'REGISTER', 'UNDO'}

    def update_display_name(self, _):
        if self.auto_update_name:
            self.new_mesh_name = self.new_display_name

    new_display_name: StringProperty(name="New Group Name", description="New Display Name", options={'TEXTEDIT_UPDATE'}
                                     , update=update_display_name)
    new_mesh_name: StringProperty(name="Mesh Name",
                                  description="A prefix that denotes both low-poly and high-poly objects, "
                                              "which works when renaming")
    auto_update_name: BoolProperty(name="Auto Name",
                                   description="Automatically synchronizes the mesh name to the group name",
                                   default=False)
    update_mesh_name: BoolProperty(name="Modify Mesh Name",
                                   description="Whether to edit the names of objects in the group",
                                   default=True)
    update_low_model: BoolProperty(name="Synchronize Low-Poly Name",
                                   description="Synchronize Low-Poly Name",
                                   default=True)
    update_high_model: BoolProperty(name="Synchronize High-Poly Name",
                                    description="Synchronize High-Poly Name",
                                    default=True)
    rename_type: EnumProperty(name="Rename Type", description="Rename Type", items=[
        ('Replace', "Replace All", "Completely Replace Name"),
        ('Prefix', "Replace Prefix", "If the model name contains the old group name's prefix, only the prefix will be "
                                     "replaced. Otherwise, the new name will be added in front of the name"),
    ])
    group_uuid: StringProperty()

    def execute(self, context: Context):
        group, index = get_group_entry(self.group_uuid)
        if self.new_mesh_name == "" or self.new_display_name == "":
            self.report({'WARNING'}, "Invalid New Name")
            return {'CANCELLED'}

        if self.update_mesh_name:
            group.mesh_name = self.new_mesh_name
            bpy.ops.object.update_group_model_name(group_index=index,
                                                   update_low_model=self.update_low_model,
                                                   update_high_model=self.update_high_model)

        group.name = self.new_display_name
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        index = scene.object_groups_index
        group: ObjectGroup = scene.object_groups[index]
        self.new_mesh_name = group.mesh_name
        self.new_display_name = group.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        scene = context.scene
        layout = self.layout
        layout.prop(self, property='new_display_name', icon='GREASEPENCIL')
        layout.prop(self, 'update_mesh_name')
        box = layout.box()
        row = box.row()
        row.label(text="Mesh Name", icon='SHADERFX')
        row.prop(self, 'auto_update_name')
        col = box.column(align=True)
        box.enabled = self.update_mesh_name
        col.prop(self, 'new_mesh_name', icon='MESH_DATA')
        col.prop(self, 'update_low_model')
        col.prop(self, 'update_high_model')
        OBJECT_OT_update_model_name.draw_suffix_part(box, scene)
