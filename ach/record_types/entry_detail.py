"""Defines entry detail fields and record type."""

from typing import Dict

from ..constants import (
    ENTRY_DETAIL_DEFAULT_ADDENDA_RECORD_INDICATOR,
    ENTRY_DETAIL_RECORD_TYPE_CODE
)
from .record_fields import (
    AlphaNumFieldType, FieldDefinition, IntegerFieldType
)
from .record_type_base import RecordType


# pylint: disable=line-too-long
class EntryDetailRecordType(RecordType):
    """Define all fields in an entry detail record line of an ACH file."""
    field_definition_dict: Dict[str, FieldDefinition] = {
        'record_type_code': FieldDefinition('Record Type Code', IntegerFieldType, length=1, default=ENTRY_DETAIL_RECORD_TYPE_CODE),
        'transaction_code': FieldDefinition('Transaction Code', IntegerFieldType, length=2),
        'rdfi_routing': FieldDefinition('RDFI Routing Number', IntegerFieldType, length=9),
        'rdfi_account_number': FieldDefinition('RDFI Account Number', AlphaNumFieldType, length=17),
        'amount': FieldDefinition('Transaction Amount Expressed As Cents', IntegerFieldType, length=10),
        'individual_identification_number': FieldDefinition('Individual Identification Number (Alphanumeric)', AlphaNumFieldType, length=15, required=False),
        'individual_name': FieldDefinition('Individual Name', AlphaNumFieldType, length=22),
        'discretionary_data': FieldDefinition('Discretionary Data', AlphaNumFieldType, length=2, required=False),
        'addenda_record_indicator': FieldDefinition('Addenda Record Indicator', IntegerFieldType, length=1, default=ENTRY_DETAIL_DEFAULT_ADDENDA_RECORD_INDICATOR),
        'trace_odfi_identifier': FieldDefinition('Trace Number: ODFI Identifier', IntegerFieldType, length=8),
        'trace_sequence_number': FieldDefinition('Trace Number: Sequence Number', IntegerFieldType, length=7)
    }

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            transaction_code: int,
            rdfi_routing: str,
            rdfi_account_number: str,
            amount: int,
            individual_name: str,
            trace_number: str = None,
            **kwargs
        ):
        kwargs['transaction_code'] = transaction_code
        kwargs['rdfi_routing'] = rdfi_routing
        kwargs['rdfi_account_number'] = rdfi_account_number
        kwargs['amount'] = amount
        kwargs['individual_name'] = individual_name
        if trace_number is not None:
            kwargs['trace_odfi_identifier'] = str(trace_number)[:8]
            kwargs['trace_sequence_number'] = str(trace_number)[8:15]
        super().__init__(**kwargs)
