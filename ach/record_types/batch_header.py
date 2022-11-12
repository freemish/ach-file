"""Defines batch header fields and record type."""

from typing import Dict

from ..constants import (
    AutoDateInput,
    BATCH_HEADER_DEFAULT_ORIGINATOR_STATUS_CODE,
    BATCH_DEFAULT_SERVICE_CLASS_CODE,
    BATCH_HEADER_DEFAULT_STANDARD_ENTRY_CLASS_CODE,
    BATCH_HEADER_RECORD_TYPE_CODE
)
from .record_fields import (
    AlphaNumFieldType,
    DateFieldType,
    FieldDefinition,
    IntegerFieldType
)
from .record_type_base import RecordType


# pylint: disable=line-too-long
class BatchHeaderRecordType(RecordType):
    """Define all fields in a batch header record line of an ACH file."""
    field_definition_dict: Dict[str, FieldDefinition] = {
        'record_type_code': FieldDefinition('Record Type Code', IntegerFieldType, length=1, default=BATCH_HEADER_RECORD_TYPE_CODE),
        'service_class_code': FieldDefinition('Service Class Code', IntegerFieldType, length=3, default=BATCH_DEFAULT_SERVICE_CLASS_CODE),
        'company_name': FieldDefinition('Company Name', AlphaNumFieldType, length=16),
        'company_discretionary_data': FieldDefinition('Company Discretionary Data', AlphaNumFieldType, length=20, required=False),
        'company_identification': FieldDefinition('Company Identification Number', IntegerFieldType, length=10),
        'standard_entry_class_code': FieldDefinition('Standard Entry Class Code', AlphaNumFieldType, length=3, default=BATCH_HEADER_DEFAULT_STANDARD_ENTRY_CLASS_CODE),
        'company_entry_description': FieldDefinition('Company Entry Description', AlphaNumFieldType, length=10),
        'company_descriptive_date': FieldDefinition('Company Descriptive Date', DateFieldType, length=6, required=False),
        'effective_entry_date': FieldDefinition('Effective Entry Date', DateFieldType, length=6, default=AutoDateInput.TOMORROW, auto_correct_input=True),
        'settlement_date': FieldDefinition('Settlement Date', AlphaNumFieldType, length=3, required=False),
        'originator_status_code': FieldDefinition('Originator Status Code', IntegerFieldType, length=1, default=BATCH_HEADER_DEFAULT_ORIGINATOR_STATUS_CODE),
        'odfi_identification': FieldDefinition('ODFI Identification (Routing Without Final Digit)', IntegerFieldType, length=8),
        'batch_number': FieldDefinition('Batch Number', IntegerFieldType, length=7),
    }

    # pylint: disable=too-many-arguments
    def __init__(self, company_name: str, company_identification: str, company_entry_description: str, odfi_identification: str, batch_number: int, **kwargs):
        kwargs['company_name'] = company_name
        kwargs['company_identification'] = company_identification
        kwargs['company_entry_description'] = company_entry_description
        kwargs['odfi_identification'] = odfi_identification
        kwargs['batch_number'] = batch_number
        super().__init__(**kwargs)
