"""Test enum values."""

from unittest import TestCase

from ach.record_types.constants import (
    AutoDateInput, BatchServiceClassCode, BatchStandardEntryClassCode, TransactionCode
)

class TestTransactionCode(TestCase):
    def test_is_prenote(self):
        for e in TransactionCode:
            result = e.is_prenote()
            if str(e) in ['23', '33', '28', '38']:
                self.assertTrue(result, e)
            else:
                self.assertFalse(result, e)

    def test_is_savings(self):
        for e in TransactionCode:
            result = e.is_savings()
            if str(e) in ['32', '33', '37', '38']:
                self.assertTrue(result, e)
            else:
                self.assertFalse(result, e)

    def test_is_checking(self):
        for e in TransactionCode:
            result = e.is_checking()
            if str(e) in ['22', '23', '27', '28']:
                self.assertTrue(result, e)
            else:
                self.assertFalse(result, e)

    def test_not_transaction_code(self):
        self.assertRaises(ValueError, TransactionCode, 56)


class TestAutoDateInput(TestCase):
    def test_stringify(self):
        self.assertEqual([str(x) for x in AutoDateInput], ['NOW', 'TOMORROW'])

    def test_value(self):
        self.assertEqual([x.value for x in AutoDateInput], ['NOW', 'TOMORROW'])


class TestServiceClassCode(TestCase):
    def test_stringify(self):
        self.assertEqual([str(x) for x in BatchServiceClassCode], ['200', '220', '225'])
    
    def test_intenum(self):
        self.assertEqual([x for x in BatchServiceClassCode], [200, 220, 225])


class TestStandardEntryClassCode(TestCase):
    def test_value(self):
        self.assertEqual(
            [x.value for x in BatchStandardEntryClassCode],
            ['PPD', 'ARC', 'BOC', 'CCD', 'CIE', 'CTX', 'IAT', 'POP', 'RCK', 'TEL', 'WEB']
        )
    
    def test_stringify(self):
        self.assertEqual(
            [str(x) for x in BatchStandardEntryClassCode],
            ['PPD', 'ARC', 'BOC', 'CCD', 'CIE', 'CTX', 'IAT', 'POP', 'RCK', 'TEL', 'WEB']
        )
