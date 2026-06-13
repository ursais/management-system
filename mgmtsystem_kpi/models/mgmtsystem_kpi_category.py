# Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemKpiCategory(models.Model):
    _name = "mgmtsystem.kpi.category"
    _description = "KPI Category"

    name = fields.Char(required=True)
    description = fields.Text()
