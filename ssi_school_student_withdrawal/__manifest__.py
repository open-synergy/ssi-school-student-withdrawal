# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "School Student Withdrawal",
    "version": "14.0.1.1.0",
    "website": "https://simetri-sinergi.id",
    # pylint: disable=line-too-long
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia, Odoo Community Association (OCA)",  # noqa: B950
    # pylint: enable=line-too-long
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_school",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_decorator",
    ],
    "data": [
        "security/ir_module_category/school_student_withdrawal.xml",
        "security/res_group/school_student_withdrawal.xml",
        "security/ir_model_access/school_student_withdrawal.xml",
        "security/ir_rule/school_student_withdrawal.xml",
        "ir_sequence/school_student_withdrawal.xml",
        "sequence_template/school_student_withdrawal.xml",
        "approval_template/school_student_withdrawal.xml",
        "policy_template/school_student_withdrawal.xml",
        "views/school_student_withdrawal.xml",
        "views/assets.xml",
    ],
}
