# Approve Student Withdrawal

> **Module:** ssi_school_student_withdrawal\
> **Model:** `school_student_withdrawal`\
> **Menu:** School > Student Activities > Student Withdrawals\
> **Actor:** approver on the pending approval level\
> **State:** `confirm` → `done`\
> **Requires:** `04-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Record:** The student is still in the **Enrolled**, **On Leave**, or **Suspended**
  state.
- **Config:** An active `policy.template` grants `approve_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  **pending**. When the template uses sequential approval, only the first unapproved
  level is pending.

## Flow

1. Open the **School > Student Activities > Student Withdrawals** menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- If all approval levels are fulfilled, status changes automatically to **Done**. The
  student is transitioned depending on **Reason Type**: **Resignation** moves the
  student to the **Resigned** state; **Drop Out / Expelled** and **No News / Whereabouts
  Unknown** both move the student to the **Dropped** state. If the student had an active
  enrollment, that enrollment's **Academic Year Result** is set to **Drop Out**. Both
  `school_student`'s own state machine and this document's status are terminal at this
  point — there is no action in this module to reverse a completed withdrawal.
- If there are still pending approval levels, status remains **Waiting for Approval**
  and the next level becomes pending.

> **Note:** `school_student_withdrawal` does **not** have a manual Finish button
> (`_automatically_insert_done_button` is disabled). The transition to **Done** always
> happens automatically as soon as the last approval level is fulfilled — there is no
> `07-start.md` or `09-finish.md` for this model.
