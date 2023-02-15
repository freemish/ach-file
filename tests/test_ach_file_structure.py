"""Tests ACH file structure representation."""

from unittest import TestCase

from ach.constants import RECORD_SIZE
from ach.files import (
    ACHBatch,
    ACHFileContents,
    ACHTransactionEntry,
    ACHFileContentsParser,
)
from ach.record_types import (
    AddendaRecordType,
    BatchHeaderRecordType,
    EntryDetailRecordType,
    FileHeaderRecordType,
)
from tests import test_file


class TestACHFileContents(TestCase):
    def test_ach_file_contents(self):
        billy = EntryDetailRecordType(
            transaction_code=27,
            rdfi_routing=123456780,
            rdfi_account_number=234234234,
            amount=15000,
            individual_name="BILLY HOLIDAY",
            addenda_record_indicator=0,
            trace_number=123456780000002,
        )
        file_contents = ACHFileContents(
            FileHeaderRecordType(
                destination_routing=123456780,
                origin_routing=123456780,
                destination_name="YOUR BANK",
                origin_name="YOUR COMPANY",
                file_creation_date="140902",
                file_creation_time="0123",
            ),
            batches=[
                ACHBatch(
                    BatchHeaderRecordType(
                        company_name="YOUR COMPANY",
                        company_identification=1234567890,
                        company_entry_description="PAYROLL",
                        odfi_identification=112345678,
                        batch_number=1,
                        effective_entry_date="140903",
                    ),
                    transactions=[
                        ACHTransactionEntry(
                            EntryDetailRecordType(
                                transaction_code=22,
                                rdfi_routing=123456780,
                                rdfi_account_number=11232132,
                                amount=1000,
                                individual_name="ALICE WANDERDUST",
                                trace_number="123456780000001",
                            ),
                            addendas=[
                                AddendaRecordType(
                                    payment_related_information="HERE IS SOME ADDITIONAL INFORMATION",
                                    entry_detail_sequence_number=1,
                                    addenda_sequence_number=1,
                                ),
                            ],
                        ),
                        ACHTransactionEntry(
                            billy,
                        ),
                        ACHTransactionEntry(
                            EntryDetailRecordType(
                                transaction_code=22,
                                rdfi_routing=123232318,
                                rdfi_account_number=123123123,
                                amount=1213,
                                individual_name="RACHEL WELCH",
                                trace_odfi_identifier=12345678,
                                trace_sequence_number=3,
                                addenda_record_indicator=0,
                            )
                        ),
                    ],
                ),
            ],
        )
        file_contents_str = file_contents.render_file_contents()
        file_lines = file_contents_str.splitlines()
        test_file_lines = test_file.splitlines()
        for i, line in enumerate(file_lines):
            self.assertEqual(len(line), RECORD_SIZE)
            self.assertEqual(line, test_file_lines[i])

    def test_set_file_header_recalculates_file_control(self):
        ach_file_contents = ACHFileContentsParser(test_file).process_ach_file_contents()
        new_file_header = FileHeaderRecordType(
            destination_routing=123456780,
            origin_routing=123456780,
            destination_name="YOUR BANK",
            origin_name="YOUR COMPANY",
            file_creation_date="140902",
            file_creation_time="0123",
            blocking_factor=2,
        )
        ach_file_contents.file_header_record = new_file_header
        self.assertEqual(
            int(ach_file_contents.file_control_record.get_field_value("block_count")), 4
        )

    def test_compute_line_count(self):
        ach_file_contents = ACHFileContentsParser(test_file).process_ach_file_contents()
        self.assertEqual(ach_file_contents._compute_line_count(), 8)

    def test_add_batch_recalculates_control_records(self):
        ach_file_contents = ACHFileContentsParser(test_file).process_ach_file_contents()
        ach_file_contents.add_batch(
            ACHBatch(
                BatchHeaderRecordType(
                    company_name="Test Company",
                    company_identification="0912",
                    company_entry_description="Various",
                    odfi_identification="12345678",
                    batch_number=2,
                ),
                transactions=[
                    ACHTransactionEntry(
                        EntryDetailRecordType(
                            transaction_code=27,
                            rdfi_routing="012345678",
                            rdfi_account_number="0123456",
                            amount=100,
                            individual_name="Hello Darling",
                            trace_odfi_identifier=12345678,
                            trace_sequence_number=4,
                            addenda_record_indicator=1,
                        ),
                        addendas=[
                            AddendaRecordType(
                                "Payment-related information",
                                entry_detail_sequence_number=4,
                                addenda_sequence_number=1,
                            )
                        ],
                    )
                ],
            )
        )
        self.assertEqual(
            int(ach_file_contents.file_control_record.get_field_value("batch_count")), 2
        )
