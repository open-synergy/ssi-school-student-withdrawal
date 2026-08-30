# Create School Student Withdrawal

> **Module:** ssi_school_student_withdrawal_operating_unit\
> **Extends:** ssi_school_student_withdrawal — model `school_student_withdrawal`, action
> `01-create`

## Additional Fields

When this module is installed, the create form gains one field, visible only when the
_Multi Operating Unit_ feature is enabled (Settings > Operating Unit):

- **Operating Unit**: Automatically filled with the acting user's default operating
  unit. Change if needed.

## Modified — Record Visibility

- The withdrawal list is now filtered by operating unit (record rule): a user only sees
  withdrawal records belonging to operating units they are assigned to. This is not a
  Flow step.
