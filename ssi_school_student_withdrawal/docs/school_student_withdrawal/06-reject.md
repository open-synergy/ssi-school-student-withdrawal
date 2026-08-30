# Reject Student Withdrawal

> **Module:** ssi_school_student_withdrawal\
> **Model:** `school_student_withdrawal`\
> **Menu:** School > Student Activities > Student Withdrawals\
> **Actor:** approver on the pending approval level\
> **State:** `confirm` → `reject`\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `reject_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  pending.

## Flow

1. Open the **School > Student Activities > Student Withdrawals** menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**. The student's state is not changed.
