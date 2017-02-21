# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from shuup import configuration
from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import ADDONS_MENU_CATEGORY
from shuup.admin.toolbar import DropdownActionButton, DropdownItem
from shuup.admin.utils.permissions import get_default_model_permissions
from shuup.admin.utils.urls import admin_url
from shuup.core.models import Order, OrderLogEntry
from shuup_anders_manager.configuration_keys import ENABLED_CONF_KEY, LOG_SENT, URL_CONF_KEY, AM_EXTRA_DATA_KEY
from shuup_anders_manager.models import AndersManagerPaymentProcessor


class AdminModule(AdminModule):
    name = _("Anders Manager")
    breadcrumbs_menu_entry = MenuEntry(text=name, url="shuup_admin:andersmanager.config")

    def get_urls(self):
        return [
            admin_url(
                "^andersmanager/$",
                "shuup_anders_manager.admin.views.ConfigurationView",
                name="andersmanager.config",
                permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
            ),
            admin_url(
                "^andersmanager/send/(?P<order_pk>\d+)/$",
                "shuup_anders_manager.admin.views.send_order",
                name="andersmanager.send",
                permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
            ),
            admin_url(
                "^andersmanager/download/(?P<order_pk>\d+)/$",
                "shuup_anders_manager.admin.views.download_order",
                name="andersmanager.download",
                permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
            ),
            admin_url(
                "^andersmanager/test_configuration/$",
                "shuup_anders_manager.admin.views.test_configurations",
                name="andersmanager.test_configurations",
                permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
            ),
            admin_url(
                "^andersmanager/einvoice/(?P<order_pk>\d+)$",
                "shuup_anders_manager.admin.views.update_e_invoice_data",
                name="shuup_anders_manager.update_e_invoice_data",
                permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
            )
        ]

    def get_menu_category_icons(self):
        return {self.name: "fa fa-paint-brush"}

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name, icon="fa fa-book",
                url="shuup_admin:andersmanager.config",
                category=ADDONS_MENU_CATEGORY
            )
        ]

    def get_required_permissions(self):
        return (
            get_default_model_permissions(AndersManagerPaymentProcessor) |
            get_default_model_permissions(Order)
        )


class ResendToolbarButton(DropdownActionButton):
    def __init__(self, order, **kwargs):
        kwargs["icon"] = "fa fa-wrench"
        kwargs["text"] = _("Anders Manager tools")
        kwargs["extra_css_class"] = "btn-info"
        kwargs["disable_reason"] = self._get_disable_reason()
        self.order = order
        super(ResendToolbarButton, self).__init__(self.get_menu_items(), **kwargs)

    def get_menu_items(self):
        return filter(None, [
            self._get_send_button(),
            self._get_download_button(),
            self._get_link_button(),
        ])

    def _get_disable_reason(self):
        is_am_enabled = bool(not configuration.get(None, ENABLED_CONF_KEY))
        return _("Anders Manager integration is disabled.") if is_am_enabled else None

    def _create_button(self, text=None, icon=None, url=None, disable_reason=None,
                       required_permissions=None, extra_css_class=None):
        """
        Creates a button with given parameters if AM integration is enabled. If the integration is disabled,
        disable some of the button's features.
        """
        disable_reason = self._get_disable_reason() or disable_reason

        if disable_reason:
            url = "#"

        return DropdownItem(
            text=text,
            icon=icon,
            url=url,
            disable_reason=disable_reason,
            required_permissions=required_permissions,
            extra_css_class=extra_css_class
        )

    def _get_send_button(self):
        text = _("Send to Anders Manager")

        disable_reason = None
        icon = "fa fa-mail-forward"
        is_sent = OrderLogEntry.objects.filter(target=self.order, identifier=LOG_SENT).exists()
        if is_sent:
            text = _("Sent to Anders Manager")
            disable_reason = text
            icon = "fa fa-check"

        return self._create_button(
            text=text,
            icon=icon,
            url=reverse("shuup_admin:andersmanager.send", kwargs={"order_pk": self.order.pk}),
            disable_reason=disable_reason,
            required_permissions=get_default_model_permissions(AndersManagerPaymentProcessor),
        )

    def _get_link_button(self):
        is_sent = OrderLogEntry.objects.filter(target=self.order, identifier=LOG_SENT).exists()
        am_order_id = self.order.extra_data.get(AM_EXTRA_DATA_KEY)
        if not (is_sent and am_order_id):
            return None

        url = "%s/cake/tilaukset/nayta/%s" % (
            configuration.get(None, URL_CONF_KEY),
            am_order_id,
        )

        return self._create_button(
            text=_("View order in Anders Manager"),
            icon="fa fa-external-link",
            url=url,
            required_permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
        )

    def _get_download_button(self):
        return self._create_button(
            text=_("Download order XML"),
            icon="fa fa-download",
            url=reverse("shuup_admin:andersmanager.download", kwargs={"order_pk": self.order.pk}),
            required_permissions=get_default_model_permissions(AndersManagerPaymentProcessor)
        )
