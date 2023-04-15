"""Defines file header fields and record type."""

from typing import Dict

from ..constants import (
    AutoDateInput,
    FILE_HEADER_BLOCKING_FACTOR,
    FILE_HEADER_DEFAULT_FILE_ID_MODIFIER,
    FILE_HEADER_FORMAT_CODE,
    FILE_HEADER_PRIORITY_CODE,
    FILE_HEADER_RECORD_TYPE_CODE,
    RECORD_SIZE,
)
from .record_fields import (
    AlphaNumFieldType,
    BlankPaddedRoutingNumberFieldType,
    DateFieldType,
    TimeFieldType,
    FieldDefinition,
    IntegerFieldType,
)
from .record_type_base import RecordType


# pylint: disable=line-too-long
class FileHeaderRecordType(RecordType):
    """Defines all fields of a file header record line of an ACH file."""

    field_definition_dict: Dict[str, FieldDefinition] = {
        "record_type_code": FieldDefinition(
            "Record Type Code",
            IntegerFieldType,
            length=1,
            default=FILE_HEADER_RECORD_TYPE_CODE,
        ),
        "priority_code": FieldDefinition(
            "Priority Code",
            IntegerFieldType,
            length=2,
            default=FILE_HEADER_PRIORITY_CODE,
        ),
        "destination_routing": FieldDefinition(
            "Immediate Destination Routing",
            BlankPaddedRoutingNumberFieldType,
            length=10,
            auto_correct_input=True,
        ),
        "company_identification": FieldDefinition(
            "Company Identification Number", IntegerFieldType, length=10
        ),
        "file_creation_date": FieldDefinition(
            "File Creation Date",
            DateFieldType,
            length=6,
            auto_correct_input=True,
            default=AutoDateInput.NOW,
        ),
        "file_creation_time": FieldDefinition(
            "File Creation Time", TimeFieldType, length=4, required=False
        ),
        "file_id_modifier": FieldDefinition(
            "File ID Modifier",
            AlphaNumFieldType,
            length=1,
            default=FILE_HEADER_DEFAULT_FILE_ID_MODIFIER,
        ),
        "record size": FieldDefinition(
            "Record Size", IntegerFieldType, length=3, default=RECORD_SIZE
        ),
        "blocking_factor": FieldDefinition(
            "Blocking Factor",
            IntegerFieldType,
            length=2,
            default=FILE_HEADER_BLOCKING_FACTOR,
        ),
        "format_code": FieldDefinition(
            "Format Code", IntegerFieldType, length=1, default=FILE_HEADER_FORMAT_CODE
        ),
        "destination_name": FieldDefinition(
            "Destination Financial Institution Name", AlphaNumFieldType, length=23
        ),
        "origin_name": FieldDefinition(
            "Origin Financial Institution Name", AlphaNumFieldType, length=23
        ),
        "reference_code": FieldDefinition(
            "Reference Code Or Empty String", AlphaNumFieldType, length=8, default=""
        ),
    }

    def __init__(
        self,
        destination_routing: str,
        company_identification: str,
        destination_name: str,
        origin_name: str,
        **kwargs
    ):
        self.field_definition_dict = self.field_definition_dict
        kwargs["destination_routing"] = destination_routing
        kwargs["company_identification"] = company_identification
        kwargs["destination_name"] = destination_name
        kwargs["origin_name"] = origin_name
        super().__init__(**kwargs)
