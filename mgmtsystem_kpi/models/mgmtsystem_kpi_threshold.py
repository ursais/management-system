# Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MgmtsystemKpiThreshold(models.Model):
    _name = "mgmtsystem.kpi.threshold"
    _description = "KPI Threshold"

    name = fields.Char(required=True)
    range_ids = fields.Many2many(
        "mgmtsystem.kpi.threshold.range",
        "mgmtsystem_kpi_threshold_range_rel",
        "threshold_id",
        "range_id",
        string="Ranges",
    )
    valid = fields.Boolean(compute="_compute_valid", store=True)
    invalid_message = fields.Char(compute="_compute_valid")
    kpi_ids = fields.One2many("mgmtsystem.kpi", "threshold_id", string="KPIs")
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    @api.depends(
        "range_ids",
        "range_ids.valid",
        "range_ids.min_value",
        "range_ids.max_value",
    )
    def _compute_valid(self):
        for threshold in self:
            valid = True
            message = ""
            ranges = threshold.range_ids.filtered("valid").sorted("min_value")
            for index, current_range in enumerate(ranges):
                if index == 0:
                    continue
                previous_range = ranges[index - 1]
                if previous_range.max_value > current_range.min_value:
                    valid = False
                    message = (
                        "2 of your ranges are overlapping! Please make sure "
                        "your ranges do not overlap."
                    )
                    break
            threshold.valid = valid
            threshold.invalid_message = message

    @api.constrains("range_ids")
    def _check_range_overlap(self):
        for threshold in self:
            if not threshold.valid:
                raise ValidationError(
                    self.env._(
                        "2 of your ranges are overlapping! Please make sure your "
                        "ranges do not overlap."
                    )
                )

    def get_color(self, kpi_value):
        self.ensure_one()
        color = "#FFFFFF"
        for range_record in self.range_ids.filtered("valid"):
            if range_record.min_value <= kpi_value <= range_record.max_value:
                color = range_record.color
        return color
