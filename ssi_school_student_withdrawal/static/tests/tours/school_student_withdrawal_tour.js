// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_school_student_withdrawal.school_student_withdrawal_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared navigation block reused by every tour below --
    // corresponds to Flow 1 of every school_student_withdrawal IK:
    // "Open the School > Student Activities > Student Withdrawals
    // menu."
    function openWithdrawalList() {
        return [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the Student Activities menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school.menu_school_student_activity"]',
            },
            {
                content: "Open the Student Withdrawals menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_student_withdrawal.school_student_withdrawal_menu"]',
            },
            {
                // Gerbang: tunggu action TUJUAN benar-benar terpasang,
                // bukan sekadar "ada list di layar" (patterns.md skill
                // odoo-development-ui-test §A).
                content: "Student Withdrawals list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Student Withdrawals)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click
                    // action.
                },
            },
        ];
    }

    // Selects an option from an open many2one autocomplete dropdown.
    function pickMany2one(fieldName, label) {
        return [
            {
                content: "Select the " + fieldName + " field value",
                trigger: ".o_field_many2one[name='" + fieldName + "'] input",
                run: "text " + label,
            },
            {
                content: "Pick " + label + " from the dropdown",
                trigger: ".ui-autocomplete .ui-menu-item a:contains(" + label + ")",
                in_modal: false,
            },
        ];
    }

    // Selects an option from a 14.0 <select> Selection field. The
    // <select> itself carries the o_field_widget class (not wrapped in
    // a div), so the selector is a combined tag+class, not a
    // descendant selector (patterns.md skill odoo-development-ui-test
    // "Field selection").
    function pickSelection(fieldName, label) {
        return [
            {
                content: "Select " + label + " for the " + fieldName + " field",
                trigger: "select.o_field_widget[name='" + fieldName + "']",
                run: "text " + label,
            },
        ];
    }

    // Opens the record identified by the unique Student name shown on
    // the list row (used as Pre-Condition test data marker).
    function openRecordByStudent(studentName) {
        return [
            {
                content: "Open the record",
                trigger: ".o_data_row:contains(" + studentName + ") .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                run: function () {
                    // Assertion only.
                },
            },
        ];
    }

    // IK: docs/school_student_withdrawal/01-create.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_create",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            [
                // Flow 2 -- Click the New button. (14.0: "Create")
                {
                    content: "Click New",
                    trigger: ".o_list_button_add",
                    extra_trigger: ".o_list_view",
                },
                {
                    content: "Form is open in edit mode",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only.
                    },
                },
            ],
            // Flow 3 -- Fill in the required field: Student. Active
            // Enrollment is auto-filled, read-only, from the student.
            pickMany2one("student_id", "TOUR SW Create Student"),
            // Flow 3 -- Fill in the required field: Reason Type.
            pickSelection("reason_type", "Resignation"),
            [
                // Flow 4 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // Post-Condition -- a new record is created in Draft
                // status.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/02-edit.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_edit",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Find and open the record to edit.
            openRecordByStudent("TOUR SW Edit Student"),
            [
                // 14.0: a just-opened record is displayed read-only; an
                // explicit Edit click is required before its fields
                // become editable. Not itemized in 02-edit.md's Flow --
                // same documented 14.0 platform mechanic as
                // school_student_mutation_tour.js test_edit.
                {
                    content: "Click the Edit button",
                    trigger: ".o_form_button_edit",
                },
                {
                    content: "Form is now editable",
                    trigger: ".o_form_view.o_form_editable",
                    run: function () {
                        // Assertion only.
                    },
                },
            ],
            // Flow 3 -- Change the required field (Reason Type, from
            // Resignation to Drop Out / Expelled).
            pickSelection("reason_type", "Drop Out / Expelled"),
            [
                // Flow 4 -- Click Save.
                {
                    content: "Save the record",
                    trigger: ".o_form_button_save",
                },

                // Post-Condition -- the record is updated with the new
                // values.
                {
                    content: "Record is saved",
                    trigger: ".o_form_view.o_form_readonly",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/03-delete.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_delete",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            [
                // Flow 2 -- Select the record to delete (check the
                // checkbox).
                {
                    content: "Check the record's selector checkbox",
                    trigger:
                        ".o_data_row:contains(TOUR SW Delete Student) .o_list_record_selector input",
                },

                // Flow 3 -- Click Action > Delete.
                {
                    content: "Open the Action menu",
                    trigger: ".o_cp_action_menus button:contains(Action)",
                },
                {
                    content: "Click Delete",
                    trigger: ".o_cp_action_menus .o_menu_item a",
                    run: function () {
                        var $delete = $(".o_cp_action_menus .o_menu_item a").filter(
                            function () {
                                return $(this).text().trim() === "Delete";
                            }
                        );
                        $delete[0].click();
                    },
                },

                // Flow 4 -- Click OK to confirm.
                {
                    content: "Confirm deletion",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- the selected records are
                // permanently removed from the system.
                {
                    content: "Record no longer in the list",
                    trigger:
                        ".o_list_view:not(:has(.o_data_row:contains(TOUR SW Delete Student)))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/04-confirm.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_confirm",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record to confirm.
            openRecordByStudent("TOUR SW Confirm Student"),
            [
                // Flow 3 -- Click the Confirm button.
                {
                    content: "Click the Confirm button",
                    trigger: ".o_statusbar_buttons button[name='action_confirm']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status changes to Waiting for
                // Approval.
                {
                    content: "Status is Waiting for Approval",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/05-approve.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_approve",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record to approve.
            openRecordByStudent("TOUR SW Approve Student"),
            [
                // Flow 3 -- Click the Approve button.
                {
                    content: "Click the Approve button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_approve_approval']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- the single approval level is
                // fulfilled, so status changes automatically to Done
                // (there is no separate manual Finish step for this
                // model).
                {
                    content: "Status is Done",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='done'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/06-reject.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_reject",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record to reject.
            openRecordByStudent("TOUR SW Reject Student"),
            [
                // Flow 3 -- Click the Reject button.
                {
                    content: "Click the Reject button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_reject_approval']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status changes to Rejected.
                {
                    content: "Status is Rejected",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='reject'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/10-cancel.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_cancel",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record to cancel.
            openRecordByStudent("TOUR SW Cancel Student"),
            [
                // Flow 3 -- Click the Cancel button.
                {
                    content: "Click the Cancel button",
                    trigger: ".o_statusbar_buttons button:enabled:contains('Cancel')",
                    extra_trigger: ".o_form_view",
                },
                {
                    content: "Wizard is open",
                    trigger: ".o_form_view",
                    run: function () {
                        // Assertion only.
                    },
                },

                // Flow 4 -- In the wizard, select the Cancellation
                // Reason (radio widget).
                {
                    content: "Select the cancellation reason",
                    trigger:
                        ".o_field_widget[name='cancel_reason_id'] " +
                        ".o_radio_item:contains(TOUR SW Cancel Reason) input",
                    run: "click",
                },

                // Flow 5 -- Click Confirm.
                {
                    content: "Confirm the wizard",
                    trigger: ".modal-footer button[name='action_confirm']",
                },

                // Flow 6 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the Are you sure? dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status changes to Cancelled.
                {
                    content: "Status is Cancelled",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='cancel'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/12-restart.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_restart",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record to restart.
            openRecordByStudent("TOUR SW Restart Student"),
            [
                // Flow 3 -- Click the Restart button.
                {
                    content: "Click the Restart button",
                    trigger: ".o_statusbar_buttons button[name='action_restart']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status returns to Draft.
                {
                    content: "Status is Draft",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/13-reset-number.md
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_reset_number",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record whose document number will be
            // reset.
            openRecordByStudent("TOUR SW Reset Number Student"),
            [
                // Flow 3 -- Click the Reset Document Number button.
                {
                    content: "Click the Reset Document Number button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_reset_document_number']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- document number returns to "/".
                {
                    content: "Document number is reset (display name shows *)",
                    trigger:
                        ".oe_title .o_field_widget[name='display_name']:contains(*)",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/14-restart-approval.md
    //
    // Config Pre-Condition note: policy_template/school_student_
    // withdrawal.xml does not ship a policy.template_detail granting
    // restart_approval_ok, so the test file's setUpClass supplies it
    // directly.
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_restart_approval",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record whose approval process is
            // stalled.
            openRecordByStudent("TOUR SW Restart Approval Student"),
            [
                // Flow 3 -- Click the Restart Approval Process button.
                {
                    content: "Click the Restart Approval Process button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_reload_approval_template']",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4 -- Click OK on the confirmation dialog.
                {
                    content: "Confirm the dialog",
                    trigger: ".modal-footer button.btn-primary",
                    in_modal: true,
                },

                // Post-Condition -- status remains Waiting for
                // Approval.
                {
                    content: "Status is still Waiting for Approval",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/16-print.md
    //
    // Boundary (patterns.md §Q): same reasoning as
    // school_student_mutation_tour.js test_print -- the tour only
    // proves the wizard opens then closes it, without printing.
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_print",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record to print.
            openRecordByStudent("TOUR SW Print Student"),
            [
                // Flow 3 -- Click Print in the header.
                {
                    content: "Click the Print button",
                    trigger: ".o_statusbar_buttons button:enabled:contains('Print')",
                    extra_trigger: ".o_form_view",
                },

                // Flow 4/5 boundary -- the wizard is proven open, then
                // closed.
                {
                    content: "The Select Report To Print wizard is displayed",
                    trigger: ".modal-title:contains('Select Report To Print')",
                    run: function () {
                        // Assertion only.
                    },
                },
                {
                    content: "Close the wizard",
                    trigger: ".modal-footer button[special='cancel']",
                    in_modal: true,
                },

                // Post-Condition (tour boundary) -- the wizard is
                // closed and the record form is displayed again.
                {
                    content: "Wizard is closed and the form is displayed again",
                    trigger: ".o_form_view",
                    extra_trigger: "body:not(:has(.modal))",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );

    // IK: docs/school_student_withdrawal/17-reload-template-policy.md
    //
    // Boundary: same reasoning as school_student_mutation_tour.js
    // test_reload_template_policy -- no dialog/notification signal.
    tour.register(
        "ssi_school_student_withdrawal_school_student_withdrawal_reload_template_policy",
        {
            test: true,
            url: "/web",
        },
        [].concat(
            // Flow 1 -- Open the Student Withdrawals menu.
            openWithdrawalList(),
            // Flow 2 -- Open the record whose assigned policy template
            // should be re-evaluated.
            openRecordByStudent("TOUR SW Reload Policy Student"),
            [
                // Flow 3 -- On the Policies tab, click Reload Template
                // Policy.
                {
                    content: "Open the Policies tab",
                    trigger: ".o_notebook .nav-link:contains(Policies)",
                },
                {
                    content: "Click the Reload Template Policy button",
                    trigger:
                        ".o_form_view button[name='action_reload_policy_template']:enabled",
                },

                // Post-Condition (tour boundary) -- the form survives
                // the click.
                {
                    content: "Form is intact after the reload",
                    trigger: "body:not(.o_ui_blocked)",
                    extra_trigger:
                        ".o_form_view button[name='action_reload_policy_template']:enabled",
                    run: function () {
                        // Assertion only.
                    },
                },
            ]
        )
    );
});
