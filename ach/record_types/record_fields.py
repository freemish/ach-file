"""
Fields and FieldType classes.
"""

import datetime
import re
from contextlib import suppress
from enum import Enum
from typing import Optional, Union

from ..constants import AutoDateInput


class ValueMismatchesFieldTypeError(Exception):
    """
    Raised when a string mismatches a FieldType.

    Attributes:
        msg_format: str -- Message containing "{}" to indicate where string arguments
            can be formatted dynamically on instantiation
        value: str -- Value passed in to be validated as a particular FieldType
        field_type_or_regex: str -- Descriptive string indicating either the regex
            or type of field that the value mismatched
        message: Message displayed when exception is raised
    """
    msg_format = "Passed-in value \"{}\" mismatches {}"

    def __init__(self, value: str, field_type_or_regex: str):
        self.value = value
        self.field_type_or_regex = field_type_or_regex
        self.message = self.msg_format.format(self.value, self.field_type_or_regex)
        super().__init__(self.message)


class EmptyRequiredFieldError(Exception):
    """
    Raised when a Field is required, has no default, and does not receive a value.

    Attributes:
        msg_format: str -- Message containing "{}" to indicate where string arguments
            can be formatted dynamically on instantiation
        field_name: str -- Pretty name of FieldDefinition with missing value
        message: Message displayed when exception is raised
    """
    msg_format = "Field {} requires a value and there is no default in its definition"

    def __init__(self, field_name: str):
        self.field_name = field_name
        self.message = self.msg_format.format(field_name)
        super().__init__(self.message)


class Alignment(Enum):
    """Represents whether a field type should be aligned left or right."""
    LEFT = 0
    RIGHT = 1

    def align(self, input_string: str, length: int, padding: str) -> str:
        """
        Aligns text to the left or right of a given string length,
        using padding to fill any gaps if input string is shorter than length.
        """
        justify_method = {
            Alignment.LEFT: str.ljust,
            Alignment.RIGHT: str.rjust,
        }.get(self)
        return justify_method(input_string, length, padding)

    def truncate(self, input_string: str, length: int) -> str:
        """
        Truncates a string longer than length to equal length.
        If left-aligned, truncates right side; if right-aligned,
        truncates left side.
        """
        if self == Alignment.LEFT:
            return input_string[:length]
        return input_string[-length:]


class FieldType:
    """
    Base class for FieldType.

    Attributes:
        padding: str -- Filler for fixed-width string
        alignment: Alignment -- Original string should be oriented
            either left or right in fixed-width string
        regex: Optional[re.Pattern] -- pattern against which original string
            should be validated
    """
    padding: str
    alignment: Alignment
    regex: Optional[re.Pattern]
    auto_correct: bool

    @classmethod
    def apply_fixed_length(cls, input_string: str, length: int) -> str:
        """Adds padding for short strings and truncates long ones."""
        input_string = cls.alignment.align(input_string, length, cls.padding)
        return cls.alignment.truncate(input_string, length)

    @classmethod
    def should_correct_input(cls, auto_correct_override: Optional[bool]) -> bool:
        """Return True if auto_correct is True, else False if input is not to be changed."""
        return auto_correct_override if auto_correct_override is not None else cls.auto_correct

    # pylint: disable=unused-argument
    @classmethod
    def correct_input(cls, input_string: str, auto_correct_override: Optional[bool] = None) -> str:
        """Correct input to only contain characters that would pass regex check."""
        return input_string

    @classmethod
    def is_valid(cls, input_string: str, *args, raise_exc: bool = False, **kwargs) -> bool:
        """
        Returns True if input is valid, else False.
        Raises exc instead of return False if raise_exc.
        """
        exc = None
        try:
            cls.do_validation(input_string, *args, **kwargs)
        except Exception as validation_exc:
            exc = validation_exc

        if not exc:
            return True
        if not raise_exc:
            return False
        raise exc

    @classmethod
    def do_validation(cls, input_string: str, *args, **kwargs) -> None:
        """
        Validates input string. If invalid, raises exception, else returns None.
        """
        if not cls.regex:
            return
        is_match = input_string == getattr(re.match(cls.regex, input_string), 'string', '')
        if not is_match:
            raise ValueMismatchesFieldTypeError(input_string, cls.regex.pattern or cls.__name__)


