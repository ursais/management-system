# Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

RE_SELECT_QUERY = re.compile(
    r".*("
    + "|".join(
        (
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
            "GRANT",
            "REVOKE",
            "INDEX",
        )
    )
    + ")"
)


def is_select_query(query):
    """Check if sql query is a SELECT statement."""
    return not RE_SELECT_QUERY.match(query.upper())


def extract_value_from_rows(rows):
    """Return the numeric value from a single-row query result."""
    if not rows:
        return None
    row = rows[0]
    if isinstance(row, dict):
        return row.get("value")
    if isinstance(row, (list, tuple)) and row:
        return row[0]
    return None


class MgmtsystemKpiThresholdRange(models.Model):
    _name = "mgmtsystem.kpi.threshold.range"
    _description = "KPI Threshold Range"

    name = fields.Char(required=True)
    valid = fields.Boolean(compute="_compute_valid", store=True)
    invalid_message = fields.Char(compute="_compute_valid")
    min_type = fields.Selection(
        [
            ("static", "Fixed value"),
            ("python", "Python Code"),
            ("local", "SQL - Local DB"),
        ],
        required=True,
        default="static",
    )
    min_value = fields.Float(compute="_compute_min_value")
    min_fixed_value = fields.Float(string="Minimum")
    min_code = fields.Text(string="Minimum Computation Code")
    max_type = fields.Selection(
        [
            ("static", "Fixed value"),
            ("python", "Python Code"),
            ("local", "SQL - Local DB"),
        ],
        required=True,
        default="static",
    )
    max_value = fields.Float(compute="_compute_max_value")
    max_fixed_value = fields.Float(string="Maximum")
    max_code = fields.Text(string="Maximum Computation Code")
    color = fields.Char(
        required=True,
        help="RGB code with #",
        default="#FFFFFF",
    )
    threshold_ids = fields.Many2many(
        "mgmtsystem.kpi.threshold",
        "mgmtsystem_kpi_threshold_range_rel",
        "range_id",
        "threshold_id",
        string="Thresholds",
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    def _compute_bound_value(self, bound_type):
        self.ensure_one()
        if bound_type == "min":
            value_type = self.min_type
            fixed_value = self.min_fixed_value
            code = self.min_code
        else:
            value_type = self.max_type
            fixed_value = self.max_fixed_value
            code = self.max_code

        if value_type == "local" and code and is_select_query(code):
            self.env.cr.execute(code)
            return extract_value_from_rows(self.env.cr.dictfetchall())
        if value_type == "python" and code:
            return safe_eval(code)
        if value_type == "static":
            return fixed_value
        return None

    @api.depends(
        "min_type",
        "min_fixed_value",
        "min_code",
        "max_type",
        "max_fixed_value",
        "max_code",
    )
    def _compute_min_value(self):
        for record in self:
            record.min_value = record._compute_bound_value("min") or 0.0

    @api.depends(
        "min_type",
        "min_fixed_value",
        "min_code",
        "max_type",
        "max_fixed_value",
        "max_code",
    )
    def _compute_max_value(self):
        for record in self:
            record.max_value = record._compute_bound_value("max") or 0.0

    @api.depends("min_value", "max_value")
    def _compute_valid(self):
        for record in self:
            if record.max_value < record.min_value:
                record.valid = False
                record.invalid_message = (
                    "Minimum value is greater than the maximum value! "
                    "Please adjust them."
                )
            else:
                record.valid = True
                record.invalid_message = ""
