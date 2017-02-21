# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.validators import ValidationError
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.views.generic.edit import FormView

from shuup import configuration
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.urls import derive_model_url
from shuup.core.models import Order, OrderLogEntry
from shuup.utils.analog import LogEntryKind
from shuup_form_designer.constants import (
    EINVOICE_DATA_KEY, EINVOICE_DATA_UPDATED, ENABLED_CONF_KEY,
    LOG_IDENTIFIERS, SECRET_CONF_KEY, URL_CONF_KEY
)
from shuup_form_designer.admin.forms import AMEInvoiceForm


class ConfigurationForm(forms.Form):
    is_enabled = forms.BooleanField(label=_("Enabled"), required=False)
    url = forms.CharField(label=_("Anders Manager URL"), max_length=120)
    secret = forms.CharField(label=_("Integration secret"), max_length=160)

    def clean_url(self):
        url = self.cleaned_data["url"]
        if not (url.startswith("https://") or settings.DEBUG):
            raise ValidationError(_("Only URLs with HTTPS is allowed"), code="no-https")

        return url


class ConfigurationView(FormView):
    template_name = "shuup_anders_manager/admin/config.jinja"
    form_class = ConfigurationForm

    def get_initial(self):
        initial = super(ConfigurationView, self).get_initial()
        initial.update({
            "is_enabled": bool(configuration.get(None, ENABLED_CONF_KEY)),
            "url": configuration.get(None, URL_CONF_KEY),
            "secret": configuration.get(None, SECRET_CONF_KEY)
        })
        return initial

    def form_valid(self, form):
        configuration.set(None, ENABLED_CONF_KEY, form.cleaned_data["is_enabled"])
        configuration.set(None, URL_CONF_KEY, form.cleaned_data["url"])
        configuration.set(None, SECRET_CONF_KEY, form.cleaned_data["secret"])
        messages.success(self.request, _("Configuration keys saved"))
        return HttpResponseRedirect(self.request.path)

    def get_context_data(self, **kwargs):
        context = super(ConfigurationView, self).get_context_data(**kwargs)
        context["toolbar"] = get_default_edit_toolbar(self, "am_config_form", with_split_save=False)
        context["log_entries"] = OrderLogEntry.objects.filter(
            identifier__in=LOG_IDENTIFIERS
        ).order_by("-created_on")[:50]
        return context


def update_e_invoice_data(request, order_pk):
    if request.method != "POST":
        raise Exception(_("Not allowed"))

    form = AMEInvoiceForm(request.POST)
    if form.is_valid():
        order = Order.objects.get(pk=order_pk)
        data = form.cleaned_data
        data.pop("select_operator")
        order.payment_data.update({EINVOICE_DATA_KEY: data})
        order.save(update_fields=["payment_data"])
        success_message = ugettext("New EDI address set (%(address)s) for order %(order_id)s") % {
            "address": "%s@%s" % (data.get("edi_code"), data.get("edi_operator")),
            "order_id": order.pk
        }
        messages.success(request, success_message)
        order.add_log_entry(
            success_message,
            identifier=EINVOICE_DATA_UPDATED,
            kind=LogEntryKind.EDIT
        )
        return JsonResponse({"message": success_message}, status=200)
    error_message = ugettext("Error, please check submitted values and try again.")
    return JsonResponse({"message": error_message}, status=400)
