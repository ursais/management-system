# Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemKpiHistory(models.Model):
    _name = "mgmtsystem.kpi.history"
    _description = "History of the KPI"
    _order = "date desc"

    name = fields.Char(required=True)
    kpi_id = fields.Many2one("mgmtsystem.kpi", required=True, ondelete="cascade")
    date = fields.Datetime(required=True, readonly=True, default=fields.Datetime.now)
    value = fields.Float(required=True, readonly=True)
    color = fields.Char(required=True, readonly=True, default="#FFFFFF")
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )
