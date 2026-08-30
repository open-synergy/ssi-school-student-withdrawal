# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolStudentWithdrawalOperatingUnit(
    YamlTransactionCase
):  # pylint: disable=too-few-public-methods
    """Test suite for the ``operating_unit_id`` field on withdrawals.

    Exercises the ``school_student_withdrawal`` model added by this
    glue module, checking that an explicitly assigned Operating Unit
    is persisted on the created record.
    """

    def test_school_student_withdrawal_operating_unit(self):
        """Run the YAML scenario covering Operating Unit storage.

        Creates a school student withdrawal with an explicit
        ``operating_unit_id`` and asserts the value is stored as-is
        on the record.
        """
        self.run_yaml_scenario(
            "test_data_school_student_withdrawal_operating_unit.yaml"
        )
