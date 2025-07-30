from abc import ABC, abstractmethod

from astroid import ClassDef, InferenceError, NameInferenceError
from pylint.lint import PyLinter

from . import util


class BookRule(ABC):
    @abstractmethod
    def check_rule(self, linter: PyLinter, node: ClassDef) -> None:
        pass


class TagsRule(BookRule):
    def check_rule(self, linter: PyLinter, node: ClassDef) -> None:
        decorator = util.get_decorator_by_name(node, "kognitos.bdk.decorators.book_decorator.book")
        if not decorator:
            return

        if not hasattr(decorator, "keywords") or len(decorator.keywords) == 0:
            linter.add_message(
                "book-missing-tags",
                args=node.repr_name(),
                node=node,
            )
            return

        tags_keyword = next(filter(lambda x: x.arg == "tags", decorator.keywords), None)

        if not tags_keyword:
            linter.add_message(
                "book-missing-tags",
                args=node.repr_name(),
                node=node,
            )
            return

        try:
            tags_value = next(tags_keyword.value.infer())
            if not hasattr(tags_value, "elts") or not isinstance(tags_value.elts, list):
                linter.add_message(
                    "book-tags-not-list",
                    args=node.repr_name(),
                    node=tags_keyword.value,
                )
                return

        except (InferenceError, NameInferenceError):
            linter.add_message(
                "book-tags-not-list",
                args=node.repr_name(),
                node=tags_keyword.value,
            )
            return

        bad_naming_tags = []
        for tag_element in tags_value.elts:
            try:
                tag_value = next(tag_element.infer()).value
                if isinstance(tag_value, str) and not tag_value.istitle():
                    bad_naming_tags.append(tag_value)
            except (InferenceError, NameInferenceError):
                continue

        if bad_naming_tags:
            linter.add_message(
                "tags-bad-naming",
                args=(node.repr_name(), ", ".join(bad_naming_tags)),
                node=tags_keyword.value,
            )
