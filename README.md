# ach-file

[![codecov](https://codecov.io/github/freemish/ach-file/branch/main/graph/badge.svg?token=F9BFHNSRJV)](https://codecov.io/github/freemish/ach-file)

Generates ACH files. Highly configurable and permissive enough to be able to generate a valid ACH file for any originating bank.

## Example

Here is an example of how to use the file builder:

```
from ach.files import ACHFileBuilder
from ach.constants import AutoDateInput, BatchStandardEntryClassCode, TransactionCode


b = ACHFileBuilder(
    destination_routing='012345678',
    origin_id='1234567890', #your company ID in this field
    destination_name='YOUR BANK',
    origin_name='YOUR FINANCIAL INSTITUTION',
)
b.add_batch(
    company_name='YOUR COMPANY', company_identification='1234567890', company_entry_description='Test',
    effective_entry_date=AutoDateInput.TOMORROW, standard_entry_class_code=BatchStandardEntryClassCode.CCD,
)
b.add_entries_and_addendas([
    {
      'transaction_code': TransactionCode.CHECKING_CREDIT,
      'rdfi_routing': '123456789',
      'rdfi_account_number': '65656565',
      'amount': '300',
      'individual_name': 'Janey Test',
    },
    {
      'transaction_code': TransactionCode.CHECKING_DEBIT,
      'rdfi_routing': '123456789',
      'rdfi_account_number': '65656565',
      'amount': '300',
      'individual_name': 'Janey Test',
      'addendas': [
        {'payment_related_information': 'Reversing the last transaction pls and thx'},
      ]
    },
    {
      'transaction_code': TransactionCode.CHECKING_CREDIT,
      'rdfi_routing': '023456789',
      'rdfi_account_number': '45656565',
      'amount': '7000',
      'individual_name': 'Mackey Shawnderson',
      'addendas': [
        {'payment_related_information': 'Where\'s my money'},
      ]
    },
])
```

It has this result:

```
101 012345678 102345678221110    A094101YOUR BANK              YOUR FINANCIAL INSTITUT        
5200YOUR COMPANY                        1234567890CCDTest            221111   1102345670000001
62212345678965656565         0000000300               Janey Test              0102345670000001
62712345678965656565         0000000300               Janey Test              1102345670000002
705Reversing the last transaction pls and thx                                      00010000002
62202345678945656565         0000007000               Mackey Shawnderson      1102345670000003
705Where's my money                                                                00010000003
820000000500270370340000000003000000000073001234567890                         102345670000001
9000001000001000000050027037034000000000300000000007300                                       
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999

```

## Valid Keyword Arguments

Below are tables describing all of the valid input arguments for the callables in the above example.

### File Setting Fields (ACHFileBuilder(...))

| Key Name | FieldType | Required | Default |
| -------- | ---- | -------- | ------- |
|record_type_code|IntegerFieldType|True|1|
|priority_code|IntegerFieldType|True|1|
|destination_routing|BlankPaddedRoutingNumberFieldType|True|None|
|origin_id|AlphaNumFieldType|True|None|
|file_creation_date|DateFieldType|True|"NOW"|
|file_creation_time|TimeFieldType|False|None|
|file_id_modifier|AlphaNumFieldType|True|"A"|
|record size|IntegerFieldType|True|94|
|blocking_factor|IntegerFieldType|True|10|
|format_code|IntegerFieldType|True|1|
|destination_name|AlphaNumFieldType|True|None|
|origin_name|AlphaNumFieldType|True|None|
|reference_code|AlphaNumFieldType|True|""|

### Batch Fields (b.add_batch(...))

| Key Name | FieldType | Required | Default |
| -------- | ---- | -------- | ------- |
|record_type_code|IntegerFieldType|True|5|
|service_class_code|IntegerFieldType|True|200|
|company_name|AlphaNumFieldType|True|None|
|company_discretionary_data|AlphaNumFieldType|False|None|
|company_identification|AlphaNumFieldType|True|None|
|standard_entry_class_code|AlphaNumFieldType|True|"PPD"|
|company_entry_description|AlphaNumFieldType|True|None|
|company_descriptive_date|DateFieldType|False|None|
|effective_entry_date|DateFieldType|True|"TOMORROW"|
|settlement_date|AlphaNumFieldType|False|None|
|originator_status_code|IntegerFieldType|True|1|
|odfi_identification|IntegerFieldType|True|(auto-set)|
|batch_number|IntegerFieldType|True|(auto-set)|

## Entry Fields (b.add_entries_and_addendas([{...}]))

| Key Name | FieldType | Required | Default |
| -------- | ---- | -------- | ------- |
|record_type_code|IntegerFieldType|True|6|
|transaction_code|IntegerFieldType|True|None|
|rdfi_routing|IntegerFieldType|True|None|
|rdfi_account_number|AlphaNumFieldType|True|None|
|amount|IntegerFieldType|True|None|
|individual_identification_number|AlphaNumFieldType|False|None|
|individual_name|AlphaNumFieldType|True|None|
|discretionary_data|AlphaNumFieldType|False|None|
|addenda_record_indicator|IntegerFieldType|True|(auto-set)|
|trace_odfi_identifier|IntegerFieldType|True|(auto-set)|
|trace_sequence_number|IntegerFieldType|True|(auto-set)|
|addendas|List[Dict[Addenda Fields]]|False|None|

## Addenda Fields (b.add_entries_and_addendas([{'addendas': [{...}]}]))

| Key Name | FieldType | Required | Default |
| -------- | ---- | -------- | ------- |
|record_type_code|IntegerFieldType|True|7|
|addenda_type_code|IntegerFieldType|True|5|
|payment_related_information|AlphaNumFieldType|False|None|
|addenda_sequence_number|IntegerFieldType|True|(auto-set)|
|entry_detail_sequence_number|IntegerFieldType|True|(auto-set)|
