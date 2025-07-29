import ast
import tokenize
from collections.abc import Iterator
from typing import TypeVar

from flake8_digit_separator import __version__ as version
from flake8_digit_separator.classifiers.registry import ClassifierRegistry
from flake8_digit_separator.error import Error
from flake8_digit_separator.fds_numbers.types import FDSNumbersAlias
from flake8_digit_separator.types import ErrorMessage
from flake8_digit_separator.validators.registry import ValidatorRegistry

SelfChecker = TypeVar('SelfChecker', bound='Checker')


class Checker:
    """Flake8 plugin checker for digit separator violations in numeric literals.

    This checker processes Python source code tokens to identify numeric literals
    and validates that they follow proper digit separator conventions. It classifies
    different types of numbers (integers, floats, binary, hex, octal, etc.) and
    applies appropriate validation rules to ensure consistent formatting.
    """

    name = version.NAME
    version = version.VERSION

    def __init__(
        self,
        tree: ast.AST,  # noqa: ARG002
        file_tokens: list[tokenize.TokenInfo],
    ) -> None:
        self.file_tokens = file_tokens

    def run(self) -> Iterator[ErrorMessage]:
        """Entry point and start of validation.

        1. Check that the token is a number.
        2. Classify the token.
        3. Validate the token.
        4. Display an error.

        :yield: FDS rule that was broken.
        :rtype: Iterator[ErrorMessage]
        """
        for token in self.file_tokens:
            if token.type == tokenize.NUMBER:
                error = self._process_number_token(token)
                if error:
                    yield error.as_tuple()

    def _process_number_token(
        self,
        token: tokenize.TokenInfo,
    ) -> Error | None:
        number = self._classify(token)

        if number:
            if not number.is_supported:
                return None

            validator = ValidatorRegistry.get_validator(number)
            if validator.validate():
                return None

            return Error(
                line=token.start[0],
                column=token.start[1],
                message=validator.error_message,
                object_type=type(self),
            )

        return None

    def _classify(self, token: tokenize.TokenInfo) -> FDSNumbersAlias | None:
        classifiers = ClassifierRegistry.get_ordered_classifiers()
        number = None
        for classifier in classifiers:
            number = classifier(token.string).classify()
            if number:
                break

        return number if number else None
