
{
    'name': ' Stock Basic enhancement',
    'version': '1.0.1',
    'summary': """automatic implementation for warehouse and operation type""",
    'description': """internal transfer enhancement operation type automatic name and code,
      add automatic purchase returns , sales returns and link sales returns with sales delevery & link purchase returns with purschase reciept,
      odoo standard when create new warehouse and create automatic operation then all operations take the same names for all warehouses created like (recipts-delivery-internal transfers)
      but with our application we added warehouse name to all automatic operations created like (warehouse one purchase recipt ,warehouse one sale deliver,
      warehouse one internal transfers and we added 2 new operations for returns (warehouse one purchase returns - warehouse one sales returns),
      also when auto create the parent location"the first view location" standard odoo create this locaation for all warehouses created by the name 'Stock' but
      we rename this location by warehouse name like warehouse one -warehouse two ...and so on ,
      also we added automatic ability to automatic reset the sequences on the specified times(daily-weekly-monthly-yearly) for any sequences as a general feture 
      and we use it for all operations created automatic after adding our application with yearly reset option """,
    'category': 'Warehouse',
    'author': 'Zero Systems',
    'website': "https://www.erpzero.com",
    'depends': ['base','stock',],
    'data': [
        'views/view.xml',
    ],
    'license': 'AGPL-3',
    'images': ['static/description/logo.PNG'],
    'installable': True,
    'auto_install': False,
    'price': 65.0,
    'currency': 'USD',
    'application': False,
}
