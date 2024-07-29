from typing import TypedDict, Callable

import pytest

from json_api_drupal_filters.filter_parser import FilterParser
from json_api_drupal_filters.filter_tree import Condition, Group
from json_api_drupal_filters.filter_errors import RootKeyUsedError, NoGroupOrCondition


class ExampleContext(TypedDict):
    path_mapping: dict[str, str]
    path_processory: dict[str, Callable[[str, str], str]]


@pytest.fixture()
def condition_class() -> type[Condition]:
    class TestCondition(Condition):
        def evaluate(self, context: ExampleContext):
            path = context["path_mapping"].get(self.path, self.path)
            return f"{path} {self.operator} {self.value}"

    return TestCondition


@pytest.fixture()
def group_class() -> type[Group]:
    class TestGroup(Group):
        def evaluate(self, context: ExampleContext):
            return "(" + f" {self.conjunction} ".join([member.evaluate(context) for member in self.members]) + ")"

    return TestGroup


def test_root_key_used_in_name(condition_class, group_class):
    filter_dict = {
        "TestCondition": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "TestField",
                FilterParser.Keys.VALUE: "42",
                FilterParser.Keys.MEMBER_OF: FilterParser.Keys.ROOT
            }
        },
        FilterParser.Keys.ROOT: {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.CONJUNCTION: "AND"
            }
        }
    }
    with pytest.raises(RootKeyUsedError):
        filter_parser = FilterParser(filter_dict, condition_class, group_class)
        filter_parser.parse_filter_data()


def test_no_group_or_condition(condition_class, group_class):
    filter_dict = {
        "TestThingy": {
            "Thingy": {
                FilterParser.Keys.PATH: "TestField",
                FilterParser.Keys.VALUE: "42"
            }
        }
    }
    with pytest.raises(NoGroupOrCondition):
        filter_parser = FilterParser(filter_dict, condition_class, group_class)
        filter_parser.parse_filter_data()


def test_context(condition_class, group_class):
    context = ExampleContext(path_mapping={
        "$abc": "def"
    })

    filter_dict = {
        "TestConditionInRoot": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "$abc",
                FilterParser.Keys.VALUE: "bar",
            }
        },
    }

    filter_parser = FilterParser(filter_dict, condition_class, group_class, context=context)

    res = filter_parser.parse_filter_data()
    assert res == "(def = bar)"
