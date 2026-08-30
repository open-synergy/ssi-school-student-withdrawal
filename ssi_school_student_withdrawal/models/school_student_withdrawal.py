# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ssi_decorator import ssi_decorator

_ALLOWED_STUDENT_STATES = ("enrol", "on_leave", "suspended")


class SchoolStudentWithdrawal(models.Model):
    """
    Represents a Student Withdrawal transaction: the permanent exit of
    a student from the school, covering three distinct reasons under
    one umbrella document -- Drop Out/Expelled, Resignation, and No
    News/Whereabouts Unknown (tidak ada kabar). The withdrawal reason
    (reason_type) determines the target school_student state:
    Resignation maps to 'resigned', while both Drop Out and No News
    map to 'dropped'. school_student's own state machine
    (_STATE_TRANSITIONS) already blocks re-enrollment directly from
    either of these terminal states, so no additional guard is needed
    here for that. The document follows a simplified approval
    workflow: Draft -> Confirm -> Approve -> Done (+ Cancel from
    draft/confirm/reject). On Done, the student is transitioned via
    the existing action_set_to_dropped()/action_set_to_resigned()
    methods on school_student, and, if the student has an active
    enrollment, that enrollment's academic_year_result is set to
    'drop_out'.
    """

    _name = "school_student_withdrawal"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
    ]
    _description = "Student Withdrawal"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    date = fields.Date(
        string="Date",
        default=lambda r: datetime_date.today(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The date the withdrawal document was created.",
    )
    student_id = fields.Many2one(
        string="Student",
        comodel_name="school_student",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The student being withdrawn from the school.",
    )
    active_enrollment_id = fields.Many2one(
        string="Active Enrollment",
        comodel_name="school_enrollment",
        related="student_id.active_enrollment_id",
        store=True,
        readonly=True,
        compute_sudo=True,
        help=(
            "The student's currently active (open) enrollment. When "
            "set, its academic_year_result is set to 'Drop Out' once "
            "this withdrawal reaches Done."
        ),
    )
    effective_date = fields.Date(
        string="Effective Date",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="The date on which the withdrawal takes effect for the student.",
    )
    reason_type = fields.Selection(
        string="Reason Type",
        selection=[
            ("dropout", "Drop Out / Expelled"),
            ("resignation", "Resignation"),
            ("no_news", "No News / Whereabouts Unknown"),
        ],
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help=(
            "The reason for this withdrawal. Determines the student's "
            "target state on Done: Resignation maps to Resigned, "
            "while Drop Out and No News both map to Dropped."
        ),
    )
    reason = fields.Text(
        string="Reason",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Optional additional explanation for this withdrawal.",
    )

    def _get_target_student_state(self):
        """Resolve the ``school_student`` state this withdrawal leads to.

        ``reason_type`` ``resignation`` maps to ``resigned``; both
        ``dropout`` and ``no_news`` map to ``dropped``.

        :return: ``"resigned"`` or ``"dropped"``
        """
        self.ensure_one()
        if self.reason_type == "resignation":
            return "resigned"
        return "dropped"

    @api.constrains("state", "student_id")
    def _check_student_state_allowed(self):
        """Enforce that ``student_id`` stays in an allowed state.

        Raises ``ValidationError`` for any record whose
        ``_check_student_state_allowed_condition`` returns ``False`` --
        i.e. the withdrawal is ``confirm``/``done`` and the student is
        not Enrolled, On Leave, or Suspended.
        """
        for record in self.sudo():
            if not record._check_student_state_allowed_condition():
                error_message = (
                    _(
                        """
Context: Change student withdrawal state into %s
Database ID: %s
Problem: Student '%s' is not in Enrolled, On Leave, or Suspended
state
Solution: The student must be in Enrolled, On Leave, or Suspended
state before this withdrawal can be confirmed or completed
"""
                    )
                    % (
                        record.state,
                        record.id,
                        record.student_id.name,
                    )
                )
                raise ValidationError(error_message)

    def _check_student_state_allowed_condition(self):
        """Check whether ``student_id`` is in an allowed state.

        Only evaluated while ``state`` is ``confirm`` or ``done`` --
        it returns ``True`` (i.e. no failure) for ``draft`` and any
        other state, and whenever ``student_id`` is empty. Fails
        (returns ``False``) when the student's own ``state`` is not
        one of ``enrol``, ``on_leave``, or ``suspended``.

        :return: ``True`` when the state is allowed, ``False`` otherwise
        """
        self.ensure_one()
        if self.state not in ("confirm", "done"):
            return True
        if not self.student_id:
            return True
        return self.student_id.state in _ALLOWED_STUDENT_STATES

    @api.constrains("state", "student_id")
    def _check_single_active_withdrawal(self):
        """Enforce a single draft/waiting withdrawal per student.

        Raises ``ValidationError`` for any record whose
        ``_check_single_active_withdrawal_condition`` returns
        ``False`` -- i.e. another withdrawal for the same student is
        already ``draft`` or ``confirm``.
        """
        for record in self.sudo():
            if not record._check_single_active_withdrawal_condition():
                error_message = (
                    _(
                        """
Context: Change student withdrawal state into %s
Database ID: %s
Problem: Another withdrawal for student '%s' is already draft or
waiting for approval
Solution: Complete, reject, or cancel the other withdrawal before
confirming this one
"""
                    )
                    % (
                        record.state,
                        record.id,
                        record.student_id.name,
                    )
                )
                raise ValidationError(error_message)

    def _check_single_active_withdrawal_condition(self):
        """Check that no other active withdrawal exists for the student.

        Only evaluated while ``state`` is ``draft`` or ``confirm`` and
        ``student_id`` is set. Fails (returns ``False``) when another
        record matching ``_get_single_active_withdrawal_criteria`` is
        found for the same student.

        :return: ``True`` when no duplicate exists, ``False`` otherwise
        """
        self.ensure_one()
        if self.state not in ("draft", "confirm") or not self.student_id:
            return True
        duplicate = self.search(
            self._get_single_active_withdrawal_criteria(),
        )
        return not duplicate

    def _get_single_active_withdrawal_criteria(self):
        """Build the search domain for a duplicate active withdrawal.

        Extension point: override to widen or narrow what counts as
        a conflicting withdrawal for the same student.

        :return: search domain excluding ``self`` and matching
            ``student_id`` with ``state`` in ``draft``/``confirm``
        """
        self.ensure_one()
        return [
            ("id", "!=", self.id),
            ("student_id", "=", self.student_id.id),
            ("state", "in", ["draft", "confirm"]),
        ]

    @ssi_decorator.pre_done_check()
    def _10_check_ready(self):
        """Run the Done pre-check that guards ``student_id``'s state.

        Triggered by the ``ssi_decorator`` ``pre_done_check`` slot,
        i.e. before this withdrawal is allowed to transition into
        ``done``. Delegates to ``_check_done_student_state_allowed``.
        """
        self.ensure_one()
        self._check_done_student_state_allowed()

    def _check_done_student_state_allowed(self):
        """Guard that ``student_id`` is still in an allowed state.

        Raises ``ValidationError`` when
        ``_check_student_state_allowed_condition`` returns ``False``
        at the moment this withdrawal is about to complete -- i.e.
        the student is no longer Enrolled, On Leave, or Suspended.
        """
        self.ensure_one()
        if not self._check_student_state_allowed_condition():
            error_message = (
                _(
                    """
Context: Complete student withdrawal
Database ID: %s
Problem: Student '%s' is not in Enrolled, On Leave, or Suspended
state
Solution: The student must remain in Enrolled, On Leave, or
Suspended state until this withdrawal is completed
"""
                )
                % (
                    self.id,
                    self.student_id.name,
                )
            )
            raise ValidationError(error_message)

    @ssi_decorator.post_done_action()
    def _20_apply_withdrawal(self):
        """Transition ``student_id`` once the withdrawal is Done.

        Triggered by the ``ssi_decorator`` ``post_done_action`` slot,
        i.e. right after this withdrawal reaches ``done``. Calls
        ``action_set_to_resigned()`` when
        ``_get_target_student_state`` resolves to ``resigned``,
        otherwise ``action_set_to_dropped()``.
        """
        self.ensure_one()
        if self._get_target_student_state() == "resigned":
            self.student_id.sudo().action_set_to_resigned()
        else:
            self.student_id.sudo().action_set_to_dropped()

    @ssi_decorator.post_done_action()
    def _30_set_enrollment_result(self):
        """Mark the student's active enrollment as Drop Out.

        Triggered by the ``ssi_decorator`` ``post_done_action`` slot,
        i.e. right after this withdrawal reaches ``done``. When
        ``active_enrollment_id`` is set, its ``academic_year_result``
        is written to ``drop_out``; otherwise this is a no-op.
        """
        self.ensure_one()
        if self.active_enrollment_id:
            self.active_enrollment_id.sudo().write(
                {
                    "academic_year_result": "drop_out",
                }
            )

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "done_ok",
            "cancel_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
