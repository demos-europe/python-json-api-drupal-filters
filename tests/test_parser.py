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


def test_context(condition_class, group_class):
    context = ExampleContext(paths=["name"], operators={"name": ["=", "~"]})

    filter_dict = {
        "TestConditionInRoot": {
            FilterParser.Keys.CONDITION: {
                FilterParser.Keys.PATH: "name",
                FilterParser.Keys.OPERATOR: "=",
                FilterParser.Keys.VALUE: "bar",
            }
        },
    }

    with pytest.raises(NoGroupOrCondition):
        filter_parser = FilterParser(filter_dict, condition_class, group_class)
        filter_parser.parse_filter_data()
