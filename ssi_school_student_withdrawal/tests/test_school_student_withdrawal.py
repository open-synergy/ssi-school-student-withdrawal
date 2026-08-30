# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolStudentWithdrawal(YamlTransactionCase):
    """Cover the ``school_student_withdrawal`` full workflow, the
    student-state and single-active-withdrawal constraints, through
    the YAML scenario file."""

    def test_school_student_withdrawal(self):
        """Run every scenario in test_data_school_student_withdrawal.yaml."""
        self.run_yaml_scenario("test_data_school_student_withdrawal.yaml")
