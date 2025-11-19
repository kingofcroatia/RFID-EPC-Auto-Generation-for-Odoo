# -*- coding: utf-8 -*-
# Copyright 2025 Aurora Tech Group LTD, London, UK
# Developer: Andrew
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import random
import logging

_logger = logging.getLogger(__name__)

try:
    from pyepc import SGTIN
    PYEPC_AVAILABLE = True
except ImportError:
    PYEPC_AVAILABLE = False
    _logger.warning("pyepc library not found. Install with: pip install pyepc")


class ProductProduct(models.Model):
    """
    RFID EPC Generation with Sequential Serial Numbers

    Features:
    - Automatic SGTIN-96 EPC code generation
    - Sequential serial numbers per product (default)
    - Random serial numbers (optional)
    - Auto-generates barcodes if missing
    - Thread-safe counters
    - Per-product tracking
    - Reset counter functionality

    Aurora Tech Group LTD, London, UK
    Developer: Andrew
    """
    _inherit = 'product.product'

    last_rfid_serial = fields.Integer(
        string='Last RFID Serial',
        default=0,
        help='Last used serial number for RFID tags.\n'
             'Increments automatically with each label print.\n'
             'Shows total labels printed for this product.',
        copy=False,
        index=True
    )

    use_sequential_rfid = fields.Boolean(
        string='Use Sequential RFID Serials',
        default=True,
        help='Use sequential serial numbers (1, 2, 3, 4...) per product.\n\n'
             'Benefits:\n'
             '• Track total production count\n'
             '• Predictable numbering\n'
             '• Easy debugging\n'
             '• Perfect for inventory tracking\n\n'
             'Uncheck to use random serials for high-security items.'
    )

    auto_generated_barcode = fields.Boolean(
        string='Auto-Generated Barcode',
        default=False,
        help='True if barcode was automatically generated from product ID.\n'
             'Format: 999 + Product ID (internal use only)',
        copy=False
    )

    def _generate_internal_barcode(self):
        """
        Generate internal barcode from product ID.

        For internal use - doesn't follow strict GS1 standards.
        Format: 999 (internal prefix) + Product ID (padded to 10 digits)

        Example:
            Product ID 145 → 9990000000145 (13 digits)

        Returns:
            str: 13-digit internal barcode
        """
        try:
            # Use prefix 999 (reserved for internal use)
            prefix = "999"

            # Pad product ID to 10 digits
            product_id_str = str(self.id).zfill(10)

            # Create 13-digit barcode
            barcode = prefix + product_id_str

            _logger.info(
                f"[RFID] Auto-generated barcode {barcode} "
                f"for product '{self.name}' (ID: {self.id})"
            )

            return barcode

        except Exception as e:
            _logger.error(f"[RFID] Error generating barcode: {e}")
            raise UserError(
                f"Failed to generate barcode for '{self.name}'.\n\n"
                f"Error: {str(e)}\n\n"
                f"Contact: info@auroratechgroup.co.uk"
            )

    def _ensure_barcode(self):
        """
        Ensure product has a barcode.

        If no barcode exists:
        1. Auto-generates internal barcode from product ID
        2. Saves to product permanently
        3. Marks as auto-generated

        Returns:
            str: Product barcode (existing or newly generated)
        """
        if self.barcode:
            return self.barcode

        _logger.info(
            f"[RFID] Product '{self.name}' has no barcode, auto-generating..."
        )

        # Generate internal barcode
        new_barcode = self._generate_internal_barcode()

        # Save to product
        self.write({
            'barcode': new_barcode,
            'auto_generated_barcode': True,
        })

        return new_barcode

    def generate_sgtin96_epc(self, barcode=None, serial=None):
        """
        Generate SGTIN-96 EPC code for RFID encoding.

        Process:
        1. Ensure barcode exists (auto-generate if missing)
        2. Generate serial number (sequential or random)
        3. Create SGTIN-96 EPC code
        4. Return 24-character hexadecimal EPC

        Features:
        - Sequential serials (default): 1, 2, 3, 4...
        - Random serials (optional): High security
        - Thread-safe: Multiple users can print simultaneously
        - Per-product counters: Each product independent

        Args:
            barcode (str, optional): Product barcode. Auto-generates if missing.
            serial (int, optional): Serial number (1-274B). Auto-generates if missing.

        Returns:
            str: 24-character hexadecimal EPC code (SGTIN-96)

        Example:
            Product: Medical Implant ABC

            First print:  Serial 1 → EPC: 30344B32641D29770000001
            Second print: Serial 2 → EPC: 30344B32641D29770000002
            Third print:  Serial 3 → EPC: 30344B32641D29770000003

            Counter shows: 3 (total labels printed)

        GS1 Standard:
            SGTIN-96 (96-bit EPC Tag Data Standard v1.9)

            Structure:
            - Header: 8 bits (0x30)
            - Filter: 3 bits (1 = POS)
            - Partition: 3 bits (5 = 7-digit prefix)
            - Company Prefix: 24 bits (7 digits)
            - Item Reference: 20 bits (5 digits)
            - Serial Number: 38 bits (1 to 274,877,906,943)

        Aurora Tech Group LTD | info@auroratechgroup.co.uk
        """
        if not PYEPC_AVAILABLE:
            _logger.error("[RFID] pyepc library not available")
            raise UserError(
                "RFID module error: pyepc library not installed.\n\n"
                "Install with:\n"
                "pip install pyepc --break-system-packages\n\n"
                "Contact Aurora Tech Group:\n"
                "Email: info@auroratechgroup.co.uk"
            )

        # ========== STEP 1: ENSURE BARCODE EXISTS ==========
        if not barcode:
            barcode = self._ensure_barcode()

        try:
            barcode_str = str(barcode).strip()

            # Normalize barcode to 14 digits (GTIN-14 format)
            if len(barcode_str) == 13:
                barcode_str = "0" + barcode_str  # EAN-13 → GTIN-14
            elif len(barcode_str) == 12:
                barcode_str = "00" + barcode_str  # UPC-A → GTIN-14
            elif len(barcode_str) < 12:
                barcode_str = barcode_str.zfill(14)

            if len(barcode_str) != 14:
                _logger.error(
                    f"[RFID] Invalid barcode length: {len(barcode_str)} "
                    f"for product '{self.name}'"
                )
                raise UserError(
                    f"Invalid barcode for '{self.name}'.\n\n"
                    f"Barcode: {barcode}\n"
                    f"Expected: 12-14 digits\n"
                    f"Got: {len(barcode_str)} digits"
                )

            # Split barcode into SGTIN components
            barcode_no_check = barcode_str[:-1]  # Remove check digit (13 digits)
            indicator = barcode_no_check[0]       # 1 digit: Packaging indicator
            company_prefix = barcode_no_check[1:8]  # 7 digits: GS1 Company Prefix
            item_ref = barcode_no_check[8:]         # 5 digits: Item Reference

            # ========== STEP 2: GENERATE SERIAL NUMBER ==========
            generated_serial = serial

            if not generated_serial:
                if self.use_sequential_rfid:
                    # ========== SEQUENTIAL MODE (DEFAULT) ==========
                    # Atomic SQL increment - thread-safe
                    # Multiple users can print simultaneously without conflicts
                    # Each product has its own independent counter

                    self.env.cr.execute("""
                        UPDATE product_product
                        SET last_rfid_serial = last_rfid_serial + 1
                        WHERE id = %s
                        RETURNING last_rfid_serial
                    """, (self.id,))

                    result = self.env.cr.fetchone()
                    generated_serial = result[0] if result else 1

                    _logger.info(
                        f"[RFID Sequential] Product '{self.name}' (ID: {self.id}) "
                        f"- Generated serial: {generated_serial}"
                    )
                else:
                    # ========== RANDOM MODE ==========
                    # High security mode
                    # Range: 1 to 274,877,906,943 (2^38 - 1)
                    # Collision probability: 0.00164% for 3,000 labels

                    generated_serial = random.randint(1, 274877906943)

                    _logger.info(
                        f"[RFID Random] Product '{self.name}' (ID: {self.id}) "
                        f"- Generated serial: {generated_serial}"
                    )

            # ========== STEP 3: CREATE SGTIN-96 EPC ==========
            sgtin = SGTIN(
                company_prefix=company_prefix,
                indicator=indicator,
                item_ref=item_ref
            )

            sgtin.filter_value = 1  # Filter 1 = Point of Sale Trade Item
            sgtin.serial_number = str(generated_serial)

            # Encode to 96-bit hexadecimal (24 characters)
            epc_hex = sgtin.encode()

            _logger.info(
                f"[RFID] ✓ Generated EPC: {epc_hex} "
                f"for '{self.name}' "
                f"(barcode: {barcode_str}, serial: {generated_serial})"
            )

            return epc_hex

        except UserError:
            raise
        except Exception as e:
            _logger.error(f"[RFID] Error generating EPC: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            raise UserError(
                f"Failed to generate RFID label for '{self.name}'.\n\n"
                f"Error: {str(e)}\n\n"
                f"Contact Aurora Tech Group:\n"
                f"Email: info@auroratechgroup.co.uk"
            )

    def action_reset_rfid_counter(self):
        """
        Reset RFID serial counter to 0.

        Use cases:
        - Start new production batch
        - Reset after inventory count
        - Clear counter for testing

        Returns:
            dict: Notification action
        """
        self.ensure_one()

        old_value = self.last_rfid_serial
        self.last_rfid_serial = 0

        _logger.info(
            f"[RFID] Counter reset from {old_value} to 0 "
            f"for product '{self.name}' (ID: {self.id})"
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'RFID counter reset from {old_value} to 0 for {self.name}',
                'type': 'success',
                'sticky': False,
            }
        }


