"""Tests record_types.py and other subclasses of RecordType."""

import datetime
from unittest import TestCase

from ach.record_types import (
    AddendaRecordType,
    AlphaNumFieldType,
    BatchControlRecordType,
    BatchHeaderRecordType,
    EntryDetailRecordType,
    FieldDefinition,
    FileControlRecordType,
    FileHeaderRecordType,
    IntegerFieldType,
    InvalidRecordSizeError,
    RecordType,
)


class TestRecordType(TestCase):
    def test_record_type_field_definitions_empty_length(self):
        RecordType({}, desired_record_size=0)

    def test_record_type_not_desired_size_empty(self):
        self.assertRaises(InvalidRecordSizeError, RecordType, {}, 1)

    def test_record_type_field_definitions_not_empty(self):
        RecordType(
            {
                "record_code": FieldDefinition(
                    "record_code", IntegerFieldType, length=1, required=False
                ),
                "additional_field": FieldDefinition(
                    "additional_field", AlphaNumFieldType, length=2, required=False
                ),
            },
            desired_record_size=3,
        )

    def test_record_type_field_definitions_not_desired_size_empty(self):
        with self.assertRaises(InvalidRecordSizeError):
            RecordType(
                {
                    "record_code": FieldDefinition(
                        "record_code", IntegerFieldType, length=1, required=False
                    ),
                    "additional_field": FieldDefinition(
                        "additional_field", AlphaNumFieldType, length=2, required=False
                    ),
                },
                desired_record_size=1,
            )

    def test_record_type_render_line_empty(self):
        record_type = RecordType({}, desired_record_size=0)
        self.assertEqual(record_type.render_record_line(), "")

    def test_record_type_render_line_not_empty(self):
        record_type = RecordType(
            {
                "record_code": FieldDefinition(
                    "record_code", IntegerFieldType, length=1, required=False
                ),
                "additional_field": FieldDefinition(
                    "additional_field", AlphaNumFieldType, length=2, required=False
                ),
            },
            desired_record_size=3,
        )
        self.assertEqual(record_type.render_record_line(), "0  ")

    def test_record_type_render_line_not_empty_with_kwargs(self):
        record_type = RecordType(
            {
                "record_code": FieldDefinition(
                    "record_code", IntegerFieldType, length=1, required=False
                ),
                "additional_field": FieldDefinition(
                    "additional_field", AlphaNumFieldType, length=2, required=False
                ),
            },
            desired_record_size=3,
            record_code=1,
            additional_field="hello",
        )
        self.assertEqual(record_type.render_record_line(), "1he")


class TestFileHeaderRecordType(TestCase):
    def test_file_header(self):
        file_header = FileHeaderRecordType(
            "012345678",
            123456789,
            "The Big Fed",
            "The Little Fintech",
            file_creation_date="221104",
        )
        record_line = file_header.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "101 012345678 123456789221104    A094101The Big Fed            The Little Fintech             ",
        )

    def test_file_header_default_now(self):
        today = datetime.date.today().strftime("%y%m%d")
        file_header = FileHeaderRecordType(
            "012345678", 123456789, "The Big Fed", "The Little Fintech"
        )
        record_line = file_header.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "101 012345678 123456789{}    A094101The Big Fed            The Little Fintech             ".format(
                today
            ),
        )

    def test_file_header_tweak_field_definitions(self):
        FileHeaderRecordType.field_definition_dict[
            "file_creation_date"
        ].default = "221105"
        file_header = FileHeaderRecordType(
            "012345678", 123456789, "The Big Fed", "The Little Fintech"
        )
        record_line = file_header.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "101 012345678 123456789221105    A094101The Big Fed            The Little Fintech             ",
        )
        self.assertEqual(
            file_header.fields["file_creation_date"].cleaned_value, "221105"
        )
        file_header.fields["file_creation_date"].cleaned_value = "221106"
        self.assertEqual(
            file_header.render_record_line(),
            "101 012345678 123456789221106    A094101The Big Fed            The Little Fintech             ",
        )


class TestBatchHeaderRecordType(TestCase):
    def test_batch_header(self):
        batch_header = BatchHeaderRecordType(
            "Teeniest Fintech",
            123,
            "Payday",
            "01234567",
            2,
            effective_entry_date="221023",
        )
        record_line = batch_header.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "5200Teeniest Fintech                    123       PPDPayday          221023   1012345670000002",
        )


class TestEntryDetailRecordType(TestCase):
    def test_entry_detail_full_trace_number(self):
        entry_detail = EntryDetailRecordType(
            22, "123456789", "123456", "100", "Testy Testface", "012345670000001"
        )
        record_line = entry_detail.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "622123456789123456           0000000100               Testy Testface          1012345670000001",
        )

    def test_entry_detail_two_part_trace_number(self):
        entry_detail = EntryDetailRecordType(
            22,
            "123456789",
            "123456",
            "100",
            "Testy Testface",
            trace_odfi_identifier="01234567",
            trace_sequence_number=1,
        )
        record_line = entry_detail.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "622123456789123456           0000000100               Testy Testface          1012345670000001",
        )


class TestAddendaRecordType(TestCase):
    def test_addenda(self):
        addenda = AddendaRecordType("Hee hee have my money", 1)
        record_line = addenda.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "705Hee hee have my money                                                           00010000001",
        )


class TestBatchControlRecordType(TestCase):
    def test_batch_control(self):
        batch_control = BatchControlRecordType(
            entry_and_addenda_count=2,
            entry_hash=543,
            total_debit_amount=100,
            total_credit_amount=0,
            company_identification=123,
            odfi_identification=12345678,
            batch_number=1,
        )
        record_line = batch_control.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "82000000020000000543000000000100000000000000123                                123456780000001",
        )


class TestFileControlRecordType(TestCase):
    def test_file_control(self):
        """
        batch_count: int,
        block_count: int,
        entry_and_addenda_count: int,
        entry_hash: int,
        total_debit_amount: int,
        total_credit_amount: int,
        """
        file_control = FileControlRecordType(
            batch_count=1,
            block_count=1,
            entry_and_addenda_count=2,
            entry_hash=543,
            total_debit_amount=100,
            total_credit_amount=0,
        )
        record_line = file_control.render_record_line()
        self.assertEqual(len(record_line), 94)
        self.assertEqual(
            record_line,
            "9000001000001000000020000000543000000000100000000000000                                       ",
        )
