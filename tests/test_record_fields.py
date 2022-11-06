"""Tests record_fields.py"""

import datetime
from unittest import TestCase

from record_types.record_fields import (
    Alignment, AlphaNumFieldType, BlankPaddedRoutingNumberFieldType,
    DateFieldType, EmptyRequiredFieldError, Field, FieldDefinition,
    IntegerFieldType, ValueMismatchesFieldTypeError
)


class TestErrorMessage(TestCase):
    def test_value_mismatches_field_type_error(self):
        exc = ValueMismatchesFieldTypeError("value", IntegerFieldType.regex.pattern)
        self.assertEqual(exc.message, "Passed-in value \"value\" mismatches ^\d+$")

    def test_empty_required_field_error(self):
        exc = EmptyRequiredFieldError("field_name")
        self.assertEqual(exc.message, "Field field_name requires a value and there is no default in its definition")


class TestAlignment(TestCase):
    def test_align_left(self):
        cases = [
            {'input': ['TEST', 3, ' '], 'output': 'TEST'},
            {'input': ['TEST', 4, ' '], 'output': 'TEST'},
            {'input': ['TEST', 5, ' '], 'output': 'TEST '},
            {'input': ['TEST', 5, '0'], 'output': 'TEST0'},
        ]

        for case in cases:
            output = Alignment.LEFT.align(*case['input'])
            self.assertEqual(output, case['output'])

    def test_align_right(self):
        cases = [
            {'input': ['TEST', 3, ' '], 'output': 'TEST'},
            {'input': ['TEST', 4, ' '], 'output': 'TEST'},
            {'input': ['TEST', 5, ' '], 'output': ' TEST'},
            {'input': ['TEST', 5, '0'], 'output': '0TEST'},
        ]

        for case in cases:
            output = Alignment.RIGHT.align(*case['input'])
            self.assertEqual(output, case['output'])


class TestFieldTypeValidation(TestCase):
    def test_integer_field_type(self):
        cases = [
            {'input': '123', 'output': True},
            {'input': '0123', 'output': True},
            {'input': 'TEST', 'output': False},
            {'input': '1TEST', 'output': False},
            {'input': ' 123456789', 'output': False},
        ]
        for case in cases:
            output = IntegerFieldType.is_valid(case['input'])
            self.assertEqual(output, case['output'], case['input'])
            if not output:
                self.assertRaises(
                    ValueMismatchesFieldTypeError,
                    IntegerFieldType.is_valid, case['input'], raise_exc=True,
                    msg=ValueMismatchesFieldTypeError.msg_format.format(
                        case['input'], IntegerFieldType.regex.pattern)
                )

    def test_alphanum_field_type(self):
        pass_cases = [
            'TEST',
            'test',
            'TEST test',
            'Te. st',
            '123',
            '1.23',
            '0123',
            '1TEST',
            ' 123456789',
            'TEST&',
            '(TEST)',
            'TEST-test',
        ]
        fail_cases = [
            'TesT:',
            '#test',
            '%test%',
            'test!',
            '$1.09',
            'double"quote me on this'
        ]
        for case in pass_cases:
            output = AlphaNumFieldType.is_valid(case)
            self.assertTrue(output, case)

        for case in fail_cases:
            output = AlphaNumFieldType.is_valid(case)
            self.assertFalse(output, case)

            with self.assertRaises(
                    ValueMismatchesFieldTypeError,
                    msg=ValueMismatchesFieldTypeError.msg_format.format(
                        case, AlphaNumFieldType.regex.pattern)
                ):
                AlphaNumFieldType.is_valid(case, raise_exc=True)

    def test_blank_padded_routing_number_field_type(self):
        cases = [
            {'input': '012345678', 'output': True},
            {'input': ' 123456789', 'output': True},
            {'input': '123', 'output': False},
            {'input': ' 123', 'output': False},
            {'input': ' 1234567890', 'output': False},
            {'input': '1234567890', 'output': False},
            {'input': 'TEST', 'output': False},
            {'input': '1TEST', 'output': False},
        ]
        for case in cases:
            output = BlankPaddedRoutingNumberFieldType.is_valid(case['input'])
            self.assertEqual(output, case['output'], "\"{}\"".format(case['input']))
            if not output:
                self.assertRaises(
                    ValueMismatchesFieldTypeError,
                    BlankPaddedRoutingNumberFieldType.is_valid, case['input'], raise_exc=True,
                    msg=ValueMismatchesFieldTypeError.msg_format.format(
                        case['input'], BlankPaddedRoutingNumberFieldType.regex.pattern)
                )


