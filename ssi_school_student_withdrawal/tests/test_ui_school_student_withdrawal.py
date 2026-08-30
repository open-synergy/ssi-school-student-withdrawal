# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolStudentWithdrawal(HttpSavepointCase):
    """Tour tests for the ``school_student_withdrawal`` IK."""

    @classmethod
    def setUpClass(cls):
        """Create every Pre-Condition fixture required by the 12 tours.

        Each tour gets its own isolated grade type / school / grade /
        grade class / academic year & term / student, brought to the
        Enrolled state via ``_create_open_enrollment``, so
        state-changing tours (confirm, approve, reject, cancel,
        restart, ...) never interfere with each other's data.
        """
        super().setUpClass()
        cls.admin = cls.env.ref("base.user_admin")

        # Config Pre-Condition shared by 10-cancel.md: a cancel reason
        # usable on any model.
        cls.cancel_reason = cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR SW Cancel Reason",
                "code": "TOUR-SW-CANCEL",
                "global_use": True,
            }
        )

        # Config Pre-Condition for 16-print.md.
        cls.print_report_action = cls.env["ir.actions.report"].create(
            {
                "name": "TOUR Student Withdrawal Report",
                "model": "school_student_withdrawal",
                "report_type": "qweb-pdf",
                "report_name": (
                    "ssi_school_student_withdrawal."
                    "tour_school_student_withdrawal_report"
                ),
            }
        )
        cls.env["print_document_type"].create(
            {
                "name": "TOUR SW Print Type",
                "model_id": cls.env["ir.model"]._get_id("school_student_withdrawal"),
                "report_ids": [(6, 0, [cls.print_report_action.id])],
            }
        )

        # Config Pre-Condition for 14-restart-approval.md -- same
        # reasoning as ssi_school's test_ui_school_student_mutation.py:
        # policy_template/school_student_withdrawal.xml does not ship
        # a policy.template_detail granting restart_approval_ok, so
        # it is supplied here directly.
        policy_template = cls.env.ref(
            "ssi_school_student_withdrawal.policy_template_school_student_withdrawal"
        )
        state_field = cls.env["ir.model.fields"].search(
            [
                ("model_id.model", "=", "school_student_withdrawal"),
                ("name", "=", "state"),
            ],
            limit=1,
        )
        state_confirm = cls.env["ir.model.fields.selection"].search(
            [
                ("field_id", "=", state_field.id),
                ("value", "=", "confirm"),
            ],
            limit=1,
        )
        restart_approval_field = cls.env["ir.model.fields"].search(
            [
                ("model_id.model", "=", "school_student_withdrawal"),
                ("name", "=", "restart_approval_ok"),
            ],
            limit=1,
        )
        user_group = cls.env.ref(
            "ssi_school_student_withdrawal.school_student_withdrawal_user_group"
        )
        cls.env["policy.template_detail"].create(
            {
                "template_id": policy_template.id,
                "field_id": restart_approval_field.id,
                "restrict_state": True,
                "state_ids": [(6, 0, state_confirm.ids)],
                "restrict_user": True,
                "computation_method": "use_group",
                "group_ids": [(6, 0, [user_group.id])],
                "restrict_additional": False,
            }
        )

        # 01-create.md -- no withdrawal record is pre-created; the
        # create tour creates a new one. It only needs an Enrolled
        # student to pick from the list.
        cls._create_open_enrollment("CR", "Create")

        # 02-edit.md -- Draft record to edit.
        data_ed = cls._create_open_enrollment("ED", "Edit")
        cls.withdrawal_edit = cls._create_withdrawal(data_ed)

        # 03-delete.md -- Draft record to delete.
        data_dl = cls._create_open_enrollment("DL", "Delete")
        cls.withdrawal_delete = cls._create_withdrawal(data_dl)

        # 04-confirm.md -- Draft record to confirm.
        data_co = cls._create_open_enrollment("CO", "Confirm")
        cls.withdrawal_confirm = cls._create_withdrawal(data_co)

        # 05-approve.md -- Waiting for Approval record to approve.
        data_ap = cls._create_open_enrollment("AP", "Approve")
        cls.withdrawal_approve = cls._create_withdrawal(data_ap)
        cls.withdrawal_approve.with_user(cls.admin).action_confirm()

        # 06-reject.md -- Waiting for Approval record to reject.
        data_rj = cls._create_open_enrollment("RJ", "Reject")
        cls.withdrawal_reject = cls._create_withdrawal(data_rj)
        cls.withdrawal_reject.with_user(cls.admin).action_confirm()

        # 10-cancel.md -- Waiting for Approval record to cancel.
        data_cn = cls._create_open_enrollment("CN", "Cancel")
        cls.withdrawal_cancel = cls._create_withdrawal(data_cn)
        cls.withdrawal_cancel.with_user(cls.admin).action_confirm()

        # 12-restart.md -- Cancelled record to restart.
        data_rs = cls._create_open_enrollment("RS", "Restart")
        cls.withdrawal_restart = cls._create_withdrawal(data_rs)
        cls.withdrawal_restart.with_user(cls.admin).action_confirm()
        cls.withdrawal_restart.with_user(cls.admin).action_cancel(cls.cancel_reason)

        # 13-reset-number.md -- Draft record with a manually-set
        # document number.
        data_rn = cls._create_open_enrollment("RN", "Reset Number")
        cls.withdrawal_reset_number = cls._create_withdrawal(data_rn)
        cls.withdrawal_reset_number.write({"name": "TOUR-SW-MANUAL-001"})

        # 14-restart-approval.md -- Waiting for Approval record whose
        # approval process is stalled.
        data_ra = cls._create_open_enrollment("RA", "Restart Approval")
        cls.withdrawal_restart_approval = cls._create_withdrawal(data_ra)
        cls.withdrawal_restart_approval.with_user(cls.admin).action_confirm()
        cls.withdrawal_restart_approval.sudo().approval_ids.unlink()
        cls.withdrawal_restart_approval.sudo().write({"approval_template_id": False})

        # 16-print.md -- any state is usable per the IK; a fresh Draft
        # record is enough.
        data_pr = cls._create_open_enrollment("PR", "Print")
        cls.withdrawal_print = cls._create_withdrawal(data_pr)

        # 17-reload-template-policy.md -- any state is usable per the
        # IK; a fresh Draft record is enough.
        data_rt = cls._create_open_enrollment("RT", "Reload Policy")
        cls.withdrawal_reload_template_policy = cls._create_withdrawal(data_rt)

    @classmethod
    def _create_open_enrollment(cls, suffix, label):
        """Build one isolated grade/school/class/year/term/enrollment.

        Brings a new Enrollment to Open status via Confirm + Approve
        (run as ``base.user_admin``, who holds the Validator group so
        the confirm_ok/approve_ok policy fields compute True), which
        also moves the student to the "enrol" state via the
        enrollment's post_open hook.

        :param suffix: short unique code suffix for this fixture set.
        :param label: action label (e.g. "Create", "Edit") used to
            build the tour marker name "TOUR SW <label> Student", kept
            in sync with the literals used by
            school_student_withdrawal_tour.js.
        :return: dict with the created records, keyed by role.
        """
        grade_type = cls.env["school_grade_type"].create(
            {
                "name": "TOUR SW Grade Type %s" % suffix,
                "code": "GTSW%s" % suffix,
                "sequence": 10,
            }
        )
        school = cls.env["school"].create(
            {
                "name": "TOUR SW School %s" % suffix,
                "code": "SCHSW%s" % suffix,
                "grade_type_id": grade_type.id,
            }
        )
        grade = cls.env["school_grade"].create(
            {
                "name": "TOUR SW Grade %s" % suffix,
                "code": "GSW%s" % suffix,
                "sequence": 10,
                "type_id": grade_type.id,
            }
        )
        grade_class = cls.env["school_grade_class"].create(
            {
                "name": "TOUR SW %s Class" % label,
                "code": "CLSW%s" % suffix,
                "school_id": school.id,
                "grade_id": grade.id,
                "capacity": 30,
            }
        )
        year = cls.env["school_academic_year"].create(
            {
                "name": "TOUR SW Year %s" % suffix,
                "code": "AYSW%s" % suffix,
                "date_start": "2024-07-01",
                "date_end": "2025-06-30",
            }
        )
        term = cls.env["school_academic_term"].create(
            {
                "name": "TOUR SW Term %s" % suffix,
                "code": "TMSW%s" % suffix,
                "date_start": "2024-07-01",
                "date_end": "2024-12-31",
                "year_id": year.id,
                "enrollment_state": "open",
            }
        )
        student_name = "TOUR SW %s Student" % label
        contact = cls.env["res.partner"].create({"name": "%s Contact" % student_name})
        student = cls.env["school_student"].create(
            {
                "name": student_name,
                "code": "STUSW%s" % suffix,
                "contact_id": contact.id,
                "school_id": school.id,
            }
        )
        enrollment = cls.env["school_enrollment"].create(
            {
                "date": "2024-07-01",
                "academic_year_id": year.id,
                "academic_term_id": term.id,
                "school_id": school.id,
                "grade_id": grade.id,
                "grade_class_id": grade_class.id,
                "student_id": student.id,
                "currency_id": cls.env.company.currency_id.id,
            }
        )
        enrollment.with_user(cls.admin).action_confirm()
        enrollment.invalidate_cache()
        enrollment.with_user(cls.admin).action_approve_approval()
        return {
            "school": school,
            "grade": grade,
            "grade_class": grade_class,
            "student": student,
            "enrollment": enrollment,
        }

    @classmethod
    def _create_withdrawal(cls, data):
        """Create a Draft Resignation withdrawal for ``data``'s student.

        ``user_id`` is set explicitly to ``base.user_admin`` -- see
        the docstring note in
        ``TestUiSchoolStudentGraduation._create_graduation``
        (ssi_school_student_graduation) for why this is required for
        the tour's "admin" session to see the record at all.

        :param data: dict returned by ``_create_open_enrollment``.
        :return: the created ``school_student_withdrawal`` record.
        """
        return cls.env["school_student_withdrawal"].create(
            {
                "date": "2025-06-30",
                "student_id": data["student"].id,
                "reason_type": "resignation",
                "user_id": cls.admin.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_create",
            login="admin",
        )

    def test_edit(self):
        """Run the edit tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/02-edit.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_edit",
            login="admin",
        )

    def test_delete(self):
        """Run the delete tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/03-delete.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_delete",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/04-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/05-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_approve",
            login="admin",
        )

    def test_reject(self):
        """Run the reject tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/06-reject.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_reject",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/10-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_cancel",
            login="admin",
        )

    def test_restart(self):
        """Run the restart tour for ``school_student_withdrawal``.

        IK: docs/school_student_withdrawal/12-restart.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_restart",
            login="admin",
        )

    def test_reset_number(self):
        """Run the reset document number tour.

        IK: docs/school_student_withdrawal/13-reset-number.md
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_reset_number",
            login="admin",
        )

    def test_restart_approval(self):
        """Run the restart approval process tour.

        IK: docs/school_student_withdrawal/14-restart-approval.md

        Config Pre-Condition note: policy_template/school_student_
        withdrawal.xml does not ship a policy.template_detail granting
        restart_approval_ok, so this HttpCase's setUpClass supplies
        that detail directly.
        """
        self.start_tour(
            "/web",
            (
                "ssi_school_student_withdrawal_school_student_withdrawal_"
                "restart_approval"
            ),
            login="admin",
        )

    def test_print(self):
        """Assert the Print wizard opens then close it, without printing.

        IK: docs/school_student_withdrawal/16-print.md

        Boundary: the resulting report action is an
        ``ir.actions.act_url`` download with no DOM "finished" signal --
        clicking through it could hang headless Chrome.
        """
        self.start_tour(
            "/web",
            "ssi_school_student_withdrawal_school_student_withdrawal_print",
            login="admin",
        )

    def test_reload_template_policy(self):
        """Run the reload template policy tour.

        IK: docs/school_student_withdrawal/17-reload-template-policy.md

        Boundary: action_reload_policy_template returns nothing and
        triggers no dialog; the tour only proves the button on the
        Policies tab is reachable and clickable, and that the form
        survives the click without error.
        """
        self.start_tour(
            "/web",
            (
                "ssi_school_student_withdrawal_school_student_withdrawal_"
                "reload_template_policy"
            ),
            login="admin",
        )