class IntegerFieldType(FieldType):
    """Represents an integer field type. Pads number strings with leading 0s."""
    padding: str = '0'
    alignment: Alignment = Alignment.RIGHT
    regex: re.Pattern = re.compile(r'^\d+$')
    auto_correct: bool = False


class AlphaNumFieldType(FieldType):
    """Represents an alphanumeric field type. Pads strings with trailing spaces."""
    padding: str = ' '
    alignment: Alignment = Alignment.LEFT
    regex: re.Pattern = re.compile(r'^[A-Za-z0-9./()&\'\s-]+$')
    auto_correct: bool = True

    @classmethod
    def correct_input(cls, input_string: str, auto_correct_override: Optional[bool] = None) -> str:
        """
        Replaces all characters not present in class's regex pattern with an empty string.
        """
        if not cls.should_correct_input(auto_correct_override):
            return input_string
        return re.sub( re.compile(r'[^A-Za-z0-9./()&\'\s-]'), '', input_string)


class BlankPaddedRoutingNumberFieldType(IntegerFieldType):
    """Represents a routing number padded with a leading blank space."""
    padding: str = ' '
    regex: re.Pattern = re.compile(r'^\s?\d{9}$')
    auto_correct: bool = True

    @classmethod
    def correct_input(cls, input_string: str, auto_correct_override: Optional[bool] = None) -> str:
        if not cls.should_correct_input(auto_correct_override):
            return input_string
        if not cls.auto_correct:
            return input_string
        if not input_string:
            return ''
        if cls.is_valid(input_string):
            return input_string
        if input_string.lstrip().isdigit():
            return Alignment.RIGHT.align(input_string, 9, '0')
        return input_string


class DateFieldType(AlphaNumFieldType):
    """
    Accepts 6 digits representing a valid date OR generates a date
    given a datetime.date, a datetime.datetime, or an AutoDateInput string.
    If not required, pads with blanks.
    """
    regex: re.Pattern = re.compile(r'^\d{6}$')
    auto_correct: bool = True

    @classmethod
    def correct_input(cls, input_string: str, auto_correct_override: Optional[bool] = None) -> str:
        if not cls.should_correct_input(auto_correct_override) or cls.is_valid(input_string):
            return input_string

        if input_string.upper() == AutoDateInput.NOW.value:
            return datetime.date.today().strftime('%y%m%d')

        if input_string.upper() == AutoDateInput.TOMORROW.value:
            return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%y%m%d')

        with suppress(ValueError):
            return datetime.datetime.fromisoformat(input_string).strftime('%y%m%d')

        with suppress(ValueError):
            return datetime.date.fromisoformat(input_string).strftime('%y%m%d')

        return input_string

    @classmethod
    def do_validation(cls, input_string: str, *args, **kwargs) -> None:
        if not input_string or not input_string.strip():
            return
        try:
            super().do_validation(input_string, *args, **kwargs)
        except Exception as exc:
            raise exc from exc
        datetime.date(2000 + int(input_string[:2]), int(input_string[2:4]), int(input_string[4:6]))


class TimeFieldType(AlphaNumFieldType):
    """
    Accepts 4 digits representing military time hours and minutes
    OR generates a time given a datetime.datetime or AutoDateInput string.
    """
    regex: re.Pattern = re.compile(r'^\d{4}$')
    auto_correct: bool = True

    @classmethod
    def correct_input(cls, input_string: str, auto_correct_override: Optional[bool] = None) -> str:
        if not cls.should_correct_input(auto_correct_override) or cls.is_valid(input_string):
            return input_string

        if input_string.upper() == AutoDateInput.NOW.value:
            return datetime.datetime.now().strftime('%H%M')

        if input_string.upper() == AutoDateInput.TOMORROW.value:
            return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%H%M')

        with suppress(ValueError):
            return datetime.datetime.fromisoformat(input_string).strftime('%H%M')

        with suppress(ValueError):
            return datetime.date.fromisoformat(input_string).strftime('%H%M')

        return input_string

    @classmethod
    def do_validation(cls, input_string: str, *args, **kwargs) -> None:
        if not input_string or not input_string.strip():
            return
        try:
            super().do_validation(input_string, *args, **kwargs)
        except Exception as exc:
            raise exc

        datetime.time(int(input_string[:2]), int(input_string[2:]))


class FieldDefinition:
    """
    Represents a definition of a piece of data within a record.

    Attributes:
        field_name: str -- pretty name of a field within a record,
            like "record_code"
        field_type: FieldType -- indicates the type of input that can be
            accepted in a Field with this given FieldDefinition
        length: int -- length of field
            (when original input is padded, aligned, corrected)
        required: bool -- whether value needs to be non-blank
        default: Optional[str] -- if no value is provided to Field,
            defines what is automatically set as the Field's value
    """
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        field_name: str,
        field_type: FieldType,
        length: int,
        required: bool = True,
        default: Optional[Union[str, int]] = None,
        auto_correct_input: Optional[bool] = None,
    ):
        self.field_name = field_name
        self.field_type = field_type
        self.length = length
        self.required = required
        self.default = str(default) if default is not None else None
        self.auto_correct_input = auto_correct_input

    # pylint: disable=consider-using-f-string
    def __repr__(self) -> str:
        return '<{}: {} [{}]>'.format(
            type(self).__name__, self.field_name, self.field_type.__name__)

    def correct_input(self, input_string: str) -> str:
        """Corrects input according to current setting and FieldType default setting."""
        return self.field_type.correct_input(input_string, self.auto_correct_input)

    def is_valid(self, input_string: str, *args, raise_exc: bool = True, **kwargs) -> bool:
        """
        Returns True if string is valid, else False.
        If raise_exc, raises an exception instead of returning False.
        """
        return self.field_type.is_valid(input_string, *args, raise_exc=raise_exc, **kwargs)

    def get_fixed_width_value(self, input_string: str) -> str:
        """Convert input string to fixed length according to its FieldType."""
        return self.field_type.apply_fixed_length(input_string, self.length)


class Field:
    """
    Represents a value adhering to a field definition.
    Access cleaned value with .value property.

    Attributes:
        field_definition: FieldDefinition -- defines properties of a field
            in a record
        original_value: Optional[str] -- raw value passed into field before
            alignments and corrections
        cleaned_value: str: Setting this attribute interrupts initialization
            if raw input value is invalid
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, field_definition: FieldDefinition, value: Optional[str] = None):
        self.field_definition = field_definition
        self.original_value = value
        self.value = value

    @property
    def value(self) -> str:
        """Return cleaned value of field (not original value)."""
        return self.cleaned_value

    @value.setter
    def value(self, raw_value: str) -> None:
        """Set a new cleaned value on this Field."""
        self.cleaned_value = Field._create_cleaned_value(self.field_definition, raw_value)

    @staticmethod
    def _create_cleaned_value(field_definition: FieldDefinition, value: Optional[str] = None):
        Field._validate_required_value_not_empty(field_definition, value)

        ret_value: str = ''
        if isinstance(value, (datetime.date, datetime.datetime)):
            ret_value = value.isoformat()
        ret_value = str(field_definition.default or '') if value is None else str(value)

        ret_value = field_definition.correct_input(ret_value)

        field_definition.is_valid(ret_value, raise_exc=True)
        return field_definition.get_fixed_width_value(ret_value)

    @staticmethod
    def _validate_required_value_not_empty(
        field_definition: FieldDefinition, value: Optional[str]) -> None:
        if value is None and field_definition.required and field_definition.default is None:
            raise EmptyRequiredFieldError(field_definition.field_name)
