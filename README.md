# python-json-api-drupal-filters

This package is intended as a generic parser for tree-based filters using the 
[Filter Syntax](https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/filtering)
defined by Drupal for use with APIs following the [JSON:API specification](https://jsonapi.org/).

## Usage
Input data is expected in a dict with the following format:
```python
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
```

Projects using this package should provide their own implementations of the `Condition` and `Group` classes as defined
in `json_api_drupal_filters/filter_tree.py`.

The `parse_filter_data` method of a `FilterParser` object calls `evaluate` on the parser's root group. 
A group's `evaluate` method should call `evaluate` on all the group's members (which can be conditions or other groups). 
In this way, all groups are evaluated recursively, as every group without an explicit `memberOf` value is a member of
the root group, as specified. Loops are avoided because every group can only be member of one other group, and the root.
is a member of no other group.

Very basic examples of a `Condition` and `Group` class that evaluate to a string representation of the underlying
filter logic are provided here:

```python
from json_api_drupal_filters.filter_tree import Condition, Group

class TestCondition(Condition):
    def evaluate(self):
        return f"{self.path} {self.operator} {self.value}" 


class TestGroup(Group):
    def evaluate(self):
        return "(" + f" {self.conjunction} ".join([member.evaluate() for member in self.members]) + ")"
```