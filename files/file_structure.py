"""Defines ACH file structure and how record types relate."""

from math import ceil
from typing import Any, Dict, List, Optional, Tuple

from record_types.addenda import AddendaRecordType
from record_types.batch_control import BatchControlRecordType
from record_types.batch_header import BatchHeaderRecordType
from record_types.constants import TransactionCode, FILE_HEADER_BLOCKING_FACTOR, RECORD_SIZE
from record_types.entry_detail import EntryDetailRecordType
from record_types.file_control import FileControlRecordType
from record_types.file_header import FileHeaderRecordType


class ACHFileContents:
    """
    Contains 1 FileHeaderRecordType, 1 FileControlRecord, and n ACHBatch.

    Attributes:
        file_header_record: FileHeaderRecordType
        batches: List[ACHBatch]
        [computed property] file_control_record: FileControlRecordType
    """
    def __init__(self, file_header_record: FileHeaderRecordType, batches: Optional[List['ACHBatch']] = None):
        self._file_header_record = file_header_record
        self.batches = batches or []
        self._file_control_record = None
        self._recalc_file_control = False

    def get_rendered_line_list(self) -> List[str]:
        record_types_list = [self.file_header_record.render_record_line()]
        for batch in self.batches:
            record_types_list.extend(batch.get_rendered_line_list())
        record_types_list.append(self.file_control_record.render_record_line())
        return record_types_list

    def render_file_contents(self, line_break: str = '\n', end: str = '\n') -> str:
        rendered_line_list = self.get_rendered_line_list()
        file_contents = line_break.join(rendered_line_list)

        block_orphan_count = len(rendered_line_list) % FILE_HEADER_BLOCKING_FACTOR
        if block_orphan_count:
            for _ in range(FILE_HEADER_BLOCKING_FACTOR - block_orphan_count):
                file_contents += line_break + ('9' * RECORD_SIZE)

        return file_contents + end

    def render_json_dict(self) -> Dict[str, Any]:
        file_as_json_dict = {
            'file_header': self.file_header_record.get_field_values(),
            'batches': [
                b.get_json_dict() for b in self.batches
            ],
            'file_control': self.file_control_record.get_field_values(),
        }
        return file_as_json_dict

    @property
    def file_header_record(self) -> FileHeaderRecordType:
        return self._file_header_record

    @file_header_record.setter
    def file_header_record(self, file_header_record: FileHeaderRecordType) -> None:
        self.file_header_record = file_header_record
        if self._file_control_record:
            self._recalc_file_control = True

    def add_batch(self, batch: 'ACHBatch') -> None:
        self.batches.append(batch)
        if self._file_control_record:
            self._recalc_file_control = True

    def remove_batch_by_index(self, index: int) -> 'ACHBatch':
        batch = self.batches.pop(index)
        if self._file_control_record:
            self._recalc_file_control = True
        return batch

    def get_all_transactions(self) -> List['ACHTransactionEntry']:
        txs = []
        for batch in self.batches:
            txs.extend(batch.transactions)
        return txs

    @property
    def file_control_record(self) -> FileControlRecordType:
        if self._file_control_record and not self._recalc_file_control:
            return self._file_control_record
        self._file_control_record = self._compute_file_control_record()
        return self._file_control_record

    @file_control_record.setter
    def file_control_record(self, file_control_record: FileControlRecordType) -> FileControlRecordType:
        """For use by file parser."""
        self._file_control_record = file_control_record

    def _compute_file_control_record(self) -> FileControlRecordType:
        debit_total, credit_total = self._compute_debit_and_credit_totals()
        ent_add_count = self._compute_entry_and_addenda_count()
        return FileControlRecordType(
            batch_count=len(self.batches),
            block_count=self._compute_block_count(entry_addenda_count=ent_add_count),
            entry_and_addenda_count=ent_add_count,
            entry_hash=self._compute_entry_hash(),
            total_credit_amount=credit_total,
            total_debit_amount=debit_total,
        )

    def _compute_entry_and_addenda_count(self) -> int:
        return sum([int(x.batch_control_record.get_field_value('entry_and_addenda_count')) for x in self.batches])

    def _compute_entry_hash(self) -> int:
        return sum([int(x.batch_control_record.get_field_value('entry_hash')) for x in self.batches])

    def _compute_line_count(self, entry_addenda_count: Optional[int] = None) -> int:
        if entry_addenda_count is None:
            entry_addenda_count = self._compute_entry_and_addenda_count()
        return entry_addenda_count + (len(self.batches) * 2) + 2

    def _compute_block_count(self, line_count: Optional[int] = None, entry_addenda_count: Optional[int] = None) -> int:
        if line_count is None:
            line_count = self._compute_line_count(entry_addenda_count)
        return ceil(line_count / float(FILE_HEADER_BLOCKING_FACTOR))

    def _compute_debit_and_credit_totals(self) -> Tuple[int, int]:
        debit_sum, credit_sum = 0, 0
        debit_sum = sum([int(x.batch_control_record.get_field_value('total_debit_amount')) for x in self.batches])
        credit_sum = sum([int(x.batch_control_record.get_field_value('total_credit_amount')) for x in self.batches])
        return debit_sum, credit_sum


