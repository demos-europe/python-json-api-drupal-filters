from enum import StrEnum
from collections import defaultdict

from filter_validator import FilterValidator


class FilterParser:
    class Keys(StrEnum):
        AND = "and"
        CONDITION = "condition"
        CONJUNCTION = "conjunction"
        GROUP = "group"
        MEMBER_OF = "memberOf"
        OPERATOR = "operator"
        OR = "or"
        PATH = "path"
        ROOT = "@root"
        VALUE = "value"

    def __init__(self, filter_dict):
        self.filter_validator = FilterValidator()
        self.groups = defaultdict(dict)

        if self.Keys.ROOT in filter_dict:
            raise KeyError(f"The name of a group or condition MUST NOT be the root key '{self.Keys['root']}'.")

        for key, value in filter_dict.items():
            if self.Keys.GROUP in value:
                group = value[self.Keys.GROUP]
                self.groups[key].update({
                    "conjunction": group[self.Keys.CONJUNCTION],
                    "member_of": self._get_member_of(group)
                })
            elif self.Keys.CONDITION in value:
                condition = value[self.Keys.CONDITION]
                member_of = self._get_member_of(condition)
                if member_of in self.groups:
                    if "conditions" in self.groups[member_of]:
                        self.groups[member_of]["conditions"] = [condition]
                    else:
                        self.groups[member_of]["conditions"].append(condition)
                else:
                    self.groups[member_of] = {"conditions": [condition]}
            else:
                raise KeyError(f"Filter element {key} MUST contain either '{self.Keys.GROUP}' "
                               f"or '{self.Keys.CONDITION}' as key.")

    def _get_member_of(self, group_or_condition):
        if self.Keys.MEMBER_OF in group_or_condition:
            member_of = group_or_condition[self.Keys.MEMBER_OF]
            if member_of == self.Keys.ROOT:
                raise KeyError(f"The 'memberOf' field MUST NOT use the root key '{self.Keys['root']}'.")
            return member_of
        return self.Keys.ROOT

    def parse_conditions(self):
        pass

    def create_group(self):
        pass

    def parse_filter_data(self, filter_data):
        pass


