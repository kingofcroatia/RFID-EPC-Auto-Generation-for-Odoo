from odoo import models
import random
import logging

_logger = logging.getLogger(__name__)

try:
    from pyepc import SGTIN
    PYEPC_AVAILABLE = True
except ImportError:
    PYEPC_AVAILABLE = False
    _logger.warning("pyepc library not found")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def generate_sgtin96_epc(self, barcode=None, serial=None):
        """Generate SGTIN-96 EPC using pyepc library - Ventor compatible"""
        if not PYEPC_AVAILABLE:
            _logger.error("pyepc library not available")
            return "000000000000000000000000"

        if not barcode:
            barcode = self.barcode

        if not barcode:
            _logger.warning(f"No barcode for product {self.name}")
            return "000000000000000000000000"

        try:
            barcode_str = str(barcode).strip()

            # Ensure 14-digit format (add leading 0 if 13 digits)
            if len(barcode_str) == 13:
                barcode_str = "0" + barcode_str
            elif len(barcode_str) == 12:
                barcode_str = "00" + barcode_str

            if len(barcode_str) != 14:
                _logger.error(f"Invalid barcode length: {len(barcode_str)}")
                return "000000000000000000000000"

            # Remove check digit and split
            barcode_no_check = barcode_str[:-1]  # 13 digits
            company_prefix = barcode_no_check[1:8]  # 7 digits
            item_ref = barcode_no_check[8:]  # 5 digits
            indicator = barcode_no_check[0]  # 1 digit

            # Generate random serial if not provided
            if not serial:
                serial = random.randint(1, 274877906943)

            # Create SGTIN-96
            sgtin = SGTIN(
                company_prefix=company_prefix,
                indicator=indicator,
                item_ref=item_ref
            )
            sgtin.filter_value = 1
            sgtin.serial_number = str(serial)

            epc_hex = sgtin.encode()

            _logger.info(f"EPC for {barcode_str}: {epc_hex} (serial: {serial})")

            return epc_hex

        except Exception as e:
            _logger.error(f"Error generating EPC for {barcode}: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return "000000000000000000000000"


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def generate_sgtin96_epc(self, barcode=None, serial=None):
        """Wrapper for product.template"""
        if self.product_variant_ids:
            return self.product_variant_ids[0].generate_sgtin96_epc(barcode, serial)
        return "000000000000000000000000"