class ProductTemplate(models.Model):
    """
    Extends product.template with RFID fields.

    Delegates to product.product variants for actual functionality.
    """
    _inherit = 'product.template'

    last_rfid_serial = fields.Integer(
        related='product_variant_ids.last_rfid_serial',
        string='Last RFID Serial',
        readonly=True,
        help='Total RFID labels printed for this product'
    )

    use_sequential_rfid = fields.Boolean(
        related='product_variant_ids.use_sequential_rfid',
        string='Use Sequential RFID Serials',
        readonly=False,
        help='Use sequential serial numbers (1, 2, 3...) instead of random'
    )

    auto_generated_barcode = fields.Boolean(
        related='product_variant_ids.auto_generated_barcode',
        string='Auto-Generated Barcode',
        readonly=True,
        help='Barcode was automatically generated (internal use)'
    )

    def generate_sgtin96_epc(self, barcode=None, serial=None):
        """
        Generate EPC for product template.

        Wrapper that delegates to first product variant.

        Args:
            barcode (str, optional): Product barcode
            serial (int, optional): Serial number

        Returns:
            str: 24-character hexadecimal EPC code
        """
        if self.product_variant_ids:
            return self.product_variant_ids[0].generate_sgtin96_epc(barcode, serial)

        raise UserError(
            f"Cannot generate RFID label for '{self.name}'.\n\n"
            f"No product variants found."
        )

    def action_reset_rfid_counter(self):
        """
        Reset RFID counter for template.

        Delegates to first product variant.
        """
        if self.product_variant_ids:
            return self.product_variant_ids[0].action_reset_rfid_counter()

        raise UserError(
            f"Cannot reset counter for '{self.name}'.\n\n"
            f"No product variants found."
        )