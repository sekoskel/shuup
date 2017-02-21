# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from django import forms
from django.utils.translation import ugettext_lazy as _

from shuup.admin.forms import ShuupAdminForm

from .consts import EDI_OPERATORS
from .models import AndersManagerPaymentProcessor


class AndersManagerPaymentProcessorForm(ShuupAdminForm):
    class Meta:
        model = AndersManagerPaymentProcessor
        exclude = ["identifier"]


class AMEInvoiceForm(forms.Form):
    edi_code = forms.CharField(
        label=_("EDI/OVT-code"),
        max_length=64)
    select_operator = forms.ChoiceField(
        label=_("Select operator"),
        choices=EDI_OPERATORS, required=False)
    edi_operator = forms.CharField(
        label=_("Operator code"),
        max_length=64)
