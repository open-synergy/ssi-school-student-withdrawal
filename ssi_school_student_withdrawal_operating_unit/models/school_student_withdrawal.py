# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolStudentWithdrawal(models.Model):  # pylint: disable=too-few-public-methods
    """
    Extends School Student Withdrawal with single operating unit
    support, restricting each withdrawal document to one operating
    unit.
    """

    _name = "school_student_withdrawal"
    _inherit = [
        "school_student_withdrawal",
        "mixin.single_operating_unit",
    ]
