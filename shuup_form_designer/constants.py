# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

# Configuration keys
ENABLED_CONF_KEY = "andersmanager:enabled"
URL_CONF_KEY = "andersmanager:url"
SECRET_CONF_KEY = "andersmanager:secret"

# Signal dispatch uid
ORDER_SIGNAL_DISPATCH_UID = "shuup_anders_manager.order_received"
PAYMENT_SIGNAL_DISPATCH_UID = "shuup_anders_manager.payment_received"
REFUND_SIGNAL_DISPATCH_UID = "shuup_anders_manager.refund_received"

# Log identifiers
INVALID_XML_RESPONSE = "anders_manager_invalid_xml"
LOG_SENT = "anders_manager_sent"
LOG_NOT_SENT = "anders_manager_not_sent"
EINVOICE_DATA_UPDATED = "anders_manager_e_invoice_data_updated"

LOG_IDENTIFIERS = [
    INVALID_XML_RESPONSE,
    LOG_SENT,
    LOG_NOT_SENT,
    EINVOICE_DATA_UPDATED
]

# Order extra data
AM_EXTRA_DATA_KEY = "am_order_id"

# For electronic invoice data
EINVOICE_DATA_KEY = "am_e_invoice_data"
