import uuid
import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Context, Object


from addons.HiLoTools.properties.AddonProperties import ObjectGroup
from addons.HiLoTools.utils.entry_utils import add_group_entry, del_group_entry, get_group_entry


class OBJECT_OT_add_object_group(Operator):
    bl_idname = "object.add_object_group"
    bl_label = "添加物体组"

    group_name: StringProperty(name="组名称", description="名称", default="New Group")
    mesh_name: StringProperty(name="网格名称", description="网格名称")

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH' and not obj.group_info:
                return True
        return False

    def execute(self, context: Context):
        scene = context.scene
        sub_objs = context.selected_objects
        obj_group: ObjectGroup = scene.object_groups.add()
        obj_group.group_name = self.group_name
        obj_group.model_name = self.mesh_name
        obj_group.uuid = str(uuid.uuid4())
        add_group_entry(obj_group)
        warning_text = ""
        for sub_obj in sub_objs:
            if sub_obj.type == 'MESH':
                if sub_obj.group_info:
                    grp, _ = get_group_entry(sub_obj.group_info)
                    if grp:
                        warning_text += grp.group_name + " "
                        continue
                sub_item = obj_group.high_models.add()
                sub_item.high_model = sub_obj
                sub_obj.group_info = obj_group.uuid
                # sub_obj["group"] = obj_group
        if warning_text:
            self.report({'WARNING'}, "因已添加到其他组，已跳过：" + warning_text)
        scene.object_groups_index = len(scene.object_groups) - 1

        self.report({'INFO'}, "物体组已添加")
        return {'FINISHED'}

    def invoke(self, context, event):
        for obj in context.selected_objects:
            if obj.type == 'MESH' and not obj.group_info:
                self.mesh_name = obj.name
                break
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        selected_mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        layout = self.layout
        col = layout.column()
        col.prop(self, "group_name")
        col.prop(self, "mesh_name")
        box = col.box()
        box.label(text="已选择：")
        for obj in selected_mesh_objects:
            box.label(text=obj.name, translate=False)


class OBJECT_OT_remove_object_group(Operator):
    bl_idname = "object.remove_object_group"
    bl_label = "删除物体组"

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index

        if 0 <= index < len(scene.object_groups):
            group: ObjectGroup = scene.object_groups[index]
            if group.low_model:
                group.low_model.group_info = ""
                # del group.low_model["group"]
            for item in group.high_models:
                print(item.high_model, item.high_model.group_info)
                if item.high_model:
                    item.high_model.group_info = ""
                    # del item.high_model["group"]
            del_group_entry(group)
            scene.object_groups.remove(index)
            scene.object_groups_index = min(index, len(scene.object_groups) - 1)
            self.report({'INFO'}, "物体组已删除")
        else:
            self.report({'WARNING'}, "未找到可删除的物体组")
        return {'FINISHED'}


class OBJECT_OT_add_object_to_group(Operator):
    bl_idname = "object.add_object_to_group"
    bl_label = "添加物体到组"
    bl_description = "添加物体到当前选中的物体组"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        selected_high_model = scene.selected_high_model

        if selected_high_model:
            if 0 <= index < len(scene.object_groups):
                if selected_high_model.group_info:
                    grp, _ = get_group_entry(selected_high_model.group_info)
                    if grp:
                        self.report({'WARNING'}, "物体已存在于组" + grp.group_name)
                        return {'CANCELLED'}
                high_group = scene.object_groups[index].high_models
                group = high_group.add()
                group.high_model = selected_high_model
                selected_high_model.group_info = scene.object_groups[index].uuid
                scene.selected_high_model = None
                self.report({'INFO'}, "已添加到当前选中的物体组")
                return {'FINISHED'}
        self.report({'WARNING'}, "请选择高模物体")

        return {'CANCELLED'}


class OBJECT_OT_remove_object_from_group(Operator):
    bl_idname = "object.remove_object_from_group"
    bl_label = "从组中删除物体"
    bl_description = "从当前选中的物体组中删除选中的物体"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(name="Index")  

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        if 0 <= index < len(scene.object_groups):
            group: ObjectGroup = scene.object_groups[index]
            high_models = group.high_models
            if len(high_models) <= self.index:
                self.report({'WARNING'}, "未找到指定的物体")
                return {'CANCELLED'}
            high_models[self.index].high_model.group_info = ""
            # del high_models[index].high_model["group"]

            high_models.remove(self.index)
            self.report({'INFO'}, "已从当前选中的物体组中删除")
            return {'FINISHED'}


