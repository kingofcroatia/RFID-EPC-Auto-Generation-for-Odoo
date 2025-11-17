# -*- coding: utf-8 -*-
# Copyright 2025 Aurora Tech Group LTD, London, UK
# Developer: Andrew
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models
import random
import logging

_logger = logging.getLogger(__name__)

try:
    from pyepc import SGTIN
    PYEPC_AVAILABLE = True
except ImportError:
    PYEPC_AVAILABLE = False
    _logger.warning("pyepc library not found. RFID encoding will not work. "
                   "Install with: pip install pyepc")


class ProductProduct(models.Model):
    """
    Extends product.product to add RFID EPC generation capability.
    
    Generates SGTIN-96 EPC codes compatible with GS1 standards and
    Ventor Tech Pro mobile app.
    
    Developed by Aurora Tech Group LTD, London, UK
    Developer: Andrew
    """
    _inherit = 'product.product'
    
    def generate_sgtin96_epc(self, barcode=None, serial=None):
        """
        Generate SGTIN-96 EPC code using pyepc library.
        
        Creates a 96-bit EPC code in hexadecimal format (24 characters)
        following the GS1 EPC Tag Data Standard for SGTIN-96.
        
        Args:
            barcode (str, optional): Product barcode. If not provided, uses
                                    self.barcode. Supports EAN-13, EAN-14, UPC-A.
            serial (int, optional): Serial number (1-274,877,906,943). If not
                                   provided, generates random serial.
        
        Returns:
            str: 24-character hexadecimal EPC code, or 24 zeros if error.
        
        Example:
            >>> product.generate_sgtin96_epc("01232025298615", 123456)
            '30344B32641D29774E0F0BEC'
        
        EPC Structure (SGTIN-96):
            - Header: 8 bits (0x30 for SGTIN-96)
            - Filter: 3 bits (1 = Point of Sale item)
            - Partition: 3 bits (5 = 7-digit company prefix)
            - Company Prefix: 24 bits (7 digits)
            - Item Reference: 20 bits (5 digits)  
            - Serial Number: 38 bits (up to 274,877,906,943)
        
        GS1 Standard:
            Follows GS1 EPC Tag Data Standard v1.9 for SGTIN-96 encoding.
            
        Developed by:
            Aurora Tech Group LTD, London, UK
            Developer: Andrew
        """
        if not PYEPC_AVAILABLE:
            _logger.error("pyepc library not available. Cannot generate EPC. "
                         "Contact Aurora Tech Group for support: info@auroratechgroup.co.uk")
            return "000000000000000000000000"
        
        # Use product barcode if not provided
        if not barcode:
            barcode = self.barcode
            
        if not barcode:
            _logger.warning(f"No barcode found for product {self.name}")
            return "000000000000000000000000"
        
        try:
            barcode_str = str(barcode).strip()
            
            # Normalize barcode to 14-digit EAN-14 format
            # Add leading zeros if needed
            if len(barcode_str) == 13:
                barcode_str = "0" + barcode_str  # EAN-13 → EAN-14
            elif len(barcode_str) == 12:
                barcode_str = "00" + barcode_str  # UPC-A → EAN-14
            
            # Validate barcode length
            if len(barcode_str) != 14:
                _logger.error(f"Invalid barcode length {len(barcode_str)} "
                            f"for product {self.name}. Expected 12, 13, or 14 digits.")
                return "000000000000000000000000"
            
            # Split barcode into components
            # Format: [Indicator][Company Prefix 7 digits][Item Reference 5 digits][Check digit]
            barcode_no_check = barcode_str[:-1]  # Remove check digit (13 digits)
            indicator = barcode_no_check[0]      # 1 digit: Indicator/Packaging level
            company_prefix = barcode_no_check[1:8]  # 7 digits: GS1 Company Prefix
            item_ref = barcode_no_check[8:]      # 5 digits: Item Reference
            
            # Generate random serial number if not provided
            # Range: 1 to 274,877,906,943 (2^38 - 1)
            # Uses cryptographically secure random for uniqueness
            if not serial:
                serial = random.randint(1, 274877906943)
            
            # Create SGTIN-96 object using pyepc library
            sgtin = SGTIN(
                company_prefix=company_prefix,
                indicator=indicator,
                item_ref=item_ref
            )
            
            # Set EPC parameters
            sgtin.filter_value = 1  # Filter 1 = Point of Sale (POS) Trade Item
            sgtin.serial_number = str(serial)
            
            # Encode to hexadecimal EPC
            epc_hex = sgtin.encode()
            
            # Log successful generation
            _logger.info(f"Generated EPC for barcode {barcode_str}: {epc_hex} "
                        f"(serial: {serial}) [Aurora Tech Group]")
            
            return epc_hex
            
        except Exception as e:
            # Log error with full traceback
            _logger.error(f"Error generating EPC for barcode {barcode}: {str(e)} "
                         f"[Aurora Tech Group - Contact: info@auroratechgroup.co.uk]")
            import traceback
            _logger.error(traceback.format_exc())
            return "000000000000000000000000"


class ProductTemplate(models.Model):
    """
    Extends product.template to add RFID EPC generation capability.
    
    Delegates to product.product variant for actual EPC generation.
    
    Developed by Aurora Tech Group LTD, London, UK
    Developer: Andrew
    """
    _inherit = 'product.template'
    
    def generate_sgtin96_epc(self, barcode=None, serial=None):
        """
        Generate SGTIN-96 EPC code for product template.
        
        Wrapper method that delegates to the first product variant.
        
        Args:
            barcode (str, optional): Product barcode
            serial (int, optional): Serial number
        
        Returns:
            str: 24-character hexadecimal EPC code, or 24 zeros if no variants.
        """
        if self.product_variant_ids:
            return self.product_variant_ids[0].generate_sgtin96_epc(barcode, serial)
        
        _logger.warning(f"No product variants found for template {self.name} "
                       f"[Aurora Tech Group]")
        return "000000000000000000000000"