class TestFieldIntegerFieldType(TestCase):
    def test_field_int_default_value_as_string(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, 1, default="1")
        self.assertEqual(Field(field_def).value, "1")
    
    def test_field_int_default_value_as_int(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1, default=1)
        self.assertEqual(Field(field_def).value, "1")
    
    def test_field_int_default_record_type_field_padded_int_length(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=2, default=1)
        self.assertEqual(Field(field_def).value, "01")

    def test_field_int_override_default_value(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1, default=1)
        self.assertEqual(Field(field_def, "2").value, "2")

    def test_field_int_pass_integer_value(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1)
        self.assertEqual(Field(field_def, 2).value, "2")

    def test_field_int_not_required_no_default(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1, required=False)
        self.assertEqual(Field(field_def).value, "0")
    
    def test_field_int_required_no_default(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1)
        self.assertRaises(EmptyRequiredFieldError, Field, field_def)

    def test_field_int_truncates_front(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1)
        self.assertEqual(Field(field_def, "23").value, "3")

    def test_field_int_bad_input(self):
        field_def = FieldDefinition('record_type', IntegerFieldType, length=1)
        self.assertRaises(ValueMismatchesFieldTypeError, Field, field_def, "abc")


class TestFieldAlphaNumFieldType(TestCase):
    def test_field_alphanum_default_value_as_string(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, 1, default="1")
        self.assertEqual(Field(field_def).value, "1")
    
    def test_field_alphanum_default_value_as_int(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=1, default=1)
        self.assertEqual(Field(field_def).value, "1")
    
    def test_field_alphanum_default_record_type_field_padded_int_length(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=2, default=1)
        self.assertEqual(Field(field_def).value, "1 ")

    def test_field_alphanum_override_default_value(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=1, default=1)
        self.assertEqual(Field(field_def, "2").value, "2")

    def test_field_alphanum_pass_integer_value(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=1)
        self.assertEqual(Field(field_def, 2).value, "2")

    def test_field_alphanum_not_required_no_default(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=1, required=False)
        self.assertEqual(Field(field_def).value, " ")
    
    def test_field_alphanum_required_no_default(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=1)
        self.assertRaises(EmptyRequiredFieldError, Field, field_def)

    def test_field_alphanum_truncates_trailing(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=1)
        self.assertEqual(Field(field_def, "23").value, "2")

    def test_field_alphanum_bad_input(self):
        field_def = FieldDefinition('record_type', AlphaNumFieldType, length=2)
        self.assertRaises(ValueMismatchesFieldTypeError, Field, field_def, "#freetheevil")


class TestBlankPaddedRoutingNumberFieldType(TestCase):
    def test_field_valid_str_10_length(self):
        field_def = FieldDefinition(
            'routing_num', BlankPaddedRoutingNumberFieldType, length=10, auto_correct_input=True)
        self.assertEqual(Field(field_def, " 123456789").value, " 123456789")
    
    def test_field_valid_str_9_length(self):
        field_def = FieldDefinition(
            'routing_num', BlankPaddedRoutingNumberFieldType, length=10, auto_correct_input=True)
        self.assertEqual(Field(field_def, "123456789").value, " 123456789")

    def test_field_valid_int_9_length(self):
        field_def = FieldDefinition(
            'routing_num', BlankPaddedRoutingNumberFieldType, length=10, auto_correct_input=True)
        self.assertEqual(Field(field_def, 123456789).value, " 123456789")
    
    def test_field_autocorrect_invalid_int_8_length(self):
        field_def = FieldDefinition(
            'routing_num', BlankPaddedRoutingNumberFieldType, length=10, auto_correct_input=True)
        self.assertEqual(Field(field_def, 12345678).value, " 012345678")

    def test_field_invalid_input(self):
        cases = ['1e', 'yours"truly', '1234567890', 1.2]
        field_def = FieldDefinition(
            'routing_num', BlankPaddedRoutingNumberFieldType, length=10, auto_correct_input=True)
        for case in cases:
            self.assertRaises(ValueMismatchesFieldTypeError, Field, field_def, case)


class TestDateFieldType(TestCase):
    def test_field_date_valid_input(self):
        field_def = FieldDefinition('file_date', DateFieldType, length=6, auto_correct_input=True)
        self.assertEqual(Field(field_def, '221105').value, '221105')
    
    def test_field_date_valid_input_int(self):
        field_def = FieldDefinition('file_date', DateFieldType, length=6, auto_correct_input=True)
        self.assertEqual(Field(field_def, 221105).value, '221105')
    
    def test_field_date_default_now(self):
        field_def = FieldDefinition('file_date', DateFieldType, length=6, auto_correct_input=True, default='NOW')
        self.assertEqual(Field(field_def).value, datetime.date.today().strftime('%y%m%d'))

    def test_field_date_input_now(self):
        field_def = FieldDefinition('file_date', DateFieldType, length=6, auto_correct_input=True)
        self.assertEqual(Field(field_def, 'now').value, datetime.date.today().strftime('%y%m%d'))

    def test_field_date_empty(self):
        field_def = FieldDefinition('file_date', DateFieldType, length=6, auto_correct_input=True, required=False)
        self.assertEqual(Field(field_def).value, datetime.date.today().strftime(' ' * 6))
    
    def test_field_date_required(self):
        field_def = FieldDefinition('file_date', DateFieldType, length=6, auto_correct_input=True)
        self.assertRaises(EmptyRequiredFieldError, Field, field_def)
    