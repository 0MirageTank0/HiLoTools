import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator, Context, Object

from addons.HiLoTools.properties.object_group import ObjectGroup


class ModifierSetting(bpy.types.PropertyGroup):
    modifier_name: StringProperty(name="名称")  
    modifier_type: StringProperty(name="类型")  
    exclude: BoolProperty(name="是否排除")  


class OBJECT_OT_generate_low_poly_object(Operator):
    bl_idname = "object.generate_low_model"
    bl_label = "生成低模物体"
    bl_description = "根据高模组成低模物体"
    bl_options = {'REGISTER', 'UNDO'}

    exclude_type: EnumProperty(
        name="排除方式",
        description="按某种方式排除修改器",
        items=[
            ('Name', "修改器名称", "按照名称展示、排除"),
            ('Type', "修改器类型", "按照类型展示、排除"),
        ]
    )  
    exclude_modifiers: CollectionProperty(type=ModifierSetting)  
    low_collection_name: StringProperty(name="低模集合")  

    @classmethod
    def poll(cls, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        return scene.object_groups[index] and scene.object_groups[index].high_models

    def execute(self, context: Context):
        scene = context.scene
        index = scene.object_groups_index
        obj_group: ObjectGroup = scene.object_groups[index]

        # 处理修改器设置（type类型则需要去除重复）
        if self.exclude_type == 'Type':
            types = set()
            for (index, item) in enumerate(self.exclude_modifiers):
                if item.modifier_type in types:
                    self.exclude_modifiers.remove(index)

        # 获取所有高模物体
        selected_objects = obj_group.high_models

        if not selected_objects:
            self.report({'WARNING'}, "不存在高模物体")
            return {'CANCELLED'}

        # 创建一个新的空网格对象
        mesh = bpy.data.meshes.new("MergedMesh")
        merged_obj = bpy.data.objects.new(obj_group.model_name + scene.low_suffix, mesh)
        context.collection.objects.link(merged_obj)

        new_group = []
        # 处理每个选中的物体
        for high in selected_objects:
            obj = high.high_model
            if obj.type == 'MESH':
                new_obj = obj.copy()
                new_obj.data = obj.data.copy()
                context.collection.objects.link(new_obj)
                context.view_layer.objects.active = new_obj
                new_group.append(new_obj)
                # 应用修改器
                if self.exclude_type == 'Name':
                    names = [item.modifier_name for item in self.exclude_modifiers]
                    for modifier in new_obj.modifiers:
                        if modifier.name not in names:
                            bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)
                elif self.exclude_type == 'Type':
                    types = [item.modifier_type for item in self.exclude_modifiers]
                    for modifier in new_obj.modifiers:
                        if modifier.type not in types:
                            bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)
            else:
                self.report({'WARNING'}, f"Object {obj.name} is not a mesh and will be skipped")

        # 选择合并后的物体
        # bpy.ops.object.select_all(action='DESELECT')
        # for obj in new_group:
        #     obj.select_set(True)
        # merged_obj.select_set(True)
        # context.view_layer.objects.active = merged_obj
        new_group.append(merged_obj)
        with context.temp_override(active_object=merged_obj, selected_editable_objects=new_group):
            bpy.ops.object.join()

        obj_group.low_model = merged_obj

        if self.low_collection_name == "":
            self.low_collection_name = "LOW"
        low_collection = bpy.data.collections.get(self.low_collection_name)
        if not low_collection:
            low_collection = bpy.data.collections.new(self.low_collection_name)
            context.scene.collection.children.link(low_collection)

        for coll in merged_obj.users_collection:
            coll.objects.unlink(merged_obj)

        low_collection.objects.link(merged_obj)

        self.report({'INFO'}, "Objects merged successfully")
        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        index = scene.object_groups_index
        obj_group: ObjectGroup = scene.object_groups[index]
        self.exclude_modifiers.clear()
        for obj in obj_group.high_models:
            high: Object = obj.high_model
            for modifier in high.modifiers:
                print(modifier.name)
                i = self.exclude_modifiers.add()
                i.modifier_name = modifier.name
                i.modifier_type = modifier.type
                i.exclude = modifier.type == 'SUBSURF'
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context: Context):
        layout = self.layout
        col = layout.column()
        box = col.box()
        box.label(text="集合", icon="SHADING_WIRE")
        box.prop_search(self, "low_collection_name", bpy.data, "collections")
        box.label(text="为空则自动创建LOW集合")
        col = layout.column()
        box = col.box()
        box.label(text="排除的修改器", icon="MODIFIER_DATA")
        if len(self.exclude_modifiers) == 0:
            box.label(text="无修改器")
        else:
            box.prop(self, "exclude_type")
            if self.exclude_type == 'Name':
                for item in self.exclude_modifiers:
                    row = box.row()
                    row.prop(item, "exclude", text=item.modifier_name, icon="MOD_" + item.modifier_type,
                             translate=False)
            elif self.exclude_type == 'Type':
                types = set()
                for (index, item) in enumerate(self.exclude_modifiers):
                    if item.modifier_type not in types:
                        types.add(item.modifier_type)
                        row = box.row()
                        row.prop(item, "exclude", text=item.modifier_type, icon="MOD_" + item.modifier_type)
                    # 不可修改内容，因为用户可能会再次切换到Name显示
                    # else:
                    #     self.exclude_modifiers.remove(index)