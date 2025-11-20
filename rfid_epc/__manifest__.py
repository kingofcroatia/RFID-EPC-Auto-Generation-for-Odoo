# -*- coding: utf-8 -*-
{
    "name": "RFID EPC Auto Generation",
    "version": "18.0.2.0.0",
    "category": "Inventory/Inventory",
    "summary": "Automatic SGTIN-96 EPC generation for RFID labels with sequential serials",
    "description": """
RFID EPC Auto Generation
========================

Professional RFID solution for Odoo with sequential serial number tracking.

Features:
---------
* Automatic SGTIN-96 EPC code generation (GS1 standard)
* Sequential serial numbers per product (default)
* Random serial numbers (optional for high-security items)
* Auto-generates internal barcodes if missing
* Thread-safe counters (multi-user support)
* Per-product serial tracking
* Reset counter functionality
* ZPL label templates with RFID encoding
* Compatible with Zebra RFID printers (ZT231R, ZT411R, etc.)
* Integration with Ventor Tech Pro mobile app

Sequential Serials:
-------------------
* Each product gets its own counter: 1, 2, 3, 4...
* Perfect for production tracking
* Know exactly how many labels printed
* Never resets (permanent tracking)
* Thread-safe atomic increments

Auto-Barcode Generation:
------------------------
* Products without barcodes get one automatically
* Format: 999 + Product ID (internal use)
* Saved permanently to product
* Works seamlessly with EPC generation

Technical:
----------
* Uses pyepc library for GS1 EPC encoding
* SGTIN-96 format (96-bit EPC tags)
* Serial range: 1 to 274,877,906,943
* Atomic SQL increments for thread safety
* ZPL commands for RFID encoding (^RFW)

Perfect for:
------------
* Medical device tracking
* Inventory management
* Asset tracking
* Production counting
* Quality control
* Recall capability
* Warehouse operations

Developed by:
-------------
Aurora Tech Group LTD
London, United Kingdom
Email: info@auroratechgroup.co.uk
Web: https://auroratechgroup.co.uk

Developer: Andrew
License: LGPL-3
    """,
    "author": "Aurora Tech Group LTD",
    "website": "https://auroratechgroup.co.uk",
    "license": "LGPL-3",
    "support": "info@auroratechgroup.co.uk",

    "depends": [
        "stock",
        "product",
    ],

    "external_dependencies": {
        "python": ["pyepc"],
    },

    "data": [
        "views/product_label_rfid.xml",
        "views/product_view.xml",
    ],

    "images": [
        "static/description/icon.png",
        "static/description/banner.png",
    ],

    "installable": True,
    "application": False,
    "auto_install": False,

    # Apply sequential mode to all products on installation
    "post_init_hook": "post_init_hook",
}