from common.class_loader.auto_load import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("*", "A Blender add-on designed to streamline the management of high-poly and low-poly models"):
            "一个旨在简化高模低模管理的插件",
        ("*", "Still in development, if you run into any issues, please open an issue on GitHub"):
            "仍在开发中，如果您遇到任何问题，请在GitHub上提出issue",
        ("*", ""): "",
        # group_panel
        ("*", "Missing Object"): "缺失物体",
        ("*", "Model Group Management"): "模型组管理",
        ("*", "Add Group"): "添加物体组",
        ("*", "Delete Group"): "删除物体组",
        ("*", "To make the semi-transparent work, initialize the background material first"): "为了使半透工作，先初始化背景材质",
        ("*", "Initialize Background Material"): "初始化背景材质",
        ("*", "Current Group:"): "当前组:",
        ("*", "Current Group"): "当前组别",
        ("*", "Low-Poly Object"): "低模物体",
        ("*", "High-Poly Object"): "高模物体",
        ("*", "Ungrouped"): "未分组",
        ("*", "Unassigned"): "未分配",
        ("*", "Model Group Management"): "模型组管理",
        ("*", "Specify Low-Poly Object:"): "指定低模物体：",
        ("*", "Generate from High-Poly:"): "根据高模生成：",
        ("*", "Progress"): "进度",
        ("*", "High-Poly"): "高模",
        ("*", "Low-Poly"): "低模",
        ("*", "Model Group Management"): "模型组管理",
        ("*", "{} High-Poly(s)"): "{}个高模",
        ("*", "No High-Poly"): "无高模",
        ("Operator", "Add New High-Poly"): "添加新高模",
        ("*", "Add New High-Poly"): "添加新高模",
        ("Operator", "Rename Group"): "组重命名",
        ("*", ""): "",
        # summary_panel
        ("*", "Summary"): "汇总",
        ("*", "HiLoTools"): "HiLoTools",
        ("*", "All Low-Poly"): "全部低模",
        ("*", "Select All"): "选择全部",
        ("*", "All High-Poly"): "全部高模",
        ("*", "No Low-Poly Exist"): "不存在低模物体",
        ("*", "No High-Poly Exist"): "不存在高模物体",
        ("*", "{} Has HighPoly But No LowPoly"): "{} 存在高模但无低模",
        ("*", "No Ungrouped Objects Exist"): "不存在未分组的物体",
        ("*", "Ungrouped Objects"): "未分组的物体",
        ("*", ""): "",
        # material_panel
        ("*", "Material"): "材质",
        ("*", "Background Material"): "背景材质",
        ("*", "X-Ray High-Poly"): "X-Ray高模材质",
        ("*", "X-Ray Low-Poly"): "X-Ray低模材质",
        # text_ctxt是hl,用于区分默认的Background翻译
        ("hl", "Background Color"): "背景颜色",
        ("*", "X-Ray High-Poly Color"): "X-Ray高模颜色",
        ("*", "X-Ray Low-Poly Color"): "X-Ray低模颜色",
        ("*", ""): "",
        # group_ops
        ("Operator", "Add Group"): "添加物体组",
        ("*", "Create a new group with the selected objects as the High-Poly of the new group"):
            "创建一个新组,并将所选物体作为新组的高模",
        ("*", "Place each selected object individually in a different new group"): "将每个所选物体单独的放到不同的新组中",
        ("*", "The prefix used to rename objects in this group"): "对组内物体进行重命名时所采用的前缀",
        ("*", "The display name of this group, which does not affect the actual name of the object"):
            "此组的显示名称,不影响物体的实际名称",
        ("*", "Separate grouping is enabled, so each object will be in its own group"): "启用了单独的分组，因此每个对象都将位于其自己的组中",
        ("*", "Selected high-poly object:"): "已选择的高模：",
        ("*", "Ignored objects:"): "忽略的对象：",
        ("*", "Objects will be ignored if they are already in another group"): "如果对象已位于另一个组中，则对象将被忽略",
        ("*", "Separate grouping"): "单独分组",
        ("*", "Update Name"): "更新名称",
        ("*", "Update the suffix for the high-poly object name"): "为高模物体名称更新后缀",
        ("Operator", "Delete Group"): "删除物体组",
        ("*", "Deletes the selected group (does not delete objects in the group)"): "删除所选的组(不会删除组内的物体)",
        ("*", "Please select a group"): "需要选择组",
        ("*", "Object group deleted"): "物体组已删除",
        ("Operator", "Add Object to Group"): "添加物体到组",
        ("*", "Add object to the currently selected object group"): "添加物体到当前选中的物体组",
        ("*", "Object already in group"): "物体已存在于组",
        ("*", "Added to the currently selected object group"): "已添加到当前选中的物体组",
        ("*", "Please select a high-poly object"): "请选择高模物体",
        ("*", "Select High-Poly Objects"): "选择高模物体",
        ("Operator", "Remove Object from Group"): "从组中删除物体",
        ("*", "Remove selected objects from the currently selected object group"): "从当前选中的物体组中删除选中的物体",
        ("*", "Object Name"): "Object Name",
        ("*", "Error Index"): "Error Index",
        ("*", "Removed from object group"): "已从物体组中移出",
        ("*", "Removed from object group"): "已从物体组中移出",
        ("*", "Object not found"): "未找到指定的物体",
        ("*", "Cleared {} empty objects"): "清除了{}个空物体",
        ("*", "No empty objects found"): "未发现存在任何空物体",
        ("Operator", "Rename Group"): "组重命名",
        ("*", "Rename Group"): "组重命名",
        ("*", "Rename the current group and synchronize high-poly and low-poly names"): "对当前组进行重命名并同步更新高低模名称",
        ("*", "New Group Name"): "新组别名称",
        ("*", "New Display Name"): "新显示名称",
        ("*", "New Name"): "新名称",
        ("*", "Auto Name"): "自动名称",
        ("*", "Automatically synchronizes the mesh name to the group name"): "自动将网格名称与组名称同步",
        ("*", "Modify Mesh Name"): "修改网格名称",
        ("*", "Whether to edit the names of objects in the group"): "是否修改组内物体的名称",
        ("*", "Synchronize Low-Poly Name"): "同步低模名称",
        ("*", "Synchronize High-Poly Name"): "同步高模名称",
        ("*", "Rename Type"): "重命名类型",
        ("*", "Rename Type"): "重命名类型",
        ("*", "Replace All"): "替换全部",
        ("*", "Completely Replace Name"): "完全替换名称",
        ("*", "Replace Prefix"): "替换前缀",
        ("*", "If the model name contains the old group name's prefix, only the prefix will be replaced. Otherwise, "
              "the new name will be added in front of the name"): "若模型名称包含旧组名称的前缀，则仅替换前缀。否则在名称前追加新名称",
        ("*", "Invalid New Name"): "无效的新名称",
        ("*", "Mesh Name"): "网格名称",
        ("*", "A prefix that denotes both low-poly and high-poly objects, which works when renaming"):
            "在重命名时作为高模和低模对象的前缀",
        ("*", "Suffix"): "后缀",
        ("Operator", "Select Group"): "选择组",
        ("*", "Select Group"): "选择组",
        ("*", "Group Not Found"): "组未找到",
        ("*", ""): "",
        # material_ops
        ("Operator", "Restore Default Material"): "恢复默认材质",
        ("*", "Resets the color of the default material (for semi-see-through/X-Ray mode)"):
            "还原默认材质(用于半透视/X-Ray模式)的颜色",
        ("Operator", "Create Default Material"): "创建默认材质",
        ("*", "Create a default material (for semi-see-through/X-Ray mode)\nDo nothing if a material with the same "
              "name exists"): "创建默认材质(用于半透视/X-Ray模式)\n如果存在同名的材质,则什么也不做",
        ("*", ""): "",
        # object_ops
        ("Operator", "Generate Low-Poly Object"): "生成低模物体",
        ("*", "Generate Low-Poly Object"): "生成低模物体",
        ("*", "Generate Low-Poly Object from High-Poly"): "根据高模组成低模物体",
        ("*", "Exclusion Method"): "排除方式",
        ("*", "Exclude Modifiers in a Certain Way"): "按某种方式排除修改器",
        ("*", "Modifier Name"): "修改器名称",
        ("*", "Exclude by Name"): "按照名称展示、排除",
        ("*", "Modifier Type"): "修改器类型",
        ("*", "Exclude by Type"): "按照类型展示、排除",
        ("*", "Low-Poly Collection"): "低模集合",
        ("*", "No High-Poly Objects Found"): "不存在高模物体",
        ("*", "Objects Merged Successfully"): "物体生成成功",
        ("*", "Collection"): "集合",
        ("*", "Create LOW Collection Automatically if Empty"): "为空则自动创建LOW集合",
        ("*", "Excluded Modifiers"): "排除的修改器",
        ("*", "No Modifiers"): "无修改器",
        ("Operator", "Move Objects to Collection"): "移动物体到集合",
        ("*", "Move all grouped objects to the corresponding set"): "移动所有已编组的物体到对应集合中",
        ("*", "Move Low-Poly Model"): "移动低模物体",
        ("*", "Move the low-poly model to the low-poly collection"): "将低模物体移动到低模集合中",
        ("*", "Move High-Poly Models"): "移动高模物体",
        ("*", "Move the high-poly models to the high-poly collection"): "将高模物体移动到高模集合中",
        ("*", "Low-Poly Collection"): "低模集合",
        ("*", "The name of the collection where low-poly objects will be moved to"): "低模物体将要被移动到此集合中",
        ("*", "High-Poly Collection"): "高模集合",
        ("*", "The name of the collection where high-poly objects will be moved to"): "高模物体将要被移动到此集合中",
        ("*", "Note: If collection does not exist, it will be created"): "注意：如果集合不存在，则创建集合",
        ("Operator", "Update Objects Name"): "更新组内物体名称",
        ("*", "Rename all objects in the group.\nThe naming convention is: mesh name + suffix "
              "\n(If there are duplicate objects, the _n distinction will be appended before the suffix)"):
            "重命名已遍组的所有物体,命名规范为：组网格名+后缀，如果存在重名物体则会在后缀之前附加_n区分",
        ("Operator", "Updated all object names"): "更新所有物体命名",
        ("*", "Group Name"): "组名称",
        ("*", "Name"): "名称",
        ("*", "New Group"): "New Group",
        ("*", "Please select high-poly objects not in other groups"): "需要选择不处于其他组的高模物体",
        ("*", "Skipped due to being in another group:"): "因已添加到其他组，已跳过：",
        ("*", "Object group added"): "物体组已添加",
        ("*", "Selected high-poly objects:"): "已选择的高模：",
        ("*", ""): "",
        # selection_ops
        ("Operator", "Select Group"): "选择组",
        ("*", "Can only be used in Object Mode"): "只能在物体模式中使用",
        ("Operator", "Switch within Group"): "组内切换",
        ("*", "Switch objects within group based on current active item"): "根据当前活动项，切换组内物体",
        ("*", "Selection Range"): "选择范围",
        ("*", "Selection Mode"): "选择模式",
        ("*", "All"): "全部",
        ("*", "Select All"): "选择全部",
        ("*", "High-Poly"): "高模",
        ("*", "Select Only High-Poly"): "只选择高模",
        ("*", "Low-Poly"): "低模",
        ("*", "Select Only Low-Poly"): "只选择低模",
        ("*", "Can only be used in Object Mode or Edit Mode"): "只能在物体模式、编辑模式中使用",
        ("*", "This object does not belong to any group"): "此物体不属于任何组",
        ("*", "Expired UUID"): "过期的UUID",
        ("Operator", "Hover Select"): "悬停选择",
        ("*", "Select object under mouse"): "选择鼠标下的物体",
        ("*", "Please hold Alt key to activate hover select"): "请按住Alt键以激活悬停选择",
        ("Operator", "Select Object"): "选择物体",
        ("*", "Select Object"): "选择物体",
        ("*", "Object Name"): "物体名称",
        ("*", "{} object exists, but not in the current scene"): "{} 物体存在，但不在当前场景中",
        ("*", "Object {} not found"): "未找到物体 {}",
        ("Operator", "Select All Groups"): "全选组",
        ("*", "Select all objects in all groups"): "全选所有组物体",
        ("*", "Clear Selection"): "清除选择",
        ("Operator", "Select Ungrouped Objects"): "选择未分组对象",
        ("*", "Select objects not in any group"): "选择未分组的对象",
        ("*", "High-Poly does not exist or is hidden"): "高模不存在或被隐藏",
        ("*", "Low-Poly does not exist or is hidden"): "低模不存在或被隐藏",
        ("*", "Warning"): "警告",
        ("*", "The object cannot be selected because it is not in the current scene"): "无法选择物体,因为它不在当前场景中",
        ("*", ""): "",
        # view_ops
        ("*", "Solo Group"): "Solo Group",
        ("Operator", "Solo Group"): "Solo Group",
        ("*", "Invalid Group Index"): "无效的组索引",
        ("*", "Local View Group"): "本地视图组",
        ("*", "Switch to the local view of the current object group"): "切换到当前物体组的本地视图",
        ("*", "Invalid Group Index"): "无效的组索引",
        ("*", "Please select at least one group"): "至少选择一组",
        ("*", "X-Ray Group"): "X射线组",
        ("*", "Switch to X-Ray mode for the object group"): "切换到物体组的X-Ray模式",
        ("*", ""): "",
        # properties
        ("*", "Current Selected Group Index"): "当前选取组索引",
        ("*", "Show High-Poly List"): "显示高模列表",
        ("*", "Display Mode"): "画面显示模式",
        ("*", "Default"): "默认",
        ("*", "Default option, no special effect"): "默认选项，无特殊效果",
        ("*", "Focus"): "聚焦",
        ("*", "Switch to the local view of the group"): "切换到组的局部视图显示",
        ("*", "Semi-Transparent"): "半透其他",
        ("*", "Make other groups transparent"): "将其他组进行透明化显示",
        ("*", "Affects Out-Of-Group"): "影响组外物体",
        ("*", "Translucent: All objects that do not belong to any group"): "半透明所有不属于任何组的物体",
        ("*", "High-Poly Mesh Suffix"): "高模后缀",
        ("*", "Low-Poly Mesh Suffix"): "低模后缀",
        ("*", "X-ray fluoroscopy of the currently active group is used to more clearly see "
              "the shape difference between low and high poly"):
            "对当前活动组进行X光透视，用于更加明显的看出低模与高模之间的形状差异",
        ("*", "Material used for inactive objects in Semi-Transparent mode, which is only used for plug-in visuals "
              "and should not be exported for production purposes"):
            "半透模式下非活动物体所用的材质，此材质仅用于插件视觉效果，不应该导出",
        ("*", "Material used for high-poly objects in X-Ray mode, which is only used for plug-in visuals "
              "and should not be exported for production purposes"):
            "X-Ray模式下高模物体所用的材质，此材质仅用于插件视觉效果，不应该导出",
        ("*", "Material used for low-poly objects in X-Ray mode, which is only used for plug-in visuals "
              "and should not be exported for production purposes"):
            "X-Ray模式下低模物体所用的材质，此材质仅用于插件视觉效果，不应该导出",
        ("*", "Warning: Do not modify this value. This value is used to quickly determine the object's affiliation "
              "without having to iterate through the contents of the entire group for matching"):
            "警告：请勿修改此值。此值用于快速确定物体所属，而无需遍历整个组的内容进行匹对",
        ("*", "Sync Selection"): "同步选择",
        ("*", "Synchronizes the active group to the currently selected"): "将活动组与当前所选同步",
        ("*", "All groups of high-poly.\n(click to toggle the folding status)"): "列举所有组别的高模\n（点击可切换折叠状态）",
        ("*", "All groups of low-poly.\n(click to toggle the folding status)"): "列举所有组别的低模\n（点击可切换折叠状态）",
        ("*", "All ungrouped objects.\n(click to toggle the folding status)"): "列举未打组的物体\n（点击可切换折叠状态）",
        ("*", "High-Poly Object"): "高模物体",
        ("*", "Select an object to add as a high-poly to this group.\n"
              "(Note: Automatically filter non-mesh and objects already in other groups)"):
            "选择一个物体作为高模添加到此组中\n（注意：自动过滤非网格物体和已在其他组中的物体）",
        ("*", "Low-Poly does not exist"): "低模物体不存在",
        ("*", ""): "",
        # object_group
        ("*", "Active"): "是否可被选择",
        ("*", "Visible"): "是否可见",
        ("*", "Progress"): "进度",
        ("*", "Pending"): "未开始",
        ("*", "Ongoing"): "正在制作",
        ("*", "Finished"): "已完成",
        ("*", "The production of low-poly has not yet begun"): "低模还未开始制作",
        ("*", "Low poly is in the process of being made"): "低模正在制作过程中",
        ("*", "The low-poly has been made"): "低模已完成制作",
        ("*", ""): "",
        # depsgraph_handler
        ("*", "Not in any group"): "不属于任何组",
        ("*", ""): "",
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
