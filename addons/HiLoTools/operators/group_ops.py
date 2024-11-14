import uuid
import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Context, Object

from addons.HiLoTools.properties.object_group import ObjectGroup, get_group_entry, add_group_entry, del_group_entry
from addons.HiLoTools.utils.material_utils import clear_object_material
_ = bpy.app.translations.pgettext

class OBJECT_OT_add_object_group(Operator):
    bl_idname = 'object.add_object_group'
    bl_label = "Add Object Group"
    bl_description = "Create a new group with the selected objects as the High-Poly of the new group"
    name: StringProperty(name="Group Name", description="Name", default="New Group")
    mesh_name: StringProperty(name="Mesh Name", description="Mesh Name")

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH' and not obj.group_uuid:
                return True
        cls.poll_message_set("Please select high-poly objects not in other groups")
        return False

    def execute(self, context: Context):
        scene = context.scene
        sub_objs = context.selected_objects
        obj_group: ObjectGroup = scene.object_groups.add()
        obj_group.name = self.name
        obj_group.model_name = self.mesh_name
        obj_group.uuid = str(uuid.uuid4())
        add_group_entry(obj_group)
        warning_text = ""
        for sub_obj in sub_objs:
            if sub_obj.type == 'MESH':
                if sub_obj.group_uuid:
                    grp, _ = get_group_entry(sub_obj.group_uuid)
                    if grp:
                        warning_text += grp.name + " "
                        continue
                sub_item = obj_group.high_models.add()
                sub_item.high_model = sub_obj
                sub_obj.group_uuid = obj_group.uuid
        if warning_text:
            self.report({'WARNING'}, "Skipped due to being in another group:" + warning_text)
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
        selected_mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        layout = self.layout
        col = layout.column()
        col.prop(self, 'name')
        col.prop(self, 'mesh_name')
        box = col.box()
        box.label(text="Selected high-poly objects:")
        for obj in selected_mesh_objects:
            box.label(text=obj.name, translate=False)


class OBJECT_OT_remove_object_group(Operator):
    bl_idname = 'object.remove_object_group'
    bl_label = "Delete Object Group"
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
    bl_idname = 'object.add_object_to_group'
    bl_label = "Add Object to Group"
    bl_description = "Add object to the currently selected object group"
    bl_options = {'REGISTER', 'UNDO'}

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
        layout.prop(scene, 'selected_high_model', text="Select High-Poly Objects", icon='SHADING_RENDERED')


class OBJECT_OT_remove_object_from_group(Operator):
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

        def update_view(ob):
            # 清除材质,用于避免x-ray模式下,被删除的物体没有清除x-ray的材质
            clear_object_material(ob)
            # 重新计算当前的画面(可能位于solo模式)
            scene.object_groups_index = scene.object_groups_index

        if self.object_name:
            if group.low_model and group.low_model.name == self.object_name:
                obj = group.low_model  # 提前保存 用于update_view
                group.low_model.group_uuid = ""
                group.low_model = None
                update_view(obj)
                self.report({'INFO'}, "Removed from object group")
                return {'FINISHED'}

            i: int = 0
            for h in group.high_models:
                if h.high_model and h.high_model.name == self.object_name:
                    obj = h.high_model  # 提前保存 用于update_view
                    h.high_model.group_uuid = ""
                    group.high_models.remove(i)
                    update_view(obj)
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
    bl_idname = 'object.rename_group'
    bl_label = "Rename Group"
    bl_description = "Rename the current group and synchronize high-poly and low-poly names"
    bl_options = {'REGISTER', 'UNDO'}

    def update_display_name(self, _):
        if self.auto_update_name:
            self.new_name = self.new_display_name

    new_display_name: StringProperty(name="New Group Name", description="New Display Name", options={'TEXTEDIT_UPDATE'}
                                     , update=update_display_name)
    new_name: StringProperty(name="Mesh Name", description="New Name")
    auto_update_name: BoolProperty(name="Auto Name",
                                   description="Automatically synchronizes the grid name to the group name",
                                   default=False)
    update_mesh_name: BoolProperty(name="Modify Mesh Name",
                                   description="Whether to modify the name of the mesh",
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
        scene = context.scene
        group, _ = get_group_entry(self.group_uuid)
        print(group)
        if self.new_name == "" or self.new_display_name == "":
            self.report({'WARNING'}, "Invalid New Name")
            return {'CANCELLED'}

        if self.update_mesh_name:
            old_name = group.model_name
            # 重命名低模
            low_model: Object = group.low_model
            if self.update_low_model and low_model:
                if self.rename_type == 'Prefix':
                    new_name: str
                    if low_model.name.startswith(old_name):
                        new_name = low_model.name.replace(old_name, self.new_name)
                    else:
                        new_name = self.new_name + low_model.name
                    low_model.name = new_name
                elif self.rename_type == 'Replace':
                    low_model.name = self.new_name + scene.low_suffix
            # 重命名高模
            if self.update_high_model:
                named_times = 0
                for item in group.high_models:
                    high_model: Object = item.high_model
                    if not high_model:
                        continue
                    if self.rename_type == 'Prefix':
                        new_name = ""
                        if high_model.name.startswith(old_name):
                            new_name = high_model.name.replace(old_name, self.new_name)
                        else:
                            new_name = self.new_name + high_model.name
                        high_model.name = new_name
                    elif self.rename_type == 'Replace':
                        if named_times > 0:
                            high_model.name = self.new_name + "." + str(named_times) + scene.high_suffix
                        else:
                            high_model.name = self.new_name + scene.high_suffix
                        named_times += 1
            group.model_name = self.new_name
        group.name = self.new_display_name
        context.area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        index = scene.object_groups_index
        group: ObjectGroup = scene.object_groups[index]
        self.new_name = group.model_name
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
        col.prop(self, property='new_name', icon='MESH_DATA')
        col.prop(self, 'rename_type')
        col.prop(self, 'update_low_model')
        col.prop(self, 'update_high_model')
        box = box.box()
        box.label(text="Suffix")
        col = box.column()
        col.enabled = self.update_low_model
        col.prop(scene, 'low_suffix', icon='SHADING_WIRE')
        col = box.column()
        col.enabled = self.update_high_model
        col.prop(scene, 'high_suffix', icon='SHADING_RENDERED')
