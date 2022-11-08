"""Defines an ACH file parser."""

from typing import Dict, List, Optional, Union

from record_types import (
    AddendaRecordType, BatchControlRecordType,
    BatchHeaderRecordType, EntryDetailRecordType,
    FileControlRecordType, FileHeaderRecordType
)
from record_types.record_type_base import RecordType
from record_types.constants import (
    ADDENDA_RECORD_TYPE_CODE,
    BATCH_CONTROL_RECORD_TYPE_CODE,
    BATCH_HEADER_RECORD_TYPE_CODE,
    ENTRY_DETAIL_RECORD_TYPE_CODE,
    FILE_CONTROL_RECORD_TYPE_CODE,
    FILE_HEADER_RECORD_TYPE_CODE,
    RECORD_SIZE
)

from files.file_structure import ACHBatch, ACHFileContents, ACHTransactionEntry


class ACHFileContentsParser:
    def __init__(self, ach_file_str: str):
        self._raw_str = ach_file_str
        self.ach_file_contents: Optional[ACHFileContents] = None
        self.records_list: List[RecordType] = []

    def process_records_list(self) -> None:
        self.records_list = self.convert_file_string_to_records_list(self._raw_str)

    def process_ach_file_contents(self) -> None:
        self.ach_file_contents = self.convert_records_list_to_ach_file_contents(self.records_list)

    @staticmethod
    def convert_records_list_to_ach_file_contents(records_list: List[RecordType]) -> ACHFileContents:
        return ACHFileContents(records_list[0], ACHFileContentsParser.convert_sub_records_list_to_ach_batch_list(records_list[1:-1]))

    @staticmethod
    def convert_sub_records_list_to_ach_batch_list(records_list: List[RecordType]) -> List[ACHBatch]:
        ach_batch_list: List[ACHBatch] = []
        batch_to_records: Dict[BatchControlRecordType, List[Union[EntryDetailRecordType, AddendaRecordType]]] = {}
        curr_batch_header: Optional[BatchHeaderRecordType] = None
        for record in records_list:
            if record.get_field_value('record_type_code') == str(BATCH_HEADER_RECORD_TYPE_CODE):
                curr_batch_header = record
                batch_to_records[curr_batch_header] = []
                continue
            if record.get_field_value('record_type_code') == str(BATCH_CONTROL_RECORD_TYPE_CODE):
                tx_entries = ACHFileContentsParser.convert_batch_transaction_record_types_to_ach_transaction_entry_list(batch_to_records[curr_batch_header])
                ach_batch_list.append(ACHBatch(curr_batch_header, tx_entries))
                continue
            batch_to_records[curr_batch_header].append(record)
        return ach_batch_list

    @staticmethod
    def convert_batch_transaction_record_types_to_ach_transaction_entry_list(
        records_list: List[Union[EntryDetailRecordType, AddendaRecordType]],
    ) -> List[ACHTransactionEntry]:
        entries: List[ACHTransactionEntry] = []
        curr_entry: Optional[EntryDetailRecordType] = None
        curr_entry_addendas: List[AddendaRecordType] = []
        for record in records_list:
            if record.get_field_value('record_type_code') == str(ADDENDA_RECORD_TYPE_CODE):
                curr_entry_addendas.append(record)
                continue
            if curr_entry:
                entries.append(ACHTransactionEntry(curr_entry, curr_entry_addendas))
            curr_entry = record
            curr_entry_addendas = []

        entries.append(ACHTransactionEntry(curr_entry, curr_entry_addendas))
        return entries


    def get_record_fields_dict_list(self) -> List[Dict[str, str]]:
        dict_list = []
        for record in self.records_list:
            dict_list.append({x: y.value for x, y in record.fields.items()})
        return dict_list
    
    @staticmethod
    def get_record_type_from_record_type_code(record_type_code: Union[str, int]) -> Optional[RecordType]:
        record_type_map = {
            ADDENDA_RECORD_TYPE_CODE: AddendaRecordType,
            BATCH_CONTROL_RECORD_TYPE_CODE: BatchControlRecordType,
            BATCH_HEADER_RECORD_TYPE_CODE: BatchHeaderRecordType,
            ENTRY_DETAIL_RECORD_TYPE_CODE: EntryDetailRecordType,
            FILE_CONTROL_RECORD_TYPE_CODE: FileControlRecordType,
            FILE_HEADER_RECORD_TYPE_CODE: FileHeaderRecordType,
        }
        return record_type_map.get(int(record_type_code))

    @staticmethod
    def convert_line_to_record_type(line_str: str, record_type_class: RecordType) -> RecordType:
        str_index = 0
        kwargs = {}
        for key, field_def in record_type_class.field_definition_dict.items():
            kwargs[key] = line_str[str_index: str_index + field_def.length]
            str_index += field_def.length
        return record_type_class(**kwargs)

    @staticmethod
    def convert_file_string_to_records_list(file_str: str, line_break: str = '\n') -> List[RecordType]:
        lines = file_str.split(line_break)
        records = []
        for line in lines:
            if not line or line == '9' * RECORD_SIZE:
                continue
            record_type_class = ACHFileContentsParser.get_record_type_from_record_type_code(line[0])
            record_type = ACHFileContentsParser.convert_line_to_record_type(line, record_type_class)
            records.append(record_type)
        return records
