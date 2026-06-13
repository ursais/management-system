# Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

from .mgmtsystem_kpi_threshold_range import (
    extract_value_from_rows,
    is_select_query,
)

_logger = logging.getLogger(__name__)


class MgmtsystemKpi(models.Model):
    _name = "mgmtsystem.kpi"
    _description = "Key Performance Indicator"

    name = fields.Char(required=True)
    description = fields.Text()
    category_id = fields.Many2one("mgmtsystem.kpi.category", required=True)
    threshold_id = fields.Many2one("mgmtsystem.kpi.threshold", required=True)
    periodicity = fields.Integer(default=1)
    periodicity_uom = fields.Selection(
        [
            ("hour", "Hour"),
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
        ],
        required=True,
        default="day",
    )
    next_execution_date = fields.Datetime(readonly=True)
    value = fields.Float(compute="_compute_value")
    kpi_type = fields.Selection(
        [
            ("python", "Python"),
            ("local", "SQL - Local DB"),
        ],
        string="KPI Computation Type",
        default="python",
    )
    kpi_code = fields.Text(
        help="SQL code must return the result as 'value' (i.e. 'SELECT 5 AS value').",
    )
    history_ids = fields.One2many("mgmtsystem.kpi.history", "kpi_id", string="History")
    active = fields.Boolean(
        default=True,
        help="Only active KPIs will be updated by the scheduler based on "
        "the periodicity configuration.",
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )

    @api.depends("history_ids", "history_ids.value", "history_ids.date")
    def _compute_value(self):
        for kpi in self:
            last_history = kpi.history_ids.sorted("date", reverse=True)[:1]
            kpi.value = last_history.value if last_history else 0.0

    def _compute_kpi_value(self):
        self.ensure_one()
        kpi_value = 0.0
        if (
            self.kpi_type == "local"
            and self.kpi_code
            and is_select_query(self.kpi_code)
        ):
            self.env.cr.execute(self.kpi_code)
            value = extract_value_from_rows(self.env.cr.dictfetchall())
            kpi_value = value or 0.0
        elif self.kpi_type == "python" and self.kpi_code:
            kpi_value = safe_eval(self.kpi_code)

        return kpi_value

    def compute_kpi_value(self):
        history_model = self.env["mgmtsystem.kpi.history"]
        for kpi in self:
            kpi_value = kpi._compute_kpi_value()
            history_model.create(
                {
                    "name": fields.Date.context_today(kpi).strftime("%d %B %Y"),
                    "kpi_id": kpi.id,
                    "value": kpi_value,
                    "color": kpi.threshold_id.get_color(kpi_value),
                }
            )
        return True

    def _get_next_execution_date(self):
        self.ensure_one()
        if self.periodicity_uom == "hour":
            delta = timedelta(hours=self.periodicity)
        elif self.periodicity_uom == "day":
            delta = timedelta(days=self.periodicity)
        elif self.periodicity_uom == "week":
            delta = timedelta(weeks=self.periodicity)
        elif self.periodicity_uom == "month":
            delta = relativedelta(months=self.periodicity)
        else:
            delta = timedelta()
        return fields.Datetime.now() + delta

    def update_next_execution_date(self):
        for kpi in self:
            kpi.next_execution_date = kpi._get_next_execution_date()
        return True

    @api.model
    def update_kpi_value(self):
        now = fields.Datetime.now()
        kpis = self.search(
            [
                ("active", "=", True),
                "|",
                ("next_execution_date", "<=", now),
                ("next_execution_date", "=", False),
            ]
        )
        if not kpis:
            return True
        try:
            kpis.compute_kpi_value()
            kpis.update_next_execution_date()
        except Exception:
            _logger.exception("Failed updating KPI values")
        return True
