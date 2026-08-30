# Create Student Withdrawal

> **Module:** ssi*school_student_withdrawal\
> **Model:** `school_student_withdrawal`\
> **Menu:** School > Student Activities > Student Withdrawals\
> **Actor:** user in group \_School Student Withdrawal — User*\
> **State:** `—` → `draft`

## Pre-Condition

- **Data:** The student to be withdrawn is currently in the **Enrolled**, **On Leave**,
  or **Suspended** state (`school_student.state`). This is enforced by a model
  constraint once the withdrawal reaches `confirm` or `done` (needed later by
  `04-confirm` and `05-approve`), but it is not checked while still in Draft.
- **Config:** An active `policy.template` for this model grants `confirm_ok` for state
  `draft` to the actor's group (needed later by `04-confirm`).
- **Access:** User is in group _School Student Withdrawal — User_.

## Flow

1. Open the **School > Student Activities > Student Withdrawals** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Student** _(required)_: Select the student being withdrawn from the school.
   - **Active Enrollment**: Automatically filled, read-only, from the student's
     currently open enrollment (blank if the student has none).
   - **Date**: Defaults to today's date. Change if needed.
   - **Effective Date**: Optional. The date on which the withdrawal takes effect for the
     student.
   - **Reason Type** _(required)_: Select **Drop Out / Expelled**, **Resignation**, or
     **No News / Whereabouts Unknown**.
   - **Reason**: Optional additional explanation, on the **Withdrawal Details** tab.
4. Click **Save**.

## Post-Condition

- A new record is created in **Draft** status.
