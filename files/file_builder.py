"""Defines an ACH file builder."""

from typing import Any, Dict, List

from record_types import (
    AddendaRecordType, BatchHeaderRecordType,
    EntryDetailRecordType, FileHeaderRecordType
)
from record_types.record_fields import FieldDefinition

from files.file_structure import ACHBatch, ACHFileContents, ACHTransactionEntry


class NoBatchForTransactionError(Exception):
    """Raise when no batches have been added before adding a transaction entry to the ACHFileBuilder."""


class ACHFileBuilder:
    """Builds an ACHFileContents object."""

    def __init__(self, auto_correct_strings: bool = False, **file_settings):
        """
        Accepts a dict of file settings; run cls.get_file_setting_fields to see all key options.

        Examples:

            settings_dict = {
                'destination_routing': '012345678',
                'origin_routing': '102345678',
                'destination_name': 'YOUR BANK',
                'origin_name': 'YOUR FINANCIAL INSTITUTION',
                'file_id_modifier': 'B',
            }
            ACHFileBuilder(**settings_dict)

            ACHFileBuilder(destination_routing='012345678', origin_routing='102345678', destination_name='YOUR BANK', origin_name='YOUR FINANCIAL INSTITUTION')
        """
        self.ach_file_contents: ACHFileContents = ACHFileContents(FileHeaderRecordType(**file_settings))
        self.auto_correct_strings = auto_correct_strings
        self.default_odfi_identification: str = file_settings.get('origin_routing', '').lstrip()[:8]

    def render(self, line_break: str = '\n', end: str = '\n') -> str:
        """Renders ACH flat file contents as a string."""
        return self.ach_file_contents.render_file_contents(line_break=line_break, end=end)

    def add_batch(self, **batch_settings: Dict[str, Any]) -> 'ACHFileBuilder':
        """
        Accepts a dict of batch settings: see cls.get_batch_fields to see all options.

        Example:
            b.add_batch(
                company_name='YOUR COMPANY',
                company_identification='1234567890',
                standard_entry_class_code='CCD',
                company_entry_description='Bonus',
                effective_entry_date='NOW',
            )
        """
        self._update_batch_settings(batch_settings)
        self.ach_file_contents.add_batch(ACHBatch(BatchHeaderRecordType(**batch_settings)))
        return self

    def add_entries_and_addendas(self, entry_dict_list: List[Dict[str, Any]], batch_index: int = -1,) -> 'ACHFileBuilder':
        """
        Iterates over a list of entries and their addendas. Adds them to last added batch in file by default.

        Example:
            b.add_entries_and_addendas([
                {'transaction_code': 22, 'rdfi_routing': '123456789', 'rdfi_account_number': '65656565', 'amount': '300', 'individual_name': 'Janey Test',},
                {'transaction_code': 27, 'rdfi_routing': '123456789', 'rdfi_account_number': '65656565', 'amount': '300', 'individual_name': 'Janey Test', 'addendas': [
                    {'payment_related_information': 'Reversing the last transaction pls and thx'},
                ]},
                {'transaction_code': 22, 'rdfi_routing': '023456789', 'rdfi_account_number': '45656565', 'amount': '7000', 'individual_name': 'Mackey Shawnderson', 'addendas': [
                    {'payment_related_information': 'Where\'s my money'},
                ]},
            ])
        """
        for e in entry_dict_list:
            self.add_entry_and_addenda(batch_index=batch_index, **e)
        return self

    def add_entry_and_addenda(self, batch_index: int = -1, **entry_details) -> 'ACHFileBuilder':
        """
        Adds single entry and its addenda(s) to a batch.
        Raises NoBatchForTransactionError or IndexError if batch index specified does not exist.

        Example:
            b.add_entry_and_addenda(
                transaction_code=22,
                rdfi_routing='123456789',
                rdfi_account_number='45454545',
                amount=2000,
                individual_name='Tester Testerson',
                addendas=[{'payment_related_information': 'This is a memo'}],
            )
        """
        if not self.ach_file_contents.batches:
            raise NoBatchForTransactionError("Must add batch before adding transaction entries")

        ach_tx_entry = self._convert_entry_detail_kwargs_to_ach_transaction_entry(**entry_details)
        self.ach_file_contents.batches[batch_index].add_transaction(ach_tx_entry)
        return self

    def _update_batch_settings(self, batch_settings: Dict[str, Any]) -> None:
        update_batch_settings = {
            'odfi_identification': self.default_odfi_identification,
            'batch_number': len(self.ach_file_contents.batches) + 1,
        }
        for k in update_batch_settings:
            if k not in batch_settings:
                batch_settings[k] = update_batch_settings[k]

    def _convert_entry_detail_kwargs_to_ach_transaction_entry(self, **entry_details) -> ACHTransactionEntry:
        addenda_list_kwargs = self._update_entry_detail_kwargs(entry_details)

        entry_record = EntryDetailRecordType(**entry_details)
        addenda_records = []

        for i, addenda_kwargs in enumerate(addenda_list_kwargs):
            self._update_addenda_record_kwargs(addenda_kwargs, entry_details.get('trace_sequence_number'), i+1)
            addenda_records.append(AddendaRecordType(**addenda_kwargs))

        return ACHTransactionEntry(entry_record, addenda_records)

    def _update_entry_detail_kwargs(self, entry_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_addendas = []
        if 'addendas' in entry_details:
            raw_addendas = entry_details.pop('addendas')

        update_entry = {
            'addenda_record_indicator': len(raw_addendas),
            'trace_odfi_identifier': self.default_odfi_identification,
            'trace_sequence_number': len(self.ach_file_contents.get_all_transactions()) + 1,
        }
        for k in update_entry:
            if k not in entry_details:
                entry_details[k] = update_entry[k]
        return raw_addendas

    def _update_addenda_record_kwargs(self, addenda_kwargs: Dict[str, Any], entry_detail_sequence_num: int, addenda_sequence_num: int) -> None:
        update_entry = {
            'entry_detail_sequence_number': entry_detail_sequence_num,
            'addenda_sequence_number': addenda_sequence_num,
        }
        for k in update_entry:
            if k not in addenda_kwargs:
                addenda_kwargs[k] = update_entry[k]

    @staticmethod
    def get_file_setting_fields(only_required: bool = False) -> Dict[str, FieldDefinition]:
        """Returns kwargs to pass into init. If only_required, returns only keywords that need to be set."""
        if only_required:
            return FileHeaderRecordType.get_required_kwargs()
        return FileHeaderRecordType.field_definition_dict

    @staticmethod
    def get_batch_fields(only_required: bool = False) -> Dict[str, FieldDefinition]:
        """Returns kwargs to pass into init. If only_required, returns only keywords that need to be set."""
        if only_required:
            required_kwargs = dict(BatchHeaderRecordType.get_required_kwargs())
            required_kwargs.pop('odfi_identification')
            required_kwargs.pop('batch_number')
            return required_kwargs
        return BatchHeaderRecordType.field_definition_dict

    @staticmethod
    def get_entry_fields(only_required: bool = False) -> Dict[str, FieldDefinition]:
        """Returns kwargs to pass into init. If only_required, returns only keywords that need to be set."""
        if only_required:
            required_kwargs = dict(EntryDetailRecordType.get_required_kwargs())
            required_kwargs.pop('trace_odfi_identifier')
            required_kwargs.pop('trace_sequence_number')
            return required_kwargs
        return EntryDetailRecordType.field_definition_dict

    @staticmethod
    def get_addenda_fields(only_required: bool = False) -> Dict[str, FieldDefinition]:
        """Returns kwargs to pass into init. If only_required, returns only keywords that need to be set."""
        if only_required:
            required_kwargs = dict(AddendaRecordType.get_required_kwargs())
            required_kwargs.pop('entry_detail_sequence_number')
            return required_kwargs
        return AddendaRecordType.field_definition_dict
