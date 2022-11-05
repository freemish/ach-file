"""Defines file control fields and record type."""

from typing import Dict

from record_types.constants import FILE_CONTROL_RECORD_TYPE_CODE
from record_types.record_fields import (
    AlphaNumFieldType,
    FieldDefinition,
    IntegerFieldType
)
from record_types.record_type_base import RecordType


class FileControlRecordType(RecordType):
    field_definition_dict: Dict[str, FieldDefinition] = {
        'record_type_code': FieldDefinition('Record Type Code', IntegerFieldType, length=1, default=FILE_CONTROL_RECORD_TYPE_CODE),
        'batch_count': FieldDefinition('Batch Count', IntegerFieldType, length=6),
        'block_count': FieldDefinition('Block Count', IntegerFieldType, length=6),
        'entry_and_addenda_count': FieldDefinition('Entry and Addenda Count', IntegerFieldType, length=8),
        'entry_hash': FieldDefinition('Entry Hash', IntegerFieldType, length=10),
        'total_debit_amount': FieldDefinition('Total Debit Amount', IntegerFieldType, length=12),
        'total_credit_amount': FieldDefinition('Total Credit Amount', IntegerFieldType, length=12),
        'reserved': FieldDefinition("Reserved Field", AlphaNumFieldType, length=39, required=False),
    }

    def __init__(
        self,
        batch_count: int,
        block_count: int,
        entry_and_addenda_count: int,
        entry_hash: int,
        total_debit_amount: int,
        total_credit_amount: int,
        **kwargs
    ):
        kwargs['batch_count'] = batch_count
        kwargs['block_count'] = block_count
        kwargs['entry_and_addenda_count'] = entry_and_addenda_count
        kwargs['entry_hash'] = entry_hash
        kwargs['total_debit_amount'] = total_debit_amount
        kwargs['total_credit_amount'] = total_credit_amount
        super().__init__(**kwargs)
