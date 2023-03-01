import pytest

from json_api_drupal_filters.filter_parser import FilterParser
from json_api_drupal_filters.filter_tree import Condition, Group
from json_api_drupal_filters.filter_errors import *


@pytest.fixture()
def condition_class():
    class TestCondition(Condition):
        def evaluate(self):
            return self
    return TestCondition


@pytest.fixture()
def group_class():
    class TestGroup(Group):
        def evaluate(self):
            return [member.evaluate for member in self.members]
    return TestGroup


def test_root_key_used_in_member_of(condition_class, group_class):
    filter_dict = {
        "testGroup": {
            FilterParser.Keys.GROUP: {
                FilterParser.Keys.CONJUNCTION: "AND",
                FilterParser.Keys.MEMBER_OF: FilterParser.Keys.ROOT
            }
        },
    }
    with pytest.raises(RootKeyUsedError):
        filter_parser = FilterParser(filter_dict, condition_class, group_class)
        filter_parser.parse_filter_data()


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
                FilterParser.Keys.CONJUNCTION: "OR"
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
