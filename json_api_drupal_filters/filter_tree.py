from abc import ABC, abstractmethod, ABCMeta
from typing import Generic, TypeVar, Literal, Protocol

Context = TypeVar("Context", contravariant=True)


class FilterTreeElement(Protocol[Context]):

    def evaluate(self, context: Context):
        ...


class Condition(FilterTreeElement[Context]):
    """
    Concrete implementations of the Condition class should derive from this class.
    The evaluate method should return a string or object that can be interpreted by
    the data layer of your application.
    """
    default_operator = '='

    def __init__(self, **kwargs):
        self.path = kwargs["path"]
        self.operator = kwargs["operator"] if "operator" in kwargs else self.default_operator
        self.value = kwargs["value"]


class Group(FilterTreeElement[Context]):
    """
    Concrete implementations of the Group class should derive from this class.
    The members list will include other FilterTreeElement objects (Conditions or other Groups).
    The evaluate method should return a string or object that combines the return values of
    all members' evaluate methods based on the conjunction, such that calling evaluate() on the
    root group of a tree of filters will eventually evaluate all subgroups and conditions.
    """
    members: list[FilterTreeElement[Context]] = []

    def __init__(self, conjunction: Literal["AND", "OR"]):
        self.members = []
        self.conjunction = conjunction.upper()
