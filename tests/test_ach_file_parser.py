"""Test file_parser.py"""

from unittest import TestCase

from ach.files import ACHFileContentsParser
from tests import test_file


class TestParser(TestCase):
    def test_parser(self):
        test_file_lines = test_file.splitlines()

        parser = ACHFileContentsParser(test_file)
        records_list = parser.process_records_list()
        ach_file_contents = parser.process_ach_file_contents(records_list)

        for i, record in enumerate(records_list):
            self.assertEqual(record.render_record_line(), test_file_lines[i])

        self.assertEqual(ach_file_contents.render_file_contents(), test_file)

    def test_parse_lines_to_dicts(self):
        parser = ACHFileContentsParser(test_file)
        records_list = parser.process_records_list()
        record_dicts = parser.get_record_fields_dict_list(records_list)
        for i, record_dict in enumerate(record_dicts):
            for key, val in record_dict.items():
                self.assertEqual(val, records_list[i].get_field_value(key))
