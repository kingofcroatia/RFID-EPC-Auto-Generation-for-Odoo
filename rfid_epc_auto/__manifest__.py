{
    'name': 'RFID EPC Auto Generation',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Automatically generate SGTIN-96 EPC codes for RFID labels',
    'description': """
        Generates EPC codes compatible with Ventor Tech Pro app.
        Uses pyepc library for SGTIN-96 encoding.
    """,
    'depends': ['stock'],
    'external_dependencies': {
        'python': ['pyepc'],
    },
    'data': [
        'views/product_label_rfid.xml',
    ],
    'installable': True,
    'application': False,
}
