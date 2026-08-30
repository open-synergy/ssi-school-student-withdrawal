# Restart Approval Process — Student Withdrawal

> **Module:** ssi*school_student_withdrawal\
> **Model:** `school_student_withdrawal`\
> **Menu:** School > Student Activities > Student Withdrawals\
> **Actor:** user in group \_School Student Withdrawal — User*\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**, and the approval process is stalled
  (for example, the record currently has no approval template assigned, or the assigned
  template no longer matches).
- **Config:** An active `policy.template` for this model grants `restart_approval_ok`
  for state `confirm` to the actor's group.
- **Config:** An active `approval.template` for this model matches this record, with an
  approver group configured for its approval level, so the process can be rebuilt once
  restarted.
- **Access:** User is in group _School Student Withdrawal — User_.

## Flow

1. Open the **School > Student Activities > Student Withdrawals** menu.
2. Open the record whose approval process is stalled.
3. Click the **Restart Approval Process** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status remains **Waiting for Approval**.
- The existing approval records are discarded and a new approval process is created from
  the approval template that now matches the record.
