# -*- coding: utf-8 -*-
# Copyright 2025 Aurora Tech Group LTD, London, UK
# Developer: Andrew
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'RFID EPC Auto Generation',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Automatically generate SGTIN-96 EPC codes for RFID labels',
    'description': """
RFID EPC Auto Generation
========================

Automatically generate GS1-compliant SGTIN-96 EPC codes during label printing.

Developed by Aurora Tech Group LTD, London, UK.

Features:
---------
* Automatic EPC generation for product labels
* Compatible with Ventor Tech Pro mobile app
* Supports high-volume RFID label production
* GS1 EPC Tag Data Standard compliant
* Works with Zebra RFID printers (ZT231R, ZT411R)
* Unique serial number generation for each label
* Zero configuration required
* Universal barcode support (EAN-13, EAN-14, UPC-A)

Use Case:
---------
Eliminate manual RFID tag writing for thousands of products. Print RFID-encoded 
labels directly from Odoo with automatic EPC generation.

Saves 70%+ time compared to manual RFID writing process.

Requirements:
-------------
* Python library: pyepc (install with: pip install pyepc)
* Zebra RFID printer (ZT231R, ZT411R, or similar)
* RFID labels compatible with your printer
* Odoo 18.0+

Technical:
----------
* Implements SGTIN-96 encoding (96-bit EPC)
* Random serial number generation (1 to 274,877,906,943)
* 7-digit company prefix support
* Filter value: 1 (Point of Sale item)
* Partition: 5 (GS1 standard for 7-digit prefix)

Enterprise Support:
------------------
Aurora Tech Group offers professional support, custom development, and 
integration services for this module.

Contact: info@auroratechgroup.co.uk
Website: https://auroratechgroup.co.uk
GitHub: https://github.com/kingofcroatia/rfid_epc_auto

For more information:
---------------------
* Documentation: https://github.com/kingofcroatia/rfid_epc_auto
* Issues: https://github.com/kingofcroatia/rfid_epc_auto/issues
* GS1 Standard: https://www.gs1.org/standards/epc-rfid/tds
    """,
    'author': 'Aurora Tech Group LTD',
    'website': 'https://auroratechgroup.co.uk',
    'maintainer': 'Aurora Tech Group LTD',
    'license': 'LGPL-3',
    'support': 'info@auroratechgroup.co.uk',
    
    'depends': [
        'stock',
    ],
    'external_dependencies': {
        'python': ['pyepc'],
    },
    'data': [
        'views/product_label_rfid.xml',
    ],
    'demo': [],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.00,
    'currency': 'EUR',
}
