# Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Key Performance Indicator",
    "version": "19.0.1.0.0",
    "author": "Savoir-faire Linux, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/management-system",
    "license": "AGPL-3",
    "category": "Management System",
    "depends": ["mgmtsystem"],
    "data": [
        "security/ir.model.access.csv",
        "security/mgmtsystem_kpi_security.xml",
        "data/ir_cron.xml",
        "views/mgmtsystem_kpi_category.xml",
        "views/mgmtsystem_kpi_threshold_range.xml",
        "views/mgmtsystem_kpi_threshold.xml",
        "views/mgmtsystem_kpi.xml",
        "views/menus.xml",
    ],
    "installable": True,
}
