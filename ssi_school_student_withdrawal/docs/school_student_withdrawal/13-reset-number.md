# Reset Document Number — Student Withdrawal

> **Module:** ssi*school_student_withdrawal\
> **Model:** `school_student_withdrawal`\
> **Menu:** School > Student Activities > Student Withdrawals\
> **Actor:** user in group \_School Student Withdrawal — Validator*\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Config:** An active `sequence.template` exists for this model.
- **Config:** An active `policy.template` grants `manual_number_ok` for state `draft` to
  the actor's group.
- **Access:** User is in group _School Student Withdrawal — Validator_.

## Flow

1. Open the **School > Student Activities > Student Withdrawals** menu.
2. Open the record whose document number will be reset.
3. Click the **Reset Document Number** button (or edit the **# Document** field directly
   and change it to **/**).
4. Click **OK** on the confirmation dialog (only when the button was used).

## Post-Condition

- Document number returns to **/**.
- The record will receive an automatic number when it transitions to **Done**, according
  to the configured sequence.
