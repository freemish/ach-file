"""Defines file control fields and record type."""

from typing import Dict

from ..constants import FILE_CONTROL_RECORD_TYPE_CODE
from .record_fields import AlphaNumFieldType, FieldDefinition, IntegerFieldType
from .record_type_base import RecordType


# pylint: disable=line-too-long
class FileControlRecordType(RecordType):
    """Defines all fields of the file control record line in an ACH file."""

    field_definition_dict: Dict[str, FieldDefinition] = {
        "record_type_code": FieldDefinition(
            "Record Type Code",
            IntegerFieldType,
            length=1,
            default=FILE_CONTROL_RECORD_TYPE_CODE,
        ),
        "batch_count": FieldDefinition("Batch Count", IntegerFieldType, length=6),
        "block_count": FieldDefinition("Block Count", IntegerFieldType, length=6),
        "entry_and_addenda_count": FieldDefinition(
            "Entry and Addenda Count", IntegerFieldType, length=8
        ),
        "entry_hash": FieldDefinition("Entry Hash", IntegerFieldType, length=10),
        "total_debit_amount": FieldDefinition(
            "Total Debit Amount", IntegerFieldType, length=12
        ),
        "total_credit_amount": FieldDefinition(
            "Total Credit Amount", IntegerFieldType, length=12
        ),
        "reserved": FieldDefinition(
            "Reserved Field", AlphaNumFieldType, length=39, required=False
        ),
    }
