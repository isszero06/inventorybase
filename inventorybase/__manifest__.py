# -*- coding: utf-8 -*-
#################################################################################
# Author      : Zero For Information Systems (<www.erpzero.com>)
# Copyright(c): 2016-Zero For Information Systems
# All Rights Reserved.
#zerosystems #erp #odoo
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': ' Stock Basic enhancement',
    'version': '13.0.2',
    'summary': """Auto Genration for Sales Returns and Purchase Returns operations, 
                Link them with Sales delivery,
                 Purchase Recipt and other Enhancment""",
    'description': """
                internal transfer enhancement operation type automatic name and code, add automatic purchase returns ,

                sales returns and link sales returns with sales delivery & link purchase returns with purchase receipt,

                odoo standard when create new warehouse and create automatic operation then all operations take the same names for all warehouses created like (receipts-delivery-internal transfers) but with our application we added warehouse name to all automatic operations created like (warehouse one purchase receipt ,

                warehouse one sale deliver, warehouse one internal transfers and we added 2 new operations for returns (warehouse one purchase returns - warehouse one sales returns),

                also when auto create the parent location "the first view location" standard odoo create this location for all warehouses created by the name 'Stock' but we rename this location by warehouse name like warehouse one -warehouse two ...and so on ,

                also we added automatic ability to automatic reset the sequences on the specified times(daily-weekly-monthly-yearly) for any sequences as a general features and we use it for all operations created automatic after adding our application with yearly reset option
                 """,
    'category': 'Warehouse',
    'author': 'Zero Systems',
    'website': "https://www.erpzero.com",
    'depends': ['base','stock',],
    'data': [
        'views/view.xml',
    ],
    'license': 'OPL-1',
    'live_test_url': 'https://www.youtube.com/watch?v=1S9B4HsxtEw',
    'images': ['static/description/logo.PNG'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 0.0,
    'currency': 'USD',
}
