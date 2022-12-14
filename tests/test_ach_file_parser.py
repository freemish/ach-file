"""Test file_parser.py"""

from unittest import TestCase

from ach.files import ACHFileContentsParser


test_file = """101 123456780 1234567801409020123A094101YOUR BANK              YOUR COMPANY                   
5200YOUR COMPANY                        1234567890PPDPAYROLL         140903   1123456780000001
62212345678011232132         0000001000               ALICE WANDERDUST        1123456780000001
705HERE IS SOME ADDITIONAL INFORMATION                                             00010000001
627123456780234234234        0000015000               BILLY HOLIDAY           0123456780000002
622123232318123123123        0000001213               RACHEL WELCH            0123456780000003
820000000400370145870000000150000000000022131234567890                         123456780000001
9000001000001000000040037014587000000015000000000002213                                       
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
"""

class TestParser(TestCase):
    def test_parser(self):
        test_file_lines = test_file.splitlines()

        parser = ACHFileContentsParser(test_file)
        records_list = parser.process_records_list()
        ach_file_contents = parser.process_ach_file_contents(records_list)
        
        for i, record in enumerate(records_list):
            self.assertEqual(record.render_record_line(), test_file_lines[i])

        self.assertEqual(ach_file_contents.render_file_contents(), test_file)
