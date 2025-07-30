from __future__ import annotations

import json
import re
from typing import get_type_hints
from dataclasses import dataclass

@dataclass
class ForeignKeyProxy:
    column_name: str
    table_name: str


CORE_TYPES = [
    "Mapped[str]",
    "Mapped[int]",
    "Mapped[float]",
    "Mapped[bool]",
    "Mapped[Optional[str]]",
    "Mapped[Optional[int]]",
    "Mapped[Optional[float]]",
    "Mapped[Optional[bool]]",

    # In swedish we call it helgardering
    "sqlalchemy.orm.base.Mapped[str]",
    "sqlalchemy.orm.base.Mapped[int]",
    "sqlalchemy.orm.base.Mapped[float]",
    "sqlalchemy.orm.base.Mapped[bool]",
    "sqlalchemy.orm.base.Mapped[typing.Optional[str]]",
    "sqlalchemy.orm.base.Mapped[typing.Optional[int]]",
    "sqlalchemy.orm.base.Mapped[typing.Optional[float]]",
    "sqlalchemy.orm.base.Mapped[typing.Optional[bool]]",
]
class JsonSerializer[T]():
    def __init__(self, camelCase_to_snake_case: bool = False):
        self.camelCase_to_snake_case = camelCase_to_snake_case

    def __key_name(self, key: str) -> str:
        if self.camelCase_to_snake_case:
            return re.sub(r'_(\w)', lambda m: m.group(1).upper(), key)
        else:
            return key
        
    def __get_generic(self) -> T:
        return self.__orig_class__.__args__[0] # type: ignore
    
    def __get_fk(self, attr: str) -> ForeignKeyProxy | None:
        generic_attrs = self.__get_generic().__dict__[attr].__dict__
        is_fk = bool("foreign_keys" in generic_attrs and generic_attrs["foreign_keys"])
        if not is_fk:
            return None
        if is_fk:
            fk = [fk for fk in generic_attrs["foreign_keys"]][0] #TODO: Allow multiple (???)
            return ForeignKeyProxy(fk.column.name, fk.column.table.name)
    
    def __is_optional(self, t: type):
        return "Optional" in str(t)
    
    def deserialize_string_to_many(self, s: str) -> list[T]:
        parsed_list = json.loads(s)
        if not isinstance(parsed_list, list):
            raise ValueError("Provided json string is not an array.")
        deserialized_list: list[T] = []
        for i in parsed_list: # type:ignore
            deserialized_list.append(self.deserialize_string(json.dumps(i)))
        return deserialized_list
        
    def deserialize_string(self, s: str) -> T:
        generic = self.__get_generic()
        parsed_from_json_string = json.loads(s)
        deserialized = {}
        foreign_keys: dict[str, ForeignKeyProxy] = {}
        try:
            type_hint_items = get_type_hints(generic).items()
        except NameError as e:
            print(f"""Got "{e}", probably because a nested type is not defined in globals. Please declare your references type on a module level to make sure they are in the global scope.""")
            raise
        for type_hinted_attribute, type_hinted_type in type_hint_items:
            if str(type_hinted_type) in CORE_TYPES:
                fk = self.__get_fk(type_hinted_attribute)
                if fk:
                    foreign_keys[type_hinted_attribute] = fk
                    continue
            
                core_type_val = parsed_from_json_string.get(self.__key_name(type_hinted_attribute), None)
                if core_type_val is None and not self.__is_optional(type_hinted_type):
                    raise ValueError(f"{type_hinted_attribute} is missing from the string input")
                deserialized[type_hinted_attribute] = core_type_val
            else:
                nested_class = type_hinted_type.__args__[0]
                deserialized[type_hinted_attribute] = JsonSerializer[nested_class](camelCase_to_snake_case=self.camelCase_to_snake_case).deserialize_string(json.dumps(parsed_from_json_string[self.__key_name(type_hinted_attribute)]))

        for fk_id_attribute, fk in foreign_keys.items():
            related_attribut_table = fk.table_name #TODO: This is probably not a safe assumption
            related_attribute_column = fk.column_name
            deserialized[fk_id_attribute] = deserialized[related_attribut_table].__dict__[related_attribute_column] # type: ignore
        return generic(**deserialized) # type: ignore