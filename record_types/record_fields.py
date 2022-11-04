"""
Fields and FieldType classes.
"""

import re
from enum import Enum
from typing import Optional, Union


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

    def align(self, s: str, length: int, padding: str) -> str:
        justify_method = {
            Alignment.LEFT: str.ljust,
            Alignment.RIGHT: str.rjust,
        }.get(self)
        return justify_method(s, length, padding)

    def truncate(self, s: str, length: int) -> str:
        if self == Alignment.LEFT:
            return s[:length]
        return s[-length:]


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

    @classmethod
    def apply_fixed_length(cls, s: str, length: int) -> str:
        """Adds padding for short strings and truncates long ones."""
        s = cls.alignment.align(s, length, cls.padding)
        return cls.alignment.truncate(s, length)

    @classmethod
    def correct_input(cls, s: str) -> str:
        """TODO: Correct input to only contain characters that would pass regex check."""
        return s

    @classmethod
    def is_valid(cls, s: str, raise_exc: bool = False, *args, **kwargs) -> bool:
        exc = cls.do_validation(s, *args, **kwargs)
        if not exc:
            return True
        if not raise_exc:
            return False
        raise exc

    @classmethod
    def do_validation(cls, s: str, *args, **kwargs) -> Optional[Exception]:
        if not cls.regex:
            return None
        is_match = s == getattr(re.match(cls.regex, s), 'string', '')
        if not is_match:
            return ValueMismatchesFieldTypeError(s, cls.regex.pattern or cls.__name__)


class IntegerFieldType(FieldType):
    """Represents an integer field type. Pads number strings with leading 0s."""
    padding: str = '0'
    alignment: Alignment = Alignment.RIGHT
    regex: re.Pattern = re.compile(r'^\d+$')


class AlphaNumFieldType(FieldType):
    """Represents an alphanumeric field type. Pads strings with trailing spaces."""
    padding: str = ' '
    alignment: Alignment = Alignment.LEFT
    regex: re.Pattern = re.compile(r'^[A-Za-z0-9./()&\'\s-]+$')


class BlankPaddedRoutingNumberFieldType(IntegerFieldType):
    """Represents a routing number padded with a leading blank space."""
    padding: str = ' '
    regex: re.Pattern = re.compile(r'^\s?\d{9}$')


class FieldDefinition:
    """
    Represents a definition of a piece of data within a record.

    Attributes:
        field_name: str -- pretty name of a field within a record, like "record_code"
        field_type: FieldType -- indicates the type of input that can be accepted
            in a Field with this given FieldDefinition
        length: int -- length of field (when original input is padded, aligned, corrected)
        required: bool -- whether value needs to be non-blank
        default: Optional[str] -- if no value is provided to Field, defines what is automatically set
            as the Field's value
    """
    def __init__(self, field_name: str, field_type: FieldType, length: int,
            required: bool = True,
            default: Optional[Union[str, int]] = None,
            auto_correct_input: bool = False,
        ):
        self.field_name = field_name
        self.field_type = field_type
        self.length = length
        self.required = required
        self.default = str(default) if default is not None else None
        self.auto_correct_input = auto_correct_input
    
    def correct_input(self, s: str) -> str:
        return self.field_type.correct_input(s)
    
    def is_valid(self, s: str, raise_exc: bool = True, *args, **kwargs) -> bool:
        return self.field_type.is_valid(s, raise_exc=raise_exc, *args, **kwargs)

    def get_fixed_width_value(self, s: str) -> str:
        return self.field_type.apply_fixed_length(s, self.length)


class Field:
    """
    Represents a value adhering to a field definition.
    Access cleaned value with .value property.

    Attributes:
        field_definition: FieldDefinition -- defines properties of a field in a record
        original_value: Optional[str] -- raw value passed into field before alignments and corrections
        cleaned_value: str: Setting this attribute interrupts initialization if raw input value is invalid
    """
    def __init__(self, field_definition: FieldDefinition, value: Optional[str] = None):
        self.field_definition = field_definition
        self.original_value = value
        self.cleaned_value = Field.create_cleaned_value(field_definition, value)
    
    @property
    def value(self) -> str:
        return self.cleaned_value

    @staticmethod
    def create_cleaned_value(field_definition: FieldDefinition, value: Optional[str] = None):
        Field._validate_required_value_not_empty(field_definition, value)
        ret_value = str(value or field_definition.default or '')

        if field_definition.auto_correct_input:
            ret_value = field_definition.correct_input(ret_value)

        field_definition.is_valid(ret_value, raise_exc=True)
        return field_definition.get_fixed_width_value(ret_value)
    
    @staticmethod
    def _validate_required_value_not_empty(field_definition: FieldDefinition, value: Optional[str]) -> None:
        if value is None and field_definition.required and field_definition.default is None:
            raise EmptyRequiredFieldError(field_definition.field_name)
