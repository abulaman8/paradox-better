from typing import List, Literal, Union


class DependencyType:
    def __init__(self, id: str, block_id: int, element_id: int, value: str):
        self.id = id
        self.block_id = block_id
        self.element_id = element_id
        self.value = value


class InputType:
    def __init__(self, id: str, value: str, required: bool, placeholder: str, autocomplete: bool, max: int | None, min: int | None = None, maxLength: int | None = None, minLength: int | None = None):
        self.id = id
        self.value = value
        self.required = required
        self.placeholder = placeholder
        self.autocomplete = autocomplete
        self.max = max
        self.min = min
        self.maxLength = maxLength
        self.minLength = minLength


class SelectType:
    def __init__(self, id: str, value: str, required: bool, inputs: List[str]):
        self.id = id
        self.value = value
        self.required = required
        self.inputs = inputs


class RadioGroupType:
    def __init__(self, id: str, value: str, required: bool, dependency: bool, inputs: List[str]):
        self.id = id
        self.value = value
        self.required = required
        self.dependency = dependency
        self.inputs = inputs


class CheckboxGroupType:
    def __init__(self, id: str, values: List[str], required: bool, inputs: List[str]):
        self.id = id
        self.values = values
        self.required = required
        self.inputs = inputs


class ElementType:
    def __init__(self, id: str, position: int, block_id: str, label: str, name: str, inputType: str, element: Union[InputType, SelectType, RadioGroupType, CheckboxGroupType]):
        self.id = id
        self.position = position
        self.block_id = block_id
        self.label = label
        self.name = name
        self.inputType = inputType
        self.element = element


class BlockType:
    def __init__(self, id: str, position: int, title: str,  elements: List[ElementType], dependencies: List[DependencyType] | None = None):
        self.id = id
        self.position = position
        self.title = title
        self.dependencies = dependencies if dependencies is not None else []
        self.elements = elements


class FormType:
    def __init__(self, id: str, bg_img: str, name: str, desc: str, solo: bool, blocks: List[BlockType]):
        self.id = id
        self.bg_img = bg_img
        self.name = name
        self.desc = desc
        self.solo = solo
        self.blocks = blocks


AllTypes = Literal[
    "text",
    "select",
    "radio",
    "checkbox",
    "textarea",
    "number",
    "url",
    "datetime-local",
    "date",
    "time",
    "tel",
    "email"
]
