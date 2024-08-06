from typing import Generic, Any
from json_api_drupal_filters.filter_parser import ParsingContext, FilterParser
from json_api_drupal_filters.filter_tree import Condition, Group


class DrupalFilter(Generic[ParsingContext]):
    """A base class for customizing filter parsing behavior"""
    def __init__(self, condition: type[Condition[ParsingContext]], group: type[Group[ParsingContext]]):
        self.group = group
        self.condition = condition


    def before_parsing(self, filter_dict: dict, context: ParsingContext):  # noqa: ARG002
        """
        called before parsing.
        Can be implemented in a subclass to modify filter_dict or context before parsing
        """
        ...

    def after_parsing(self, result: Any, context: ParsingContext):  # noqa: ARG002
        """
        called after the parser has successfully parsed `result`
        Can be implemented in a subclass to modify the result
        """
        ...

    def parse(self, filter_dict: dict, context: ParsingContext) -> Any:
        """ calls before parsing, parsing and then after parsing """
        self.before_parsing(filter_dict, context)
        parser = FilterParser[ParsingContext](
            filter_dict=filter_dict,
            condition_class=self.condition,
            group_class=self.group,
            context=context,
        )
        result = parser.parse_filter_data()
        self.after_parsing(result, context)
        return result

