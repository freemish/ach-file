"""
Defines base RecordType class. Validates FieldDefinition arrays and instantiates Fields.
"""

from typing import Any, Dict, List, Optional

from ..constants import RECORD_SIZE
from .record_fields import Field, FieldDefinition


class InvalidRecordSizeError(Exception):
    """
    Raises when a RecordType's FieldDefinitions result in
    an invalid record size.
    """

    msg_format = (
        "FieldDefinition list for {} would result in an invalid record size"
        " of {} (valid record size is {})"
    )

    def __init__(
        self,
        record_type_class_name: str,
        invalid_record_size: int,
        valid_record_size: int = RECORD_SIZE,
    ):
        self.record_type_class_name = record_type_class_name
        self.invalid_record_size = invalid_record_size
        self.valid_record_size = valid_record_size
        self.message = self.msg_format.format(
            record_type_class_name, invalid_record_size, valid_record_size
        )
        super().__init__(self.message)


class InvalidRecordTypeParametersError(Exception):
    """
    Raises when a RecordType accepts an invalid parameter by keyword.
    """

    msg_format = "RecordType class {} received invalid kwargs on instantiation: {}"

    def __init__(self, record_type_class_name: str, invalid_kwargs: List[str]) -> None:
        self.record_type_class_name = record_type_class_name
        self.invalid_kwargs = invalid_kwargs
        self.message = self.msg_format.format(
            self.record_type_class_name, invalid_kwargs
        )
        super().__init__(self.message)


class RecordTypeAggregateFieldCreationError(Exception):
    """
    Raises after aggregating multiple Field creation exceptions.

    Attributes:
        errors: List[Exception] -- List of multiple errors that occurred when trying to create
            multiple Fields for a RecordType
        failed_keys: List[str] -- List of keys that failed to be set
        class_name: str -- Name of class where errors were encountered
    """

    msg_format = (
        "Encountered {} errors generating Fields for class {}; failed keys: {}; {}"
    )

    def __init__(
        self, class_name: str, errors: List[Exception], failed_keys: List[str]
    ):
        self.class_name = class_name
        self.errors = errors
        self.failed_keys = failed_keys
        self.message = self.msg_format.format(
            len(errors), self.class_name, failed_keys, errors
        )
        super().__init__(self.message)


class RecordType:
    """
    Base class for record types.
    Renders Fields as a record line by validating FieldDefinitions and generating Fields from them.
    """

    field_definition_dict: Dict[str, FieldDefinition] = {}

    def __init__(
        self,
        field_definition_dict: Optional[Dict[str, FieldDefinition]] = None,
        desired_record_size: int = RECORD_SIZE,
        **kwargs
    ):
        if field_definition_dict:
            self.field_definition_dict = field_definition_dict

        self._validate_field_definition_list(
            self.field_definition_dict, desired_record_size
        )
        self._validate_no_unknown_key_arguments(self.field_definition_dict, kwargs)

        self.fields: Dict[str, Field] = self._generate_fields_dict(
            self.field_definition_dict, kwargs
        )

    def render_record_line(self) -> str:
        """Render single record as a line in a valid ACH file."""
        result = ""
        for field in self.fields.values():
            result += field.value
        return result

    @classmethod
    def get_required_kwargs(cls) -> Dict[str, FieldDefinition]:
        """
        Get required kwargs that have no defaults set.
        Returns keys mapped to FieldDefinitions.
        """
        required_kwargs = {}
        for field_def_key, field_def in cls.field_definition_dict.items():
            if field_def.required and field_def.default is None:
                required_kwargs[field_def_key] = field_def
        return required_kwargs

    def get_field_value(self, field_name: str) -> str:
        """Get cleaned Field value of given field name."""
        return self.fields[field_name].value

    def get_field_values(self) -> Dict[str, str]:
        """
        Get all field names (keys) mapped to all cleaned Field values.
        """
        return {x: y.value for x, y in self.fields.items()}

    def set_field_value(
        self,
        key: str,
        value: Any,
        field_def_dict: Optional[Dict] = None,
        fields_dict: Optional[Dict] = None,
    ) -> None:
        """
        Set a new value on a single field after object creation.
        Raises InvalidRecordTypeParametersError if key does not exist in field definitions.
        """
        if field_def_dict is None:
            field_def_dict = self.field_definition_dict

        if fields_dict is None:
            fields_dict = self.fields

        if key not in field_def_dict:
            raise InvalidRecordTypeParametersError(type(self).__name__, [key])
        fields_dict[key] = Field(field_def_dict[key], value)

    def set_field_values(self, **kwargs) -> None:
        """
        Runs set_value_on_field for multiple key-value pairs for convenience,
        catching errors as it iterates.
        Raises RecordTypeAggregateFieldCreationError at the end if any errors were encountered.
        """
        failed_keys, exceptions = [], []
        for key, value in kwargs.items():
            self._catch_set_value_on_field_errors(failed_keys, exceptions, key, value)
        if failed_keys:
            raise RecordTypeAggregateFieldCreationError(
                type(self).__name__, exceptions, failed_keys
            ) from exceptions[0]

    def _generate_fields_dict(
        self, field_def_dict: Dict, kwargs: Dict
    ) -> Dict[str, Field]:
        fields = {}
        failed_keys, exceptions = [], []
        for key in field_def_dict:
            self._catch_set_value_on_field_errors(
                failed_keys,
                exceptions,
                key,
                kwargs.get(key),
                field_def_dict=field_def_dict,
                fields_dict=fields,
            )
        if exceptions:
            raise RecordTypeAggregateFieldCreationError(
                type(self).__name__, exceptions, failed_keys
            ) from exceptions[0]
        return fields

    def _catch_set_value_on_field_errors(
        self,
        failed_keys: List[str],
        exceptions: List[Exception],
        key: str,
        value: Any,
        **kwargs
    ) -> None:
        try:
            self.set_field_value(key, value, **kwargs)
        except Exception as exc:
            failed_keys.append(key)
            exceptions.append(exc)

    @classmethod
    def _validate_no_unknown_key_arguments(cls, field_def_dict: Dict, kwargs: Dict):
        invalid_kwargs = set(kwargs.keys()).difference(field_def_dict.keys())
        if invalid_kwargs:
            raise InvalidRecordTypeParametersError(cls.__name__, list(invalid_kwargs))

    @classmethod
    def _validate_field_definition_list(
        cls,
        field_definition_dict: Dict[str, FieldDefinition],
        desired_record_size: int = RECORD_SIZE,
    ) -> None:
        resulting_record_size = 0
        for field_def in field_definition_dict.values():
            resulting_record_size += field_def.length

        if resulting_record_size != desired_record_size:
            raise InvalidRecordSizeError(
                cls.__name__, resulting_record_size, desired_record_size
            )
