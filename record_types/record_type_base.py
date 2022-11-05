"""
Defines base RecordType class. Validates FieldDefinition arrays and instantiates Fields.
"""

from typing import Dict, List, Optional
from .constants import RECORD_SIZE
from .record_fields import Field, FieldDefinition


class InvalidRecordSizeError(Exception):
    """
    Raises when a RecordType's FieldDefinitions result in an invalid record size.
    """
    msg_format = "FieldDefinition list for {} would result in an invalid record size of {} (valid record size is {})"

    def __init__(self, record_type_class_name: str, invalid_record_size: int, valid_record_size: int = RECORD_SIZE):
        self.record_type_class_name = record_type_class_name
        self.invalid_record_size = invalid_record_size
        self.valid_record_size = valid_record_size
        self.message = self.msg_format.format(record_type_class_name, invalid_record_size, valid_record_size)
        super().__init__(self.message)


class InvalidRecordTypeParametersError(Exception):
    """
    Raises when a RecordType accepts an invalid parameter by keyword.
    """
    msg_format = "RecordType class {} received invalid kwargs on instantiation: {}"

    def __init__(self, record_type_class_name: str, invalid_kwargs: List[str]) -> None:
        self.record_type_class_name = record_type_class_name
        self.invalid_kwargs = invalid_kwargs
        self.message = self.msg_format.format(self.record_type_class_name, invalid_kwargs)
        super().__init__(self.message)


class RecordType:
    """
    Base class for record types.
    Renders Fields as a record line by validating FieldDefinitions and generating Fields from them.
    """
    field_definition_dict: Dict[str, FieldDefinition] = {}

    def __init__(self, field_definition_dict: Optional[Dict[str, FieldDefinition]] = None, desired_record_size: int = RECORD_SIZE, **kwargs):
        if field_definition_dict:
            self.field_definition_dict = field_definition_dict
        
        self._validate_field_definition_list(self.field_definition_dict, desired_record_size)
        self._validate_no_unknown_key_arguments(self.field_definition_dict, kwargs)

        self.fields: Dict[str, Field] = self._generate_fields_dict(self.field_definition_dict, kwargs)

    def render_record_line(self) -> str:
        result = ''
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

    @staticmethod
    def _generate_fields_dict(field_def_dict: Dict, kwargs: Dict) -> Dict[str, Field]:
        fields = {}
        for field_def_key, field_def in field_def_dict.items():
            fields[field_def_key] = Field(field_def, value=kwargs.get(field_def_key))
        return fields

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
            raise InvalidRecordSizeError(cls.__name__, resulting_record_size, desired_record_size)
