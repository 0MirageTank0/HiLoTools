import bpy

from typing import Optional, Tuple

from addons.HiLoTools.properties.AddonProperties import ObjectGroup


def get_group_entry(uuid) -> Tuple[Optional[ObjectGroup], int]:
    # entry : ObjectGroup
    for (index, entry) in enumerate(bpy.context.scene.object_groups):
        if entry.uuid == uuid:
            return entry, index
    return None, -1


def add_group_entry(group: ObjectGroup):
    return


def del_group_entry(uuid):
    return