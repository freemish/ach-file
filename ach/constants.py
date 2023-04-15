"""Defines constants shared by record types and record fields."""

import enum


class BatchServiceClassCode(enum.IntEnum):
    """
    Represents whether a batch contains only credits,
    only debits, or both.
    """

    MIXED = 200
    CREDITS = 220
    DEBITS = 225

    def __str__(self) -> str:
        return str(self.value)


class TransactionCode(enum.IntEnum):
    """
    Represents type of transaction:
        - target is savings or checking account
        - action is crediting the account or debiting the account
        - whether is a dry-run (prenote) or is immediately effective
    """

    CHECKING_CREDIT = 22
    CHECKING_CREDIT_PRENOTE = 23
    CHECKING_DEBIT = 27
    CHECKING_DEBIT_PRENOTE = 28
    SAVINGS_CREDIT = 32
    SAVINGS_CREDIT_PRENOTE = 33
    SAVINGS_DEBIT = 37
    SAVINGS_DEBIT_PRENOTE = 38

    @classmethod
    def _missing_(cls, value):
        return cls._create_pseudo_member(value)

    # pylint: disable=attribute-defined-outside-init
    @classmethod
    def _create_pseudo_member(cls, value):
        pseudo_member = cls._value2member_map_.get(value, None)
        if pseudo_member is None:
            new_member = int.__new__(cls, value)
            new_member._name_ = f"UNKNOWN_{value}"
            new_member._value_ = value
            pseudo_member = cls._value2member_map_.setdefault(value, new_member)
        return pseudo_member

    def __str__(self) -> str:
        return str(self.value)

    def is_credit(self) -> bool:
        """Return True if TransactionCode credits the account, else False"""
        return self.value % 10 < 5

    def is_debit(self) -> bool:
        """Return True if TransactionCode debits the account, else False"""
        return self.value % 10 >= 5

    def is_prenote(self) -> bool:
        """Return True if TransactionCode is only a dry-run transaction (prenote), else False"""
        return self.value % 10 in [3, 8]

    def is_checking(self) -> bool:
        """Return True if transaction is against a checking account, else False"""
        return self.value // 10 == 2

    def is_savings(self) -> bool:
        """Return True if transaction is against a savings account, else False"""
        return self.value // 10 == 3


class BatchStandardEntryClassCode(enum.Enum):
    """
    Represents one of several common SEC codes.
    See this site for more details:
    https://achdevguide.nacha.org/ach-file-details
    """

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

    # pylint: disable=invalid-overridden-method
    @property
    def value(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class AutoDateInput(enum.Enum):
    """
    If values "NOW" or "TOMORROW"
    are put into a DateFieldType or TimeFieldType Field,
    the Field will autogenerate a date given today's datetime.
    """

    NOW = enum.auto()
    TOMORROW = enum.auto()

    # pylint: disable=invalid-overridden-method
    @property
    def value(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


RECORD_SIZE = 94

FILE_HEADER_RECORD_TYPE_CODE = 1
FILE_HEADER_PRIORITY_CODE = 1
FILE_HEADER_DEFAULT_FILE_ID_MODIFIER = "A"
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
