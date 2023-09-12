from collections import defaultdict

from json_api_drupal_filters.filter_errors import *


class FilterParser:
    class Keys:
        CONDITION = "condition"
        CONJUNCTION = "conjunction"
        GROUP = "group"
        MEMBER_OF = "memberOf"
        OPERATOR = "operator"
        PATH = "path"
        ROOT = "@root"
        VALUE = "value"

    def __init__(self, filter_dict, condition_class, group_class):
        """
        :param filter_dict: a dictionary with the following structure:
        {
            ...
            "groupName1": {
                "group": {
                    "conjunction": "AND"
                }
            },
            "conditionName1": {
                "condition": {
                    "path": "field1",
                    "operator": "%3D",
                    "value": 42,
                    "memberOf": "groupName1"
                }
            },
            "conditionName2": {
                "condition": {
                    "path": "field2",
                    "operator": "%3D",
                    "value": 23,
                    "memberOf": "groupName1"
                }
            },
            ...
        }
        :param condition_class: A concrete implementation of the Condition class
        :param group_class: A concrete implementation of the Group class
        """

        self.filter_dict = filter_dict
        self.condition_class = condition_class
        self.group_class = group_class
        self.grouped_conditions = defaultdict(dict)
        self.root_group = self.group_class(conjunction="AND")
        self.grouped_conditions[self.Keys.ROOT] = {"object": self.root_group}

    def parse_filter_data(self):
        self._group_conditions()
        self._parse_conditions_and_groups()
        self._build_tree()
        return self.root_group.evaluate()

    def _get_member_of(self, group_or_condition):
        if self.Keys.MEMBER_OF in group_or_condition:
            member_of = group_or_condition[self.Keys.MEMBER_OF]
            if member_of == self.Keys.ROOT:
                raise RootKeyUsedError(
                    f"The 'memberOf' field MUST NOT use the root key '{self.Keys.ROOT}'.")
            return member_of
        return self.Keys.ROOT

    def _group_conditions(self):
        if self.Keys.ROOT in self.filter_dict:
            raise RootKeyUsedError(
                f"The name of a group or condition MUST NOT be the root key '{self.Keys.ROOT}'.")

        for name, group_or_condition in self.filter_dict.items():
            if self.Keys.GROUP in group_or_condition:
                group = group_or_condition[self.Keys.GROUP]
                if self.Keys.CONJUNCTION not in group or not group[self.Keys.CONJUNCTION]:
                    continue
                self.grouped_conditions[name].update({
                    "conjunction": group[self.Keys.CONJUNCTION],
                    "member_of": self._get_member_of(group)
                })
            elif self.Keys.CONDITION in group_or_condition:
                condition = group_or_condition[self.Keys.CONDITION]
                member_of = self._get_member_of(condition)
                if self.Keys.VALUE not in condition or not condition[self.Keys.VALUE]:
                    continue
                # grouped_conditions is a defaultdict
                if "conditions" in self.grouped_conditions[member_of]:
                    self.grouped_conditions[member_of]["conditions"].append(
                        condition)
                else:
                    self.grouped_conditions[member_of]["conditions"] = [
                        condition]
            else:
                raise NoGroupOrCondition(f"Filter element {name} MUST contain either '{self.Keys.GROUP}' "
                                         f"or '{self.Keys.CONDITION}' as key.")

    def _parse_conditions_and_groups(self):
        for name, group in self.grouped_conditions.items():
            group_object = self.root_group if name == self.Keys.ROOT else self.group_class(
                group["conjunction"])
            if "conditions" in group:
                for condition in group["conditions"]:
                    group_object.members.append(
                        self.condition_class(**condition))
            group["object"] = group_object

    def _build_tree(self):
        for name, group in self.grouped_conditions.items():
            if "member_of" in group:
                parent_name = group["member_of"]
                self.grouped_conditions[parent_name]["object"].members.append(
                    group["object"])
