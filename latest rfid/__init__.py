# -*- coding: utf-8 -*-
from . import models


def post_init_hook(env):
    """
    Post-installation hook to set all products to sequential RFID mode.

    This ensures:
    - All existing products use sequential serials
    - Consistent configuration across all products
    - Production tracking from day one

    Aurora Tech Group LTD
    """
    import logging
    _logger = logging.getLogger(__name__)

    try:
        # Get all products
        products = env['product.product'].search([])

        if not products:
            _logger.info("[RFID] No products found to update")
            return

        # Set sequential mode for all products
        products.write({
            'use_sequential_rfid': True,
            'last_rfid_serial': 0,
        })

        _logger.info(f"[RFID] ✓ Set {len(products)} products to sequential RFID mode")
        _logger.info(f"[RFID] ✓ All future products will use sequential mode by default")

    except Exception as e:
        _logger.error(f"[RFID] Error in post_init_hook: {e}")