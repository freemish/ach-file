"""Defines addenda fields and record type."""

from typing import Dict

from .constants import (
    ADDENDA_DEFAULT_SEQUENCE_NUMBER,
    ADDENDA_RECORD_TYPE_CODE,
    ADDENDA_TYPE_CODE
)
from .record_fields import (
    AlphaNumFieldType,
    FieldDefinition,
    IntegerFieldType
)
from .record_type_base import RecordType


class AddendaRecordType(RecordType):
    field_definition_dict: Dict[str, FieldDefinition] = {
        'record_type_code': FieldDefinition('Record Type Code', IntegerFieldType, length=1, default=ADDENDA_RECORD_TYPE_CODE),
        'addenda_type_code': FieldDefinition('Addenda Type Code', IntegerFieldType, length=2, default=ADDENDA_TYPE_CODE),
        'payment_related_information': FieldDefinition('Payment Related Information', AlphaNumFieldType, length=80, required=False),
        'addenda_sequence_number': FieldDefinition('Addenda Sequence Number', IntegerFieldType, length=4, default=ADDENDA_DEFAULT_SEQUENCE_NUMBER),
        'entry_detail_sequence_number': FieldDefinition('Entry Detail Sequence Number', IntegerFieldType, length=7),
    }

    def __init__(self, payment_related_information: str, entry_detail_sequence_number: int, **kwargs):
        kwargs['payment_related_information'] = payment_related_information
        kwargs['entry_detail_sequence_number'] = entry_detail_sequence_number
        super().__init__(**kwargs)
