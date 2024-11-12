from typing import Callable, Any

import bpy
from bpy.types import Object


def check_group_index(index: int) -> bool:
    return 0 <= index < len(bpy.context.scene.object_groups)


def process_group(group, func: Callable[[Object], Any]):
    process_low_model(group, func)
    process_high_models(group, func)


def process_low_model(group, func: Callable[[Object], Any]):
    if group.low_model:
        func(group.low_model)


def process_high_models(group, func: Callable[[Object], Any]):
    for h in group.high_models:
        if h.high_model:
            func(h.high_model)


def set_attribute_for_group(group, attribute_name, attribute_value):
    set_attribute_for_low_model(group, attribute_name, attribute_value)
    set_attribute_for_high_models(group, attribute_name, attribute_value)


def set_attribute_for_low_model(group, attribute_name, attribute_value):
    if group.low_model:
        setattr(group.low_model, attribute_name, attribute_value)


def set_attribute_for_high_models(group, attribute_name, attribute_value):
    for h in group.high_models:
        if h.high_model:
            setattr(h.high_model, attribute_name, attribute_value)
