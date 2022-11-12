"""Defines batch control fields and record type."""

from typing import Dict

from ..constants import (
    BATCH_CONTROL_RECORD_TYPE_CODE,
    BATCH_DEFAULT_SERVICE_CLASS_CODE
)
from .record_fields import (
    AlphaNumFieldType,
    FieldDefinition,
    IntegerFieldType
)
from .record_type_base import RecordType


# pylint: disable=line-too-long
class BatchControlRecordType(RecordType):
    """Define all fields of a batch control record line of an ACH file."""
    field_definition_dict: Dict[str, FieldDefinition] = {
        'record_type_code': FieldDefinition('Record Type Code', IntegerFieldType, length=1, default=BATCH_CONTROL_RECORD_TYPE_CODE),
        'service_class_code': FieldDefinition('Service Class Code', IntegerFieldType, length=3, default=BATCH_DEFAULT_SERVICE_CLASS_CODE),
        'entry_and_addenda_count': FieldDefinition('Entry and Addenda Count', IntegerFieldType, length=6),
        'entry_hash': FieldDefinition('Entry Hash', IntegerFieldType, length=10),
        'total_debit_amount': FieldDefinition('Total Debit Amount', IntegerFieldType, length=12),
        'total_credit_amount': FieldDefinition('Total Credit Amount', IntegerFieldType, length=12),
        'company_identification': FieldDefinition('Company Identification', IntegerFieldType, length=10),
        'message_authentication_code': FieldDefinition('Message Authentication Code', AlphaNumFieldType, length=19, required=False),
        'reserved': FieldDefinition('Reserved Space', AlphaNumFieldType, length=6, required=False),
        'odfi_identification': FieldDefinition('ODFI Identification (First 8 of Routing)', IntegerFieldType, length=8),
        'batch_number': FieldDefinition('Batch Number', IntegerFieldType, length=7),
    }
