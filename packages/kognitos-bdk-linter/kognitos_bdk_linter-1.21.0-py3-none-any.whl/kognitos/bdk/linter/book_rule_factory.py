from abc import ABC, abstractmethod
from typing import List

from .book_rules import BookRule, TagsRule


class BookRuleFactory(ABC):
    @abstractmethod
    def get_rules(self) -> List[BookRule]:
        pass


class DefaultBookRuleFactory(BookRuleFactory):
    def get_rules(self) -> List[BookRule]:
        return [TagsRule()]