class ACHBatch:
    """
    Contains 1 BatchHeaderRecordType, 1 BatchControlRecordType, and n ACHTransactionEntry.

    Attributes:
        batch_header_record: BatchHeaderRecordType
        transactions: List[ACHTransactionEntry]
        [computed + cached property] batch_control_record: BatchControlRecordType
    """
    def __init__(self, batch_header_record: BatchHeaderRecordType, transactions: Optional[List['ACHTransactionEntry']] = None):
        self.batch_header_record = batch_header_record
        self.transactions = transactions or []
        self._batch_control_record: BatchControlRecordType = None
        self._recalc_batch_control = False
    
    def set_batch_header_record(self, batch_header_record: BatchHeaderRecordType) -> None:
        self.batch_header_record = batch_header_record
        if self._batch_control_record:
            self._recalc_batch_control = True

    def add_transaction(self, transaction: 'ACHTransactionEntry') -> None:
        self.transactions.append(transaction)
        if self._batch_control_record:
            self._recalc_batch_control = True
    
    def remove_transaction_by_index(self, index: int) -> 'ACHTransactionEntry':
        transaction = self.transactions.pop(index)
        if self._batch_control_record:
            self._recalc_batch_control = True
        return transaction

    @property
    def batch_control_record(self) -> BatchControlRecordType:
        if self._batch_control_record and not self._recalc_batch_control:
            return self._batch_control_record
        self._batch_control_record = self._compute_batch_control_record()
        return self._batch_control_record

    @batch_control_record.setter
    def batch_control_record(self, batch_control_record: BatchControlRecordType) -> None:
        """For use by file parser."""
        self._batch_control_record = batch_control_record

    def get_rendered_line_list(self) -> List[str]:
        record_types_list = [self.batch_header_record.render_record_line()]
        for tx in self.transactions:
            record_types_list.extend(tx.get_rendered_line_list())
        record_types_list.append(self.batch_control_record.render_record_line())
        return record_types_list

    def get_json_dict(self) -> Dict[str, Any]:
        batch_dict = {
            'batch_header': self.batch_header_record.get_field_values(),
            'transactions': [
                t.get_json_dict() for t in self.transactions
            ],
            'batch_control': self.batch_control_record.get_field_values(),
        }
        return batch_dict

    def _compute_batch_control_record(self) -> BatchControlRecordType:
        debit_total, credit_total = self._compute_debit_and_credit_totals()
        return BatchControlRecordType(
            entry_and_addenda_count=self._compute_entry_and_addenda_count(),
            entry_hash=self._compute_entry_hash(),
            total_debit_amount=debit_total,
            total_credit_amount=credit_total,
            service_class_code=self.batch_header_record.get_field_value('service_class_code'),
            company_identification=self.batch_header_record.get_field_value('company_identification'),
            odfi_identification=self.batch_header_record.get_field_value('odfi_identification'),
            batch_number=self.batch_header_record.get_field_value('batch_number'),
        )

    def _compute_entry_hash(self) -> int:
        return sum([x.get_entry_hash_int() for x in self.transactions])

    def _compute_entry_and_addenda_count(self) -> int:
        return sum([x.get_entry_and_addenda_count() for x in self.transactions])

    def _compute_debit_and_credit_totals(self) -> Tuple[int, int]:
        debit_total = sum([x.get_debit_amount() for x in self.transactions])
        credit_total = sum([x.get_credit_amount() for x in self.transactions])
        return debit_total, credit_total


class ACHTransactionEntry:
    """
    Contains 1 entry detail record and 0-n addendas associated with that record.

    Attributes:
        entry: EntryDetailRecordType
        addendas: List[AddendaRecordType]
    """
    def __init__(
        self,
        entry: EntryDetailRecordType,
        addendas: Optional[List[AddendaRecordType]] = None,
    ):
        self.entry = entry
        self.addendas = addendas or []

    def set_entry(self, entry: EntryDetailRecordType) -> None:
        self.entry = entry

    def add_addenda(self, addenda: AddendaRecordType) -> None:
        self.addendas.append(addenda)

    def remove_addenda_by_index(self, index: int) -> AddendaRecordType:
        return self.addendas.pop(index)
    
    def get_entry_and_addenda_count(self) -> int:
        return len(self.addendas) + 1
    
    def get_entry_hash_int(self) -> int:
        return int(self.entry.get_field_value('rdfi_routing')[:8])

    def get_transaction_code_enum(self) -> TransactionCode:
        return TransactionCode(int(self.entry.get_field_value("transaction_code")))

    def get_amount(self) -> int:
        return int(self.entry.get_field_value("amount"))

    def get_debit_amount(self) -> int:
        return self.get_amount() if self.get_transaction_code_enum().is_debit() else 0

    def get_credit_amount(self) -> int:
        return self.get_amount() if self.get_transaction_code_enum().is_credit() else 0

    def get_rendered_line_list(self) -> List[str]:
        return [self.entry.render_record_line()] + [x.render_record_line() for x in self.addendas]

    def get_json_dict(self) -> Dict[str, Any]:
        tx_dict = {
            'entry_detail': self.entry.get_field_values(),
            'addendas': [
                a.get_field_values() for a in self.addendas
            ],
        }
        return tx_dict