class OBJECT_OT_rename_group(Operator):
    bl_idname = "object.rename_group"
    bl_label = "组重命名"
    bl_description = "对当前组进行重命名并同步更新高低模名称"
    bl_options = {"REGISTER", "UNDO"}

    def update_display_name(self, _):
        if self.auto_update_name:
            self.new_name = self.new_display_name

    new_display_name: StringProperty(name="新组别名称", description="新显示名称", options={'TEXTEDIT_UPDATE'},
                                     update=update_display_name)  
    new_name: StringProperty(name="网格名称", description="新名称")  
    auto_update_name: BoolProperty(name="自动名称", description="是否自动更新名称", default=False)  
    update_mesh_name: BoolProperty(name="同步网格名称", description="是否同步网格名称", default=True)  
    update_low_model: BoolProperty(name="同步低模名称", description="是否同步低模名称", default=True)  
    update_high_model: BoolProperty(name="同步高模名称", description="是否同步高模名称", default=True)  
    rename_type: EnumProperty(name="重命名类型", description="重命名类型", items=[
        ("Replace", "替换全部", "完全替换名称"),
        ("Prefix", "替换前缀", "若模型名称包含旧组名称的前缀，则仅替换前缀。否则在名称前追加新名称"),
    ])  

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        group: ObjectGroup = scene.object_groups[index]

        if self.new_name == "" or self.new_display_name == "":
            self.report({'WARNING'}, "无效的新名称")
            return {'CANCELLED'}

        if self.update_mesh_name:
            old_name = group.model_name
            # 重命名低模
            low_model: Object = group.low_model
            if self.update_low_model and low_model:
                if self.rename_type == "Prefix":
                    new_name = ""
                    if low_model.name.startswith(old_name):
                        new_name = low_model.name.replace(old_name, self.new_name)
                    else:
                        new_name = self.new_name + low_model.name
                    low_model.name = new_name
                elif self.rename_type == "Replace":
                    low_model.name = self.new_name + scene.low_suffix
            # 重命名高模
            if self.update_high_model:
                named_times = 0
                for item in group.high_models:
                    high_model: Object = item.high_model
                    if not high_model:
                        continue
                    if self.rename_type == "Prefix":
                        new_name = ""
                        if high_model.name.startswith(old_name):
                            new_name = high_model.name.replace(old_name, self.new_name)
                        else:
                            new_name = self.new_name + high_model.name
                        high_model.name = new_name
                    elif self.rename_type == "Replace":
                        if named_times > 0:
                            high_model.name = self.new_name + "." + str(named_times) + scene.high_suffix
                        else:
                            high_model.name = self.new_name + scene.high_suffix
                        named_times += 1
            group.model_name = self.new_name
        group.group_name = self.new_display_name
        context.area.tag_redraw()
        return {"FINISHED"}

    def invoke(self, context, event):
        scene = context.scene
        index = scene.object_groups_index
        group: ObjectGroup = scene.object_groups[index]
        self.new_name = group.model_name
        self.new_display_name = group.group_name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        scene = context.scene
        layout = self.layout
        layout.prop(self, property="new_display_name", icon="GREASEPENCIL")
        #
        layout.prop(self, "auto_update_name")

        box = layout.box()
        row = box.row()
        row.label(text="网格名称", icon="SHADERFX")
        row.prop(self, "update_mesh_name")
        col = box.column()
        col.enabled = self.update_mesh_name
        col.prop(self, property="new_name", icon="MESH_DATA")
        col.prop(self, "rename_type")
        col.prop(self, "update_low_model")
        col.prop(self, "update_high_model")
        box = box.box()
        box.label(text="后缀")
        col = box.column()
        col.enabled = self.update_low_model
        col.prop(scene, "low_suffix", icon="SHADING_WIRE")
        col = box.column()
        col.enabled = self.update_high_model
        col.prop(scene, "high_suffix", icon="SHADING_RENDERED")