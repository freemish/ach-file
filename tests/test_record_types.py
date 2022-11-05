"""Tests record_types.py and other subclasses of RecordType."""

from unittest import TestCase

from record_types.record_fields import FieldDefinition, IntegerFieldType, AlphaNumFieldType
from record_types.record_type_base import RecordType, InvalidRecordSizeError


class TestRecordType(TestCase):
    def test_record_type_field_definitions_empty_length(self):
        RecordType({}, desired_record_size=0)

    def test_record_type_not_desired_size_empty(self):
        self.assertRaises(InvalidRecordSizeError, RecordType, {}, 1)
    
    def test_record_type_field_definitions_not_empty(self):
        RecordType(
            {
                'record_code': FieldDefinition('record_code', IntegerFieldType, length=1, required=False),
                'additional_field': FieldDefinition('additional_field', AlphaNumFieldType, length=2, required=False),
            },
            desired_record_size=3,
        )
    
    def test_record_type_field_definitions_not_desired_size_empty(self):
        with self.assertRaises(InvalidRecordSizeError):
            RecordType(
                {
                    'record_code': FieldDefinition('record_code', IntegerFieldType, length=1, required=False),
                    'additional_field': FieldDefinition('additional_field', AlphaNumFieldType, length=2, required=False),
                },
                desired_record_size=1,
            )
    
    def test_record_type_render_line_empty(self):
        record_type = RecordType({}, desired_record_size=0)
        self.assertEqual(record_type.render_record_line(), '')
    
    def test_record_type_render_line_not_empty(self):
        record_type = RecordType(
            {
                'record_code': FieldDefinition('record_code', IntegerFieldType, length=1, required=False),
                'additional_field': FieldDefinition('additional_field', AlphaNumFieldType, length=2, required=False),
            },
            desired_record_size=3,
        )
        self.assertEqual(record_type.render_record_line(), '0  ')
    
    def test_record_type_render_line_not_empty_with_kwargs(self):
        record_type = RecordType(
            {
                'record_code': FieldDefinition('record_code', IntegerFieldType, length=1, required=False),
                'additional_field': FieldDefinition('additional_field', AlphaNumFieldType, length=2, required=False),
            },
            desired_record_size=3,
            record_code=1,
            additional_field='hello',
        )
        self.assertEqual(record_type.render_record_line(), '1he')
