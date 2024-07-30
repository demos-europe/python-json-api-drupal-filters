from typing import TypedDict

import pytest

from json_api_drupal_filters import DrupalFilter
from json_api_drupal_filters.filter_parser import FilterParser
from json_api_drupal_filters.filter_tree import Condition, Group


class ExampleContext(TypedDict):
    mapping: dict[str, str]


class ExampleFilter(DrupalFilter[ExampleContext]):
    after: int = 0
    before: int = 0

    def before_parsing(self, filter_dict: dict, context: ExampleContext):
        self.before += 1

    def after_parsing(self, result, context: ExampleContext):
        self.after += 1


class ExampleCondition(Condition):
    def evaluate(self, context: ExampleContext):
        path = context["mapping"].get(self.path, self.path)
        return f"{path} {self.operator} {self.value}"


class ExampleGroup(Group):
    def evaluate(self, context: ExampleContext):
        return "(" + f" {self.conjunction} ".join([member.evaluate(context) for member in self.members]) + ")"


@pytest.fixture
def filter() -> ExampleFilter:
    return ExampleFilter(ExampleCondition, ExampleGroup)


def test_before_and_after_parsing(filter: ExampleFilter):
    context = ExampleContext(mapping={"$old_path": "new_path"})

    filter_dict = {}
    filter.parse(filter_dict, context)

    assert len(filter_dict) == 0
    assert filter.after == 1
    assert filter.before == 1


def test_context(filter):
    context = ExampleContext(mapping={
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

    filter_parser = FilterParser(filter_dict, ExampleCondition, ExampleGroup, context)
    res = filter_parser.parse_filter_data()
    assert res == "(def = bar)"
