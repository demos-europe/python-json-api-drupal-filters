from types import NoneType
from typing import TypedDict

import pytest

from json_api_drupal_filters.filter_parser import FilterParser
from json_api_drupal_filters.filter_tree import Condition, Group
from json_api_drupal_filters.filter_errors import RootKeyUsedError, NoGroupOrCondition


class ExampleContext(TypedDict):
    paths: list[str]
    operators: dict[str, list[str]]


@pytest.fixture()
def condition_class() -> type[Condition]:
    class TestCondition(Condition):
        def evaluate(self, _):
            return f"{self.path} {self.operator} {self.value}"

    return TestCondition


@pytest.fixture()
def group_class() -> type[Group]:
    class TestGroup(Group):
        def evaluate(self, context):
            return "(" + f" {self.conjunction} ".join([member.evaluate(context) for member in self.members]) + ")"

    return TestGroup


@pytest.fixture()
def example_context() -> ExampleContext:
    return ExampleContext(paths=["name"], operators={"name": ["=", "~"]})


@pytest.fixture()
def valid_filter_dict():
    filter_dict = {
        "TestConditionInGroup": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "TestField",
                FilterParser.Keys.VALUE: "42",
                FilterParser.Keys.MEMBER_OF: "TestGroup"
            }
        },
        "AnotherTestConditionInGroup": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "DifferentTestField",
                FilterParser.Keys.VALUE: "23",
                FilterParser.Keys.MEMBER_OF: "TestGroup"
            }
        },
        "TestConditionInOtherGroup": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "OtherTestField",
                FilterParser.Keys.VALUE: "foo",
                FilterParser.Keys.MEMBER_OF: "OtherTestGroup"
            }
        },
        "TestConditionInRoot": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "YetAnotherTestField",
                FilterParser.Keys.VALUE: "bar",
            }
        },
        "TestGroup": {
            FilterParser.Keys.GROUP: {
                FilterParser.Keys.CONJUNCTION: "OR",
            }
        },
        "OtherTestGroup": {
            FilterParser.Keys.GROUP: {
                FilterParser.Keys.CONJUNCTION: "AND",
                FilterParser.Keys.MEMBER_OF: "TestGroup"
            }
        }
    }
    return filter_dict


def test_root_key_used_in_member_of(condition_class, group_class, example_context):
    filter_dict = {
        "TestGroup": {
            FilterParser.Keys.GROUP: {
                FilterParser.Keys.CONJUNCTION: "AND",
                FilterParser.Keys.MEMBER_OF: FilterParser.Keys.ROOT
            }
        },
    }
    with pytest.raises(RootKeyUsedError):
        filter_parser = FilterParser(filter_dict, condition_class, group_class, example_context)
        filter_parser.parse_filter_data()


def test_root_key_used_in_name(condition_class, group_class, example_context):
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
        filter_parser = FilterParser(filter_dict, condition_class, group_class, example_context)
        filter_parser.parse_filter_data()


def test_no_group_or_condition(condition_class, group_class, example_context):
    filter_dict = {
        "TestThingy": {
            "Thingy": {
                FilterParser.Keys.PATH: "TestField",
                FilterParser.Keys.VALUE: "42"
            }
        }
    }
    with pytest.raises(NoGroupOrCondition):
        filter_parser = FilterParser(filter_dict, condition_class, group_class, example_context)
        filter_parser.parse_filter_data()


def test_group_conditions(condition_class, group_class, valid_filter_dict, example_context):
    filter_parser = FilterParser(valid_filter_dict, condition_class, group_class, example_context)
    filter_parser._group_conditions()
    assert len(filter_parser.grouped_conditions) == 3

    assert FilterParser.Keys.ROOT in filter_parser.grouped_conditions
    assert "TestGroup" in filter_parser.grouped_conditions
    assert "OtherTestGroup" in filter_parser.grouped_conditions

    assert len(filter_parser.grouped_conditions[FilterParser.Keys.ROOT]["conditions"]) == 1
    assert len(filter_parser.grouped_conditions["TestGroup"]["conditions"]) == 2
    assert len(filter_parser.grouped_conditions["OtherTestGroup"]["conditions"]) == 1


def test_tree(condition_class, group_class, valid_filter_dict, example_context):
    filter_parser = FilterParser(valid_filter_dict, condition_class, group_class, example_context)
    result = filter_parser.parse_filter_data()
    evaluated_root_group = "(YetAnotherTestField = bar AND (TestField = 42 OR DifferentTestField = 23 OR (OtherTestField = foo)))"
    assert result == evaluated_root_group
