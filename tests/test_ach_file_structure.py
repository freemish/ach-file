"""Tests ACH file structure representation."""

from unittest import TestCase

from record_types.constants import RECORD_SIZE
from files.file_structure import (
    ACHBatch, ACHFileContents, ACHTransactionEntry,
    AddendaRecordType, BatchHeaderRecordType, EntryDetailRecordType,
    FileHeaderRecordType
)

test_file = """101 123456780 1234567801409020123A094101YOUR BANK              YOUR COMPANY                   
5200YOUR COMPANY                        1234567890PPDPAYROLL         140903   1123456780000001
62212345678011232132         0000001000               ALICE WANDERDUST        1123456780000001
705HERE IS SOME ADDITIONAL INFORMATION                                             00010000001
627123456780234234234        0000015000               BILLY HOLIDAY           0123456780000002
622123232318123123123        0000001213               RACHEL WELCH            0123456780000003
820000000400370145870000000150000000000022131234567890                         123456780000001
9000001000001000000040037014587000000015000000000002213                                       
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999"""


class TestACHFileContents(TestCase):
    def test_ach_file_contents(self):
        billy = EntryDetailRecordType(
            transaction_code=27,
            rdfi_routing=123456780,
            rdfi_account_number=234234234,
            amount=15000,
            individual_name='BILLY HOLIDAY',
            addenda_record_indicator=0,
            trace_number=123456780000002,
        )
        file_contents = ACHFileContents(
            FileHeaderRecordType(
                destination_routing=123456780,
                origin_routing=123456780,
                destination_name='YOUR BANK',
                origin_name='YOUR COMPANY',
                file_creation_date='140902',
                file_creation_time='0123',
            ),
            batches=[
                ACHBatch(
                    BatchHeaderRecordType(
                        company_name='YOUR COMPANY',
                        company_identification=1234567890,
                        company_entry_description='PAYROLL',
                        odfi_identification=112345678,
                        batch_number=1,
                        effective_entry_date='140903',
                    ),
                    transactions=[
                        ACHTransactionEntry(
                            EntryDetailRecordType(
                                transaction_code=22,
                                rdfi_routing=123456780,
                                rdfi_account_number=11232132,
                                amount=1000,
                                individual_name='ALICE WANDERDUST',
                                trace_number='123456780000001',
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
                                individual_name='RACHEL WELCH',
                                trace_odfi_identifier=12345678,
                                trace_sequence_number=3,
                                addenda_record_indicator=0,
                            )
                        )
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
