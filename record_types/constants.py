"""Defines constants shared by record types and record fields."""

import enum


class BatchServiceClassCode(enum.IntEnum):
    MIXED = 200
    CREDITS = 220
    DEBITS = 225

    def __str__(self) -> str:
        return str(self.value)


class TransactionCode(enum.IntEnum):
    CHECKING_CREDIT = 22
    CHECKING_CREDIT_PRENOTE = 23
    CHECKING_DEBIT = 27
    CHECKING_DEBIT_PRENOTE = 28
    SAVINGS_CREDIT = 32
    SAVINGS_CREDIT_PRENOTE = 33
    SAVINGS_DEBIT = 37
    SAVINGS_DEBIT_PRENOTE = 38

    def __str__(self) -> str:
        return str(self.value)
    
    def is_credit(self) -> bool:
        return self.value % 10 in [2, 3]
    
    def is_debit(self) -> bool:
        return self.value % 10 in [7, 8]

    def is_prenote(self) -> bool:
        return self.value % 10 in [3, 8]

    def is_checking(self) -> bool:
        return self.value // 10 == 2

    def is_savings(self) -> bool:
        return self.value // 10 == 3


class BatchStandardEntryClassCode(enum.Enum):
    PPD = enum.auto()
    ARC = enum.auto()
    BOC = enum.auto()
    CCD = enum.auto()
    CIE = enum.auto()
    CTX = enum.auto()
    IAT = enum.auto()
    POP = enum.auto()
    RCK = enum.auto()
    TEL = enum.auto()
    WEB = enum.auto()

    @property
    def value(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class AutoDateInput(enum.Enum):
    NOW = enum.auto()
    TOMORROW = enum.auto()

    @property
    def value(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


RECORD_SIZE = 94

FILE_HEADER_RECORD_TYPE_CODE = 1
FILE_HEADER_PRIORITY_CODE = 1
FILE_HEADER_DEFAULT_FILE_ID_MODIFIER = 'A'
FILE_HEADER_BLOCKING_FACTOR = 10
FILE_HEADER_FORMAT_CODE = 1

BATCH_HEADER_RECORD_TYPE_CODE = 5
BATCH_DEFAULT_SERVICE_CLASS_CODE = BatchServiceClassCode.MIXED
BATCH_HEADER_DEFAULT_STANDARD_ENTRY_CLASS_CODE = BatchStandardEntryClassCode.PPD
BATCH_HEADER_DEFAULT_ORIGINATOR_STATUS_CODE = 1

ENTRY_DETAIL_RECORD_TYPE_CODE = 6
ENTRY_DETAIL_DEFAULT_ADDENDA_RECORD_INDICATOR = 1

ADDENDA_RECORD_TYPE_CODE = 7
ADDENDA_TYPE_CODE = 5
ADDENDA_DEFAULT_SEQUENCE_NUMBER = 1

BATCH_CONTROL_RECORD_TYPE_CODE = 8

FILE_CONTROL_RECORD_TYPE_CODE = 9
