import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty, IntProperty
from bpy.types import Operator, Context, Object

from addons.HiLoTools.properties.object_group import ObjectGroup
from addons.HiLoTools.utils.group_utils import process_low_model, process_high_models


def get_or_create_collection(collection_name: str, context: Context) -> bpy.types.Collection:
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        collection = bpy.data.collections.new(collection_name)
        context.scene.collection.children.link(collection)
    return collection


class ModifierSetting(bpy.types.PropertyGroup):
    """
    修改器信息,仅用于充当OBJECT_OT_generate_low_poly_object的参数
    """
    modifier_name: StringProperty()
    modifier_type: StringProperty()
    exclude: BoolProperty()


class OBJECT_OT_generate_low_poly_object(Operator):
    """
    根据高模模型生成低模物体(去除高模的特定修改器,合并网格)

    参数:
        exclude_type: 去除修改器的方式
            Name: 根据修改器名称去除修改器
            Type: 根据修改器类型去除修改器
        exclude_modifiers: 要去除的修改器的信息
        low_collection_name: 指定要将生成的低模放置于哪一个集合的名称,不存在则创建,为空则使用LOW作为参数
    """
    bl_idname = 'object.generate_low_model'
    bl_label = "Generate Low-Poly Object"
    bl_description = "Generate Low-Poly Object from High-Poly"
    bl_options = {'REGISTER', 'UNDO'}

    exclude_type: EnumProperty(
        name="Exclusion Method",
        description="Exclude Modifiers in a Certain Way",
        items=[
            ('Name', "Modifier Name", "Exclude by Name"),
            ('Type', "Modifier Type", "Exclude by Type"),
        ]
    )
    exclude_modifiers: CollectionProperty(type=ModifierSetting)
    low_collection_name: StringProperty(name="Low-Poly Collection")

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
            self.report({'WARNING'}, "No High-Poly Objects Found")
            return {'CANCELLED'}

        # 创建一个新的空网格对象
        mesh = bpy.data.meshes.new('MergedMesh')
        merged_obj = bpy.data.objects.new(obj_group.model_name + scene.low_suffix, mesh)
        context.collection.objects.link(merged_obj)

        new_group = []
        # 处理每个选中的物体
        for high in selected_objects:
            obj = high.high_model
            if obj.type == 'MESH':
                new_obj = obj.copy()
                new_obj.data = obj.data.copy()
                bpy.context.collection.objects.link(new_obj)

                new_group.append(new_obj)
                # 应用修改器
                if self.exclude_type == 'Name':
                    names = [item.modifier_name for item in self.exclude_modifiers if item.exclude]
                    bpy.context.view_layer.objects.active = new_obj
                    for modifier in new_obj.modifiers:
                        if modifier.name not in names:
                            print(f"apply {modifier.name}")
                            bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)
                elif self.exclude_type == 'Type':
                    types = [item.modifier_type for item in self.exclude_modifiers if item.exclude]
                    for modifier in new_obj.modifiers:
                        if modifier.type not in types:
                            bpy.ops.object.modifier_apply(modifier=modifier.name, single_user=True)
        new_group.append(merged_obj)
        with context.temp_override(active_object=merged_obj, selected_editable_objects=new_group):
            bpy.ops.object.join()

        obj_group.low_model = merged_obj

        if self.low_collection_name == "":
            self.low_collection_name = 'LOW'
        low_collection = get_or_create_collection(self.low_collection_name, context)

        for coll in merged_obj.users_collection:
            coll.objects.unlink(merged_obj)

        low_collection.objects.link(merged_obj)
        bpy.ops.object.select_all(action='DESELECT')
        merged_obj.select_set(True)
        self.report({'INFO'}, "Objects Merged Successfully")
        return {'FINISHED'}

    def invoke(self, context, event):
        scene = context.scene
        index = scene.object_groups_index
        obj_group: ObjectGroup = scene.object_groups[index]
        self.exclude_modifiers.clear()
        for obj in obj_group.high_models:
            high: Object = obj.high_model
            for modifier in high.modifiers:
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
        box.label(text="Collection", icon='SHADING_WIRE')
        box.prop_search(self, 'low_collection_name', bpy.data, 'collections', results_are_suggestions=True)
        box.label(text="Create LOW Collection Automatically if Empty")
        col = layout.column()
        box = col.box()
        box.label(text="Excluded Modifiers", icon='MODIFIER_DATA')
        if len(self.exclude_modifiers) == 0:
            box.label(text="No Modifiers")
        else:
            box.prop(self, 'exclude_type')
            if self.exclude_type == 'Name':
                for item in self.exclude_modifiers:
                    row = box.row()
                    row.prop(item, 'exclude', text=item.modifier_name, icon='MOD_' + item.modifier_type,
                             translate=False)
            elif self.exclude_type == 'Type':
                types = set()
                for (index, item) in enumerate(self.exclude_modifiers):
                    if item.modifier_type not in types:
                        types.add(item.modifier_type)
                        row = box.row()
                        row.prop(item, 'exclude', text=item.modifier_type, icon='MOD_' + item.modifier_type)


