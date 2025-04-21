# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Picking Product Weight Information",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Warehouse",
    "license": "OPL-1",
    "summary": " Product Weight in Delivery Orders Product Weight in Delivery Report Product Weight in Picking Odoo App Add Product Weight on Delivery Order Weight Product weight Picking Weight Product Weight on Picking Stock Product Moves Weight Delivery Product Total Weight Demanded Product Total Weight All Product Total Weight Picking Product Weight Information Delivery Product Weight Information Delivery Order Weight Module Picking Order Total Order Weight Picking Order Calculate Weight Picking Weight Count Product Weight In Delivery Picking Product Weight Odoo Picking Weight In Report Delivery Order Product Weight Calculation Picking Order Weight kg kg(s) support Picking Weight Information Picking Product Weight Detail Odoo",
    "description": """ This module allows you to see the weights of products in Delivery orders. It displays the total weight of all products and includes this information in printed reports.  """,
    "depends": [
        'stock', 'sale_management',
    ],
    "data": [
        "security/sh_weight_sequrity.xml",
        "views/stock_picking_views.xml",
        "views/report_deliveryslip_inherit.xml",
    ],
    "version": "0.0.1",
    "auto_install": False,
    "installable": True,
    "application": True,
    'images': ['static/description/background.png', ],
    "price": 9.98 ,
    "currency": "EUR"
}

