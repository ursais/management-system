# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMgmtsystemKpi(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.category = cls.env["mgmtsystem.kpi.category"].create({"name": "Quality"})
        cls.range_good = cls.env["mgmtsystem.kpi.threshold.range"].create(
            {
                "name": "Good",
                "min_type": "static",
                "min_fixed_value": 0.0,
                "max_type": "static",
                "max_fixed_value": 50.0,
                "color": "#00FF00",
            }
        )
        cls.range_bad = cls.env["mgmtsystem.kpi.threshold.range"].create(
            {
                "name": "Bad",
                "min_type": "static",
                "min_fixed_value": 50.0,
                "max_type": "static",
                "max_fixed_value": 100.0,
                "color": "#FF0000",
            }
        )
        cls.threshold = cls.env["mgmtsystem.kpi.threshold"].create(
            {
                "name": "Default threshold",
                "range_ids": [(6, 0, [cls.range_good.id, cls.range_bad.id])],
            }
        )
        cls.kpi = cls.env["mgmtsystem.kpi"].create(
            {
                "name": "Test KPI",
                "category_id": cls.category.id,
                "threshold_id": cls.threshold.id,
                "kpi_type": "python",
                "kpi_code": "42.0",
            }
        )

    def test_compute_kpi_value_python(self):
        self.kpi.compute_kpi_value()
        self.assertEqual(self.kpi.value, 42.0)
        history = self.kpi.history_ids[:1]
        self.assertEqual(history.value, 42.0)
        self.assertEqual(history.color, "#00FF00")

    def test_threshold_overlap_validation(self):
        overlapping_range = self.env["mgmtsystem.kpi.threshold.range"].create(
            {
                "name": "Overlap",
                "min_type": "static",
                "min_fixed_value": 40.0,
                "max_type": "static",
                "max_fixed_value": 60.0,
                "color": "#FFA500",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["mgmtsystem.kpi.threshold"].create(
                {
                    "name": "Invalid threshold",
                    "range_ids": [(6, 0, [self.range_good.id, overlapping_range.id])],
                }
            )

    def test_update_kpi_value_cron(self):
        self.kpi.compute_kpi_value()
        self.kpi.next_execution_date = fields.Datetime.now()
        self.env["mgmtsystem.kpi"].update_kpi_value()
        self.assertEqual(len(self.kpi.history_ids), 2)