class OBJECT_OT_move_to_collection(bpy.types.Operator):
    """
    移动所有已编组的物体到对应集合中

    参数：
        move_low_model: 是否移动低模物体
        move_high_models: 是否移动高模物体
        low_collection_name: 低模集合名称
        high_collection_name: 高模集合名称
        *如果集合不存在则将创建
    """
    bl_idname = "object.move_objects_to_collection"
    bl_label = "Move Objects to Collection"
    bl_description = "Move all grouped objects to the corresponding set"
    bl_options = {'REGISTER', 'UNDO'}

    move_low_model: BoolProperty(
        name="Move Low-Poly Model",
        description="Move the low-poly model to the low-poly collection",
        default=True
    )
    move_high_models: BoolProperty(
        name="Move High-Poly Models",
        description="Move the high-poly models to the high-poly collection",
        default=True
    )
    low_collection_name: StringProperty(
        name="Low-Poly Collection",
        description="The name of the collection where low-poly objects will be moved to",
        default="LOW"
    )
    high_collection_name: StringProperty(
        name="High-Poly Collection",
        description="The name of the collection where high-poly objects will be moved to",
        default="HIGH"
    )

    def execute(self, context):
        scene = context.scene
        low_collection: [bpy.types.Collection] = None
        if self.move_low_model:
            low_collection = get_or_create_collection(self.low_collection_name, context)

        high_collection: [bpy.types.Collection] = None
        if self.move_high_models:
            high_collection = get_or_create_collection(self.high_collection_name, context)

        for grp in scene.object_groups:
            grp: ObjectGroup
            if self.move_low_model and grp.low_model:
                for col in grp.low_model.users_collection:
                    col.objects.unlink(grp.low_model)
                low_collection.objects.link(grp.low_model)
            if self.move_high_models:
                for h in grp.high_models:
                    if h.high_model:
                        for col in h.high_model.users_collection:
                            col.objects.unlink(h.high_model)
                        high_collection.objects.link(h.high_model)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'move_low_model')
        col.prop_search(self, 'low_collection_name', bpy.data, 'collections',
                        icon='SHADING_WIRE', results_are_suggestions=True)

        col = layout.column()
        col.prop(self, 'move_high_models')
        col.prop_search(self, 'high_collection_name', bpy.data, 'collections',
                        icon='SHADING_RENDERED', results_are_suggestions=True)

        col.label(text="Note: If collection does not exist, it will be created")


class OBJECT_OT_update_model_name(Operator):
    """
    重命名已遍组的所有物体,命名规范为：组名+后缀，如果存在重名物体则会在后缀之前附加_n区分

    参数:
        group_index: 重命名目标,若为-1则代表重命名所有
        update_low_model: 是否更新低模命名
        update_high_model: 是否更新高模命名
    """
    bl_idname = 'object.update_group_model_name'
    bl_label = "Update Objects Name"
    bl_description = ("Rename all objects in the group, the naming convention is: group name + suffix, "
                      "if there are duplicate objects, the _n distinction will be appended before the suffix")
    bl_options = {'REGISTER', 'UNDO'}

    group_index: IntProperty(name="Group Index", default=-1, options={'SKIP_SAVE'})
    update_low_model: BoolProperty(name="Synchronize Low-Poly Name",
                                   description="Synchronize Low-Poly Name",
                                   default=True, options={'SKIP_SAVE'})
    update_high_model: BoolProperty(name="Synchronize High-Poly Name",
                                    description="Synchronize High-Poly Name",
                                    default=True, options={'SKIP_SAVE'})

    def execute(self, context):
        if not (self.update_low_model or self.update_high_model):
            return {'CANCELLED'}
        scene = context.scene
        index = self.group_index

        existing_names = {obj.name for obj in bpy.data.objects}

        def update_object_name(obj: Object, mesh_name: str, suffix: str):
            existing_names.remove(obj.name)
            ind: int = 0
            target_name = "{}{}".format(mesh_name, suffix)
            while target_name in existing_names:
                ind += 1
                target_name = "{}_{}{}".format(mesh_name, ind, suffix)
            obj.name = target_name
            print(target_name)
            existing_names.add(target_name)

        def update_group(group: ObjectGroup):
            if self.update_low_model:
                process_low_model(group,
                                  lambda obj: update_object_name(obj,
                                                                 mesh_name=group.model_name,
                                                                 suffix=scene.low_suffix))
            if self.update_high_model:
                process_high_models(group,
                                    lambda obj: update_object_name(obj,
                                                                   mesh_name=group.model_name,
                                                                   suffix=scene.high_suffix))

        if index == -1:
            for grp in scene.object_groups:
                update_group(grp)
        else:
            update_group(scene.object_groups[index])
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'update_low_model')
        col.prop(self, 'update_high_model')
        self.draw_suffix_part(layout, scene)

    @staticmethod
    def draw_suffix_part(layout, scene):

        box = layout.box()
        box.label(text="Suffix")
        col = box.column(align=True)
        col.prop(scene, 'low_suffix', icon='SHADING_WIRE')
        col.prop(scene, 'high_suffix', icon='SHADING_RENDERED')